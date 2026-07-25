# cython: profile=True
"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import cython
import itertools
import time

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

    def __init__(self, trade):
        from PyRoute.Calculation.TradeCalculation import TradeCalculation
        if not isinstance(trade, TradeCalculation):
            raise ValueError("Trade must be instance of TradeCalculation or subclass")
        self.trade = trade

    @profile
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def raw_ranges(self) -> list[tuple[Star, Star]]:
        t0 = time.perf_counter()
        max_route_dist = max(self.trade.btn_range)
        max_range = self.trade.galaxy.max_jump_range
        min_btn = self.trade.min_btn
        min_wtn = self.trade.min_route_wtn
        t1 = time.perf_counter()

        hiball = [item for item in self.trade.galaxy.ranges if item.wtn >= min_wtn and not item.is_redzone]
        loball = [item for item in self.trade.galaxy.ranges if item.wtn < min_wtn and not item.is_redzone]
        t2 = time.perf_counter()

        def two_boost(x: tuple[Star, Star, int, int, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) and \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def one_boost(x: tuple[Star, Star, int, int, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) ^ \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def foo_boost(x: tuple[Star, Star, int, int, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) or \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        ranges = self._base_ranges(hiball, max_range, min_btn)
        t3 = time.perf_counter()
        hi_hi_ranges = [(star, neighbour) for (star, neighbour, dist, upper1, upper0) in filter(two_boost, ranges)]
        hi_hi_ranges1 = [(star, neighbour) for (star, neighbour, dist, upper1, upper0) in filter(one_boost, ranges)
                         if upper1 >= min_btn
                         ]
        hi_hi_ranges2 = [(star, neighbour) for (star, neighbour, dist, upper1, upper0) in itertools.filterfalse(foo_boost, ranges)
                         if upper1 >= min_btn
                         ]
        t4 = time.perf_counter()
        lo_lo_ranges = self._lo_lo_ranges(loball, max_range)
        t5 = time.perf_counter()
        hi_lo_ranges = self._hi_lo_ranges(hiball, loball, max_range)
        t6 = time.perf_counter()
        hi_hi_ranges.extend(lo_lo_ranges)
        hi_hi_ranges.extend(hi_lo_ranges)
        hi_hi_ranges.extend(hi_hi_ranges1)
        hi_hi_ranges.extend(hi_hi_ranges2)
        self.trade.logger.info("Routes with endpoints more than " + str(max_route_dist) + " pc apart, trimmed")
        self.trade.logger.info(
            f"raw_ranges phases: init {t1 - t0:.6f}s, split {t2 - t1:.6f}s, ranges {t3 - t2:.6f}s, filters {t4 - t3:.6f}s, lo-lo filters {t5 - t4:.6f}s, hi-lo filters {t6 - t5:.6f}s"
        )

        return hi_hi_ranges

    @staticmethod
    @cython.returns(cython.int)
    def _get_btn_upper_bound(star1, star2, max_range, min_btn, distance=None, offset: int = 2):
        """
        Return an _upper bound_ on the BTN between star1 and star2.  If the upper bound on BTN
        doesn't meet/beat the minimum BTN, then the _actual_ BTN, which also doesn't meet/beat
        the minimum, doesn't need to be calculated.  If star1 and star2 are less than the supplied
        max_range apart in pc, set the returned BTN upper bound to greater of upper-bounded BTN and
        supplied min_btn.
        """
        # Default assumes BTN is boosted by both agricultural and industrial matches
        # Offset of 1 assumes BTN is boosted by one match, agricultural xor industrial
        # Offset of 0 assumes no boost.
        btn = star1.wtn + star2.wtn + offset + RouteCalculation.get_btn_allies(star1.alg_code, star2.alg_code)

        if distance is None:
            distance = star1.distance(star2)

        btn += RouteCalculation.get_btn_offset(distance)
        btn = min(btn, RouteCalculation.get_max_btn(star1.wtn, star2.wtn))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @cython.cfunc
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

        max_dist_fn = self.trade._max_dist

        for i in range(n - 1):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r
            hi_wtn = histar.wtn

            for j in range(i + 1, n):
                lostar = hiball[j]
                lo_wtn = lostar.wtn
                max_dist = max_dist_fn(hi_wtn, lo_wtn, True)
                del_q = q1 - lostar.hex.q
                if abs(del_q) > max_dist:
                    continue
                del_r = r1 - lostar.hex.r
                if abs(del_r) > max_dist:
                    continue
                dist = histar.distance(lostar)
                if dist > max_dist:
                    continue
                upper2 = self._get_btn_upper_bound(histar, lostar, max_range, min_btn, distance=dist)
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

    @cython.cfunc
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def _hi_lo_ranges(self, hiball: cython.list[Star], loball: cython.list[Star], max_range: cython.int):
        m: cython.Py_ssize_t = len(hiball)
        n: cython.Py_ssize_t = len(loball)
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
        range_sq = max_range * max_range

        for i in range(m):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for j in range(n):
                lostar = loball[j]
                del_q = q1 - lostar.hex.q
                if (del_q * del_q > range_sq):
                    continue
                del_r = r1 - lostar.hex.r
                if (del_r * del_r > range_sq):
                    continue

                dist = histar.distance(lostar)
                if dist <= max_range:
                    ranges.append((histar, lostar))

        return ranges

    @cython.cfunc
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def _lo_lo_ranges(self, loball: cython.list[Star], max_range: cython.int):
        n: cython.Py_ssize_t = len(loball)
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
        range_sq = max_range * max_range

        for i in range(n - 1):
            histar = loball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for j in range(i + 1, n):
                lostar = loball[j]
                del_q = q1 - lostar.hex.q
                if (del_q * del_q > range_sq):
                    continue
                del_r = r1 - lostar.hex.r
                if (del_r * del_r > range_sq):
                    continue

                dist = histar.distance(lostar)
                if dist <= max_range:
                    ranges.append((histar, lostar))

        return ranges
