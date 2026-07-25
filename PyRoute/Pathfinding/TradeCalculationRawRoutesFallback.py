"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import itertools

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
        max_route_dist = max(self.trade.btn_range)
        max_range = self.trade.galaxy.max_jump_range
        min_btn = self.trade.min_btn
        min_wtn = self.trade.min_route_wtn

        hiball = [item for item in self.trade.galaxy.ranges if item.wtn >= min_wtn and not item.is_redzone]
        loball = [item for item in self.trade.galaxy.ranges if item.wtn < min_wtn and not item.is_redzone]

        def two_boost(x: tuple[Star, Star]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) and \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def one_boost(x: tuple[Star, Star]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) ^ \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        def foo_boost(x: tuple[Star, Star]) -> bool:
            zero: TradeCodes = x[0].tradeCode
            wun: TradeCodes = x[1].tradeCode
            return (zero.ag_code_boost and wun.ag_code_boost
                    and (zero.agricultural or wun.agricultural)) or \
                   (zero.in_code_boost and wun.in_code_boost
                    and (zero.industrial or wun.industrial))

        ranges = [(star, neighbour) for (star, neighbour) in itertools.combinations(hiball, 2)
                  if (dist := star.distance(neighbour)) <= self.trade._max_dist(star.wtn, neighbour.wtn, True)
                  and self._get_btn_upper_bound(star, neighbour, max_range, min_btn, distance=dist) >= min_btn
                  ]
        hi_hi_ranges = [(star, neighbour) for (star, neighbour) in filter(two_boost, ranges)]
        hi_hi_ranges1 = [(star, neighbour) for (star, neighbour) in filter(one_boost, ranges)
                         if self._get_btn_upper_bound(star, neighbour, max_range, min_btn, offset=1) >= min_btn
                         ]
        hi_hi_ranges2 = [(star, neighbour) for (star, neighbour) in itertools.filterfalse(foo_boost, ranges)
                         if self._get_btn_upper_bound(star, neighbour, max_range, min_btn, offset=0) >= min_btn
                         ]
        lo_lo_ranges = [(star, neighbour) for (star, neighbour) in itertools.combinations(loball, 2)
                        if (star.distance(neighbour)) <= max_range
                        ]
        hi_lo_ranges = [(star, neighbour) for (star, neighbour) in itertools.product(hiball, loball)
                        if (star.distance(neighbour)) <= max_range
                        ]
        hi_hi_ranges.extend(lo_lo_ranges)
        hi_hi_ranges.extend(hi_lo_ranges)
        hi_hi_ranges.extend(hi_hi_ranges1)
        hi_hi_ranges.extend(hi_hi_ranges2)
        self.trade.logger.info("Routes with endpoints more than " + str(max_route_dist) + " pc apart, trimmed")

        return hi_hi_ranges

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
