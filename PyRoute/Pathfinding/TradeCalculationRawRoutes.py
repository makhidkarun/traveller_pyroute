# cython: profile=True
"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
import time
import numpy as np

try:
    from line_profiler import profile
except ImportError:
    def profile(func) -> object:
        return func

from PyRoute import Star
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.TradeCodes import TradeCodes


@cython.cclass
class TradeCalculationRawRoutes(object):
    trade: object
    _allies_dict: cython.dict
    algs: set
    btn_range: cython.list[cython.int]
    btn_max_range: cython.int
    btn_jump_range: cnp.ndarray[cython.int]
    btn_jump_mod: cnp.ndarray[cython.int]
    btn_jump_range_view: cython.int[:]
    btn_jump_mod_view: cython.int[:]
    btn_offset_by_dist: cnp.ndarray[cython.int]
    btn_offset_by_dist_view: cython.int[:]
    max_range: cython.int
    min_wtn: cython.int
    pairs_primed: cython.long
    pairs_considered: cython.long
    pairs_kept: cython.long

    def __init__(self, trade):
        from PyRoute.Calculation.TradeCalculation import TradeCalculation
        if not isinstance(trade, TradeCalculation):
            raise ValueError("Trade must be instance of TradeCalculation or subclass")
        self.trade = trade
        self._allies_dict: dict = {}
        self.algs = set()
        self.btn_range = trade.btn_range
        self.btn_max_range = max(self.btn_range)
        self.btn_jump_range = np.array(trade.btn_jump_range, dtype=np.int32)
        self.btn_jump_range_view = self.btn_jump_range
        self.btn_jump_mod = np.array(trade.btn_jump_mod, dtype=np.int32)
        self.btn_jump_mod_view = self.btn_jump_mod
        self.max_range = self.trade.galaxy.max_jump_range
        self.min_wtn = self.trade.min_wtn
        self.pairs_primed = 0
        self.pairs_considered = 0
        self.pairs_kept = 0
        self._seed_btn_offset_by_dist()

    @profile
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def raw_ranges(self) -> list[tuple[Star, Star]]:
        for s in self.trade.galaxy.ranges:
            self.algs.add(s.alg_code)

        for alg_code1 in self.algs:
            for alg_code2 in self.algs:
                self._allies_dict[str(alg_code1) + "/" + str(alg_code2)] = RouteCalculation.get_btn_allies(alg_code1, alg_code2)

        t0 = time.perf_counter()
        max_route_dist = max(self.trade.btn_range)
        max_range = self.trade.galaxy.max_jump_range
        min_btn = self.trade.min_btn
        min_wtn = self.trade.min_route_wtn
        offsets = TradeCalculationRawRoutes._axial_offsets_within(max_range)
        t1 = time.perf_counter()

        hiball = [item for item in self.trade.galaxy.ranges if item.wtn >= min_wtn and not item.is_redzone]
        loball = [item for item in self.trade.galaxy.ranges if item.wtn < min_wtn and not item.is_redzone]
        t2 = time.perf_counter()

        hi_hi_ranges = self._base_ranges(hiball, max_range, min_btn)
        t3 = time.perf_counter()
        t4 = time.perf_counter()
        lo_lo_ranges = self._lo_lo_ranges(loball, offsets)
        t5 = time.perf_counter()
        hi_lo_ranges = self._hi_lo_ranges(hiball, loball, offsets)
        t6 = time.perf_counter()
        hi_hi_ranges.extend(lo_lo_ranges)
        hi_hi_ranges.extend(hi_lo_ranges)
        self.trade.logger.info("Routes with endpoints more than " + str(max_route_dist) + " pc apart, trimmed")
        self.trade.logger.info(
            f"raw_ranges phases: init {t1 - t0:.6f}s, split {t2 - t1:.6f}s, ranges {t3 - t2:.6f}s, hi-hi filters {t4 - t3:.6f}s, lo-lo filters {t5 - t4:.6f}s, hi-lo filters {t6 - t5:.6f}s"
        )
        self.trade.logger.info("Pairs spun up: " + str(self.pairs_primed) + ", pairs considered: " + str(self.pairs_considered) + ", pairs kept: " + str(self.pairs_kept))

        return hi_hi_ranges

    @cython.cfunc
    def _seed_btn_offset_by_dist(self):
        self.btn_offset_by_dist = np.zeros(self.btn_max_range + 1, dtype=np.int32)
        for i in range(0, self.btn_max_range + 1):
            self.btn_offset_by_dist[i] = self._get_btn_offset(i)
        self.btn_offset_by_dist_view = self.btn_offset_by_dist

    @cython.cfunc
    @cython.returns(cython.int)
    def _get_btn_upper_bound(self, star1: Star, star2: Star, max_range: cython.int, min_btn: cython.int, distance: cython.int):
        """
        Return an _upper bound_ on the BTN between star1 and star2.  If the upper bound on BTN
        doesn't meet/beat the minimum BTN, then the _actual_ BTN, which also doesn't meet/beat
        the minimum, doesn't need to be calculated.  If star1 and star2 are less than the supplied
        max_range apart in pc, set the returned BTN upper bound to greater of upper-bounded BTN and
        supplied min_btn.
        """
        # Default assumes BTN is boosted by both agricultural and industrial matches
        wtn1: cython.int = star1.wtn
        wtn2: cython.int = star2.wtn

        # btn: cython.int = wtn1 + wtn2 + 2 + RouteCalculation.get_btn_allies(star1.alg_code, star2.alg_code)
        btn: cython.int = wtn1 + wtn2 + 2 + self._get_btn_allies(star1.alg_code, star2.alg_code)

        btn += self.btn_offset_by_dist_view[distance]
        btn = min(btn, self._get_max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @cython.cfunc
    @cython.returns(cython.int)
    def _get_rough_btn_upper_bound(self, wtn1: cython.int, wtn2: cython.int, max_range: cython.int, min_btn: cython.int, distance: cython.int):
        btn: cython.int = wtn1 + wtn2 + 2
        btn += self.btn_offset_by_dist_view[distance]
        btn = min(btn, self._get_max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    @cython.cfunc
    @cython.inline
    @cython.returns(cython.int)
    def _distance(del_q: cython.int, del_r: cython.int):
        aq: cython.int = del_q if del_q >= 0 else -del_q
        ar: cython.int = del_r if del_r >= 0 else -del_r
        ad: cython.int = del_q + del_r
        ad = ad if ad >= 0 else -ad
        dist: cython.int = (aq + ar + ad) // 2
        return dist

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    @cython.returns(cython.list[cython.tuple[Star, Star]])
    def _base_ranges(self, hiball: cython.list[Star], max_range: cython.int, min_btn: cython.int):
        n: cython.Py_ssize_t = len(hiball)
        ranges: cython.list[cython.tuple[Star, Star]] = []
        i: cython.Py_ssize_t
        j: cython.Py_ssize_t
        histar: Star
        lostar: Star
        dist: cython.int
        q1: cython.int
        del_q: cython.int
        r1: cython.int
        del_r: cython.int
        hi_wtn: cython.int
        lo_wtn: cython.int
        max_dist: cython.int
        upper2: cython.int
        upper1: cython.int
        upper0: cython.int
        zero: TradeCodes

        max_dist_fn = self._max_dist
        max_dist_array: cnp.ndarray[cython.int] = np.zeros((16, 16), dtype=np.int32)
        for i in range(16):
            for j in range(16):
                max_dist = max_dist_fn(i, j, True)
                max_dist_array[i][j] = max_dist
        max_dist_array_view: cython.int[:, :] = max_dist_array
        wtn_array: cnp.ndarray[cython.int] = np.zeros(n, dtype=np.int32)
        q_array: cnp.ndarray[cython.int] = np.zeros(n, dtype=np.int32)
        r_array: cnp.ndarray[cython.int] = np.zeros(n, dtype=np.int32)
        ag_boost_array: cnp.ndarray[cython.ushort] = np.zeros(n, dtype=np.uint8)
        ag_array: cnp.ndarray[cython.ushort] = np.zeros(n, dtype=np.uint8)
        in_boost_array: cnp.ndarray[cython.ushort] = np.zeros(n, dtype=np.uint8)
        in_array: cnp.ndarray[cython.ushort] = np.zeros(n, dtype=np.uint8)
        for i in range(n):
            histar = hiball[i]
            wtn_array[i] = histar.wtn
            q_array[i] = histar.hex.q
            r_array[i] = histar.hex.r
            zero = histar.tradeCode
            ag_boost_array[i] = 1 if zero.ag_code_boost else 0
            ag_array[i] = 1 if zero.agricultural else 0
            in_boost_array[i] = 1 if zero.in_code_boost else 0
            in_array[i] = 1 if zero.industrial else 0
        wtn_array_view: cython.int[:] = wtn_array
        q_array_view: cython.int[:] = q_array
        r_array_view: cython.int[:] = r_array
        ag_boost_array_view: cython.uchar[:] = ag_boost_array
        ag_array_view: cython.uchar[:] = ag_array
        in_boost_array_view: cython.uchar[:] = in_boost_array
        in_array_view: cython.uchar[:] = in_array
        pairs_primed: cython.long = 0
        pairs_considered: cython.long = 0
        pairs_kept: cython.long = 0
        ag_boost: cython.bint
        in_boost: cython.bint

        for i in range(n - 1):
            histar = hiball[i]
            q1 = q_array_view[i]
            r1 = r_array_view[i]
            hi_wtn = wtn_array_view[i]

            for j in range(i + 1, n):
                pairs_primed += 1
                lo_wtn = wtn_array_view[j]
                max_dist = max_dist_array_view[hi_wtn][lo_wtn]
                del_q = q1 - q_array_view[j]
                if del_q > max_dist or del_q < -max_dist:
                    continue
                del_r = r1 - r_array_view[j]
                if del_r > max_dist or del_r < -max_dist:
                    continue

                dist = TradeCalculationRawRoutes._distance(del_q, del_r)
                if dist > max_dist:
                    continue
                upper2 = self._get_rough_btn_upper_bound(hi_wtn, lo_wtn, max_range, min_btn, dist)
                if min_btn > upper2:
                    continue
                lostar = hiball[j]
                pairs_considered += 1
                upper2 = self._get_btn_upper_bound(histar, lostar, max_range, min_btn, dist)
                if min_btn > upper2:
                    continue
                if dist <= max_range:
                    upper1 = max(min_btn, upper2 - 1)
                    upper0 = max(min_btn, upper2 - 2)
                else:
                    upper1 = upper2 - 1
                    upper0 = upper2 - 2

                pairs_kept += 1
                ag_boost = (ag_boost_array_view[i] & ag_boost_array_view[j]
                            & (ag_array_view[i] | ag_array_view[j]))
                in_boost = (in_boost_array_view[i] & in_boost_array_view[j]
                            & (in_array_view[i] | in_array_view[j]))
                if ag_boost & in_boost:
                    ranges.append((histar, lostar))
                elif ag_boost ^ in_boost:
                    if upper1 >= min_btn:
                        ranges.append((histar, lostar))
                else:
                    if upper0 >= min_btn:
                        ranges.append((histar, lostar))

        self.pairs_primed = pairs_primed
        self.pairs_considered = pairs_considered
        self.pairs_kept = pairs_kept
        return ranges

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def _hi_lo_ranges(self, hiball: cython.list[Star], loball: cython.list[Star], offsets):
        m: cython.Py_ssize_t = len(hiball)
        ranges: cython.list[cython.tuple[Star, Star]] = []
        i: cython.Py_ssize_t
        histar: Star
        lostar: Star
        q1: cython.int
        r1: cython.int

        lob_map = {(s.hex.q, s.hex.r): s for s in loball}

        for i in range(m):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for dq, dr in offsets:
                lostar = lob_map.get((q1 + dq, r1 + dr))
                if lostar is not None:
                    ranges.append((histar, lostar))

        return ranges

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def _lo_lo_ranges(self, loball: cython.list[Star], offsets):
        n: cython.Py_ssize_t = len(loball)
        ranges: cython.list[cython.tuple[Star, Star]] = []
        i: cython.Py_ssize_t
        histar: Star
        lostar: Star
        q1: cython.int
        q2: cython.int
        r1: cython.int
        r2: cython.int

        lob_map = {(s.hex.q, s.hex.r): s for s in loball}

        for i in range(n - 1):
            histar = loball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for dq, dr in offsets:
                q2 = q1 + dq
                r2 = r1 + dr
                # Skip self; optional but saves one lookup
                if dq == 0 and dr == 0:
                    continue

                # Lexicographic uniqueness: only emit when (q1,r1) < (q2,r2)
                if q1 < q2 or (q1 == q2 and r1 < r2):
                    lostar = lob_map.get((q2, r2))
                    if lostar is not None:
                        ranges.append((histar, lostar))

        return ranges

    @staticmethod
    def _axial_offsets_within(R: cython.int):
        offsets: cython.list[cython.tuple[cython.int, cython.int]] = []
        for dq in range(-R, R + 1):
            for dr in range(-R, R + 1):
                dx = dq
                dz = dr
                dy = -dx - dz
                if (abs(dx) + abs(dy) + abs(dz)) // 2 <= R:
                    offsets.append((dq, dr))
        return offsets

    @cython.ccall
    @cython.returns(cython.int)
    def _get_btn_allies(self, alg_code1: str | None, alg_code2: str | None):
        return self._allies_dict[str(alg_code1) + "/" + str(alg_code2)]

    @cython.ccall
    @cython.returns(cython.int)
    def _max_dist(self, star_wtn: cython.int, neighbour_wtn: cython.int, maxjump: cython.bint = False):
        if neighbour_wtn < star_wtn:
            return self._max_dist(neighbour_wtn, star_wtn, maxjump)
        offset = min(max(0, neighbour_wtn - self.min_wtn), 6)
        max_dist = self.btn_range[offset]
        if maxjump:
            return max(max_dist, self.max_range)
        return max_dist

    @cython.cfunc
    @cython.returns(cython.int)
    def _get_max_btn(self, star_wtn: cython.int, neighbour_wtn: cython.int):
        if neighbour_wtn > star_wtn:
            neighbour_wtn, star_wtn = star_wtn, neighbour_wtn
        return (neighbour_wtn * 2) + 1

    @cython.cfunc
    @cython.returns(cython.int)
    def _get_btn_offset(self, distance: cython.int):
        index: cython.Py_ssize_t = self._lower_bound_int(self.btn_jump_range_view, distance)
        if index >= self.btn_jump_range_view.shape[0]:
            index = self.btn_jump_range_view.shape[0] - 1

        return self.btn_jump_mod_view[index]

    @cython.cfunc
    @cython.returns(cython.Py_ssize_t)
    @cython.nogil
    def _lower_bound_int(self, arr: cython.int[:], x: cython.int):
        lo: cython.Py_ssize_t = 0
        hi: cython.Py_ssize_t = arr.shape[0]
        mid: cython.Py_ssize_t

        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo
