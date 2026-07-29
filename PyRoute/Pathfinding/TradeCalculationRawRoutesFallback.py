"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import itertools
import time
import numpy as np

from Position.Hex import Hex
from PyRoute import Star
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.TradeCodes import TradeCodes


class TradeCalculationRawRoutes(object):

    def __init__(self, trade):
        from PyRoute.Calculation.TradeCalculation import TradeCalculation
        if not isinstance(trade, TradeCalculation):
            raise ValueError("Trade must be instance of TradeCalculation or subclass")
        self.trade = trade
        self.pairs_primed: int = 0
        self.pairs_stars_loaded: int = 0
        self.pairs_considered: int = 0
        self.pairs_kept: int = 0

    def raw_ranges(self) -> list[tuple[Star, Star]]:
        t0 = time.perf_counter()
        max_route_dist = max(self.trade.btn_range)
        max_range = self.trade.galaxy.max_jump_range
        min_btn = self.trade.min_btn
        min_wtn = self.trade.min_route_wtn
        t1 = time.perf_counter()

        hiball = [item for item in self.trade.galaxy.ranges if item.wtn >= min_wtn and not item.is_redzone]
        loball = [item for item in self.trade.galaxy.ranges if item.wtn < min_wtn and not item.is_redzone]
        offsets = TradeCalculationRawRoutes._axial_offsets_within(max_range)
        t2 = time.perf_counter()

        def two_boost(x: tuple[Star, Star, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) and \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def one_boost(x: tuple[Star, Star, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) ^ \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def foo_boost(x: tuple[Star, Star, int]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) or \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        ranges = self._base_ranges(hiball, max_range, min_btn)
        t3 = time.perf_counter()
        hi_hi_ranges, hi_hi_ranges1, hi_hi_ranges2 = self._hi_hi_ranges(foo_boost, max_range, min_btn, one_boost,
                                                                        ranges, two_boost)
        t4 = time.perf_counter()
        lo_lo_ranges = self._lo_lo_ranges(loball, max_range, offsets)
        t5 = time.perf_counter()
        hi_lo_ranges = self._hi_lo_ranges(hiball, loball, offsets)
        t6 = time.perf_counter()
        hi_hi_ranges.extend(lo_lo_ranges)
        hi_hi_ranges.extend(hi_lo_ranges)
        hi_hi_ranges.extend(hi_hi_ranges1)
        hi_hi_ranges.extend(hi_hi_ranges2)
        self.trade.logger.info("Routes with endpoints more than " + str(max_route_dist) + " pc apart, trimmed")
        self.trade.logger.info(
            f"raw_ranges phases: init {t1 - t0:.6f}s, split {t2 - t1:.6f}s, ranges {t3 - t2:.6f}s, hi-hi filters {t4 - t3:.6f}s, lo-lo filters {t5 - t4:.6f}s, hi-lo filters {t6 - t5:.6f}s"
        )
        self.trade.logger.info("Pairs spun up: " + str(self.pairs_primed) + ", stars loaded: " +
                               str(self.pairs_stars_loaded) + ", pairs considered: " + str(self.pairs_considered) +
                               ", pairs kept: " + str(self.pairs_kept))

        return hi_hi_ranges

    def _hi_lo_ranges(self, hiball, loball, offsets: list[tuple[int, int]]):
        m: int = len(hiball)
        lob_map = {(s.hex.q, s.hex.r): s for s in loball}
        hi_lo_ranges: list[tuple[Star, Star]] = []

        for i in range(m):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for dq, dr in offsets:
                lostar = lob_map.get((q1 + dq, r1 + dr))
                if lostar is not None:
                    hi_lo_ranges.append((histar, lostar))

        return hi_lo_ranges

    def _lo_lo_ranges(self, loball, max_range, offsets: list[tuple[int, int]]):
        n: int = len(loball)
        lob_map = {(s.hex.q, s.hex.r): s for s in loball}
        lo_lo_ranges: list[tuple[Star, Star]] = []

        for i in range(n - 1):
            histar: Star = loball[i]
            q1: int = histar.hex.q
            r1: int = histar.hex.r

            for dq, dr in offsets:
                q2: int = q1 + dq
                r2: int = r1 + dr
                # Skip self; optional but saves one lookup
                if dq == 0 and dr == 0:
                    continue

                # Lexicographic uniqueness: only emit when (q1,r1) < (q2,r2)
                if q1 < q2 or (q1 == q2 and r1 < r2):
                    lostar = lob_map.get((q2, r2))
                    if lostar is not None:
                        lo_lo_ranges.append((histar, lostar))

        return lo_lo_ranges

    def _hi_hi_ranges(self, foo_boost, max_range, min_btn, one_boost, ranges, two_boost):
        hi_hi_ranges = [(star, neighbour) for (star, neighbour, dist) in filter(two_boost, ranges)]
        hi_hi_ranges1 = [(star, neighbour) for (star, neighbour, dist) in filter(one_boost, ranges)
                         if self._get_btn_upper_bound(star, neighbour, max_range, min_btn, offset=1, distance=dist) >= min_btn
                         ]
        hi_hi_ranges2 = [(star, neighbour) for (star, neighbour, dist) in itertools.filterfalse(foo_boost, ranges)
                         if self._get_btn_upper_bound(star, neighbour, max_range, min_btn, offset=0, distance=dist) >= min_btn
                         ]
        return hi_hi_ranges, hi_hi_ranges1, hi_hi_ranges2

    def _base_ranges(self, hiball: list[Star], max_range: int, min_btn: int):
        n: int = len(hiball)
        ranges: list[tuple[Star, Star, int]] = []
        ranges_set: set[tuple[Star, Star, int]] = set()
        pairs_primed: int = 0
        pairs_stars_Loaded: int = 0
        pairs_considered: int = 0
        pairs_kept: int = 0
        world_wtn = np.zeros(n, dtype=np.int64)
        q_array = np.zeros(n, dtype=np.int64)
        r_array = np.zeros(n, dtype=np.int64)
        max_wtn_distances = np.zeros(n, dtype=np.int64)
        offsets: dict[int, list[tuple[int, int]]] = {}
        for i in range(n):
            histar: Star = hiball[i]
            world_wtn[i] = histar.wtn
            q_array[i] = histar.hex.q
            r_array[i] = histar.hex.r
            max_dist: int = self.trade._max_dist(world_wtn[i], world_wtn[i], True)
            max_wtn_distances[i] = max_dist
            if max_dist not in offsets:
                offsets[max_dist] = TradeCalculationRawRoutes._axial_offsets_within(max_dist)

        hib_map = {(s.hex.q, s.hex.r): s for s in hiball}

        for i in range(n):
            histar: Star = hiball[i]
            hihex: Hex = histar.hex
            hi_wtn: int = world_wtn[i]
            q1 = q_array[i]
            r1 = r_array[i]
            max_wtn_dist = max_wtn_distances[i]
            offset = offsets[max_wtn_dist]

            for dq, dr in offset:
                pairs_primed += 1
                # Skip self; optional but saves one lookup
                if dq == 0 and dr == 0:
                    continue
                # Lexicographic uniqueness: only emit when (q1,r1) < (q2,r2)
                if True:
                    lostar: Star = hib_map.get((q1 + dq, r1 + dr))
                    if lostar is None:
                        continue
                    lo_wtn = lostar.wtn
                    max_dist: int = self.trade._max_dist(hi_wtn, lo_wtn, True)
                    lohex: Hex = lostar.hex
                    pairs_stars_Loaded += 1

                    dist: int = hihex.distance(lohex)
                    if dist > max_dist:
                        continue
                    pairs_considered += 1
                    upbound = self._get_rough_btn_upper_bound(hi_wtn, lo_wtn, max_range, min_btn, distance=dist)
                    if upbound < min_btn:
                        continue
                    upbound = self._get_btn_upper_bound(histar, lostar, max_range, min_btn, distance=dist)
                    if upbound < min_btn:
                        continue
                    if lostar.name < histar.name:
                        ranges_set.add((lostar, histar, dist))
                    else:
                        ranges_set.add((histar, lostar, dist))
                    pairs_kept += 1

        self.pairs_primed = pairs_primed
        self.pairs_stars_loaded = pairs_stars_Loaded
        self.pairs_considered = pairs_considered
        self.pairs_kept = pairs_kept

        ranges = list(ranges_set)
        return ranges

    @staticmethod
    def _get_btn_upper_bound(star1: Star, star2: Star, max_range: int, min_btn: int, distance: int, offset: int = 2):
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

        btn += RouteCalculation.get_btn_offset(distance)
        btn = min(btn, RouteCalculation.get_max_btn(star1.wtn, star2.wtn))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    def _get_rough_btn_upper_bound(wtn1: int, wtn2: int, max_range: int, min_btn: int, distance: int):
        btn = wtn1 + wtn2 + 2

        btn += RouteCalculation.get_btn_offset(distance)
        btn = min(btn, RouteCalculation.get_max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    def _axial_offsets_within(R: int):
        offsets: list[tuple[int, int]] = []
        for dq in range(-R, R + 1):
            for dr in range(-R, R + 1):
                dx = dq
                dz = dr
                dy = -dx - dz
                if (abs(dx) + abs(dy) + abs(dz)) // 2 <= R:
                    offsets.append((dq, dr))
        return offsets
