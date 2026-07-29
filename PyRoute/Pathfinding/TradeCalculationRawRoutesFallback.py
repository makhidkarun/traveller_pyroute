"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import itertools
import time

from PyRoute import Star
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.TradeCodes import TradeCodes


class TradeCalculationRawRoutes(object):

    def __init__(self, trade):
        from PyRoute.Calculation.TradeCalculation import TradeCalculation
        if not isinstance(trade, TradeCalculation):
            raise ValueError("Trade must be instance of TradeCalculation or subclass")
        self.trade = trade

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
        lo_lo_ranges = self._lo_lo_ranges(loball, max_range)
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

    def _lo_lo_ranges(self, loball, max_range):
        lo_lo_ranges = [(star, neighbour) for (star, neighbour) in itertools.combinations(loball, 2)
                        if (star.distance(neighbour)) <= max_range
                        ]
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

    def _base_ranges(self, hiball, max_range, min_btn):
        ranges = [(star, neighbour, dist) for (star, neighbour) in itertools.combinations(hiball, 2)
                  if (dist := star.distance(neighbour)) <= self.trade._max_dist(star.wtn, neighbour.wtn, True)
                  and self._get_btn_upper_bound(star, neighbour, max_range, min_btn, distance=dist) >= min_btn
                  ]
        return ranges

    @staticmethod
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
