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
    btn_jump_range: cnp.ndarray[cython.int]
    btn_jump_mod: cnp.ndarray[cython.int]
    btn_jump_range_view: cython.int[:]
    btn_jump_mod_view: cython.int[:]
    max_range: cython.int
    min_wtn: cython.int

    def __init__(self, trade):
        from PyRoute.Calculation.TradeCalculation import TradeCalculation
        if not isinstance(trade, TradeCalculation):
            raise ValueError("Trade must be instance of TradeCalculation or subclass")
        self.trade = trade
        self._allies_dict: dict = {}
        self.algs = set()
        self.btn_range = trade.btn_range
        self.btn_jump_range = np.array(trade.btn_jump_range, dtype=np.int32)
        self.btn_jump_range_view = self.btn_jump_range
        self.btn_jump_mod = np.array(trade.btn_jump_mod, dtype=np.int32)
        self.btn_jump_mod_view = self.btn_jump_mod
        self.max_range = self.trade.galaxy.max_jump_range
        self.min_wtn = self.trade.min_wtn

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
                self._allies_dict[(alg_code1, alg_code2)] = RouteCalculation.get_btn_allies(alg_code1, alg_code2)

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

        ranges = self._base_ranges(hiball, max_range, min_btn)
        t3 = time.perf_counter()
        hi_hi_ranges = self._hi_hi_ranges(ranges, min_btn)
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

        return hi_hi_ranges

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

        btn += self._get_btn_offset(distance)
        btn = min(btn, self._get_max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    @cython.cfunc
    @cython.returns(cython.int)
    def _distance(del_q: cython.int, del_r: cython.int):
        aq = del_q if del_q >= 0 else -del_q
        ar = del_r if del_r >= 0 else -del_r
        ad = del_q + del_r
        ad = ad if ad >= 0 else -ad
        dist = (aq + ar + ad) // 2
        return dist

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def _base_ranges(self, hiball: cython.list[Star], max_range: cython.int, min_btn: cython.int):
        n: cython.Py_ssize_t = len(hiball)
        ranges: cython.list[cython.tuple[Star, Star, int, int, int]] = []
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

        max_dist_fn = self._max_dist

        for i in range(n - 1):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r
            hi_wtn = histar.wtn

            for j in range(i + 1, n):
                lostar = hiball[j]
                lo_wtn = lostar.wtn
                lo_hex = lostar.hex
                max_dist = max_dist_fn(hi_wtn, lo_wtn, True)
                del_q = q1 - lo_hex.q
                if del_q > max_dist or del_q < -max_dist:
                    continue
                del_r = r1 - lo_hex.r
                if del_r > max_dist or del_r < -max_dist:
                    continue

                dist = TradeCalculationRawRoutes._distance(del_q, del_r)
                if dist > max_dist:
                    continue
                upper2 = self._get_btn_upper_bound(histar, lostar, max_range, min_btn, dist)
                if min_btn > upper2:
                    continue
                if dist <= max_range:
                    upper1 = max(min_btn, upper2 - 1)
                    upper0 = max(min_btn, upper2 - 2)
                else:
                    upper1 = upper2 - 1
                    upper0 = upper2 - 2

                ranges.append((histar, lostar, dist, upper1, upper0))

        return ranges

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    @cython.returns(cython.list[cython.tuple[Star, Star]])
    def _hi_hi_ranges(self, ranges: cython.list[cython.tuple[Star, Star, int, int, int]], min_btn: cython.int):
        nu_ranges: cython.list[cython.tuple[Star, Star]] = []
        m: cython.Py_ssize_t = len(ranges)
        item: cython.tuple[Star, Star, int, int, int]
        zero: TradeCodes
        wun: TradeCodes
        ag_boost: cython.bint
        in_boost: cython.bint

        for i in range(m):
            item = ranges[i]
            star = item[0]
            neighbour = item[1]
            zero = item[0].tradeCode
            wun = item[1].tradeCode
            upper1 = item[3]
            upper0 = item[4]
            ag_boost = (zero.ag_code_boost and wun.ag_code_boost
                        and (zero.agricultural or wun.agricultural))
            in_boost = (zero.in_code_boost and wun.in_code_boost
                        and (zero.industrial or wun.industrial))
            if ag_boost and in_boost:  # dual boost is already accounted for in filtering in base_ranges
                nu_ranges.append((star, neighbour))
            elif ag_boost ^ in_boost:  # exactly one of ag_boost or in_boost
                if upper1 >= min_btn:
                    nu_ranges.append((star, neighbour))
            else:  # neither ag_boost nor in_boost
                if upper0 >= min_btn:
                    nu_ranges.append((star, neighbour))

        return nu_ranges

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

            a = (q1, r1)
            for dq, dr in offsets:
                q2 = q1 + dq
                r2 = r1 + dr
                # Skip self; optional but saves one lookup
                if dq == 0 and dr == 0:
                    continue

                # Lexicographic uniqueness: only emit when (q1,r1) < (q2,r2)
                if a < (q2, r2):
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
        allies_dex: cython.tuple = (alg_code1, alg_code2)
        return self._allies_dict[allies_dex]

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
            return self._get_max_btn(neighbour_wtn, star_wtn)
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
