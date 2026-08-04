"""
Created on Jul 22, 2026

@author: CyberiaResurrection
"""
import functools
import time
from array import array
from typing import Optional

import numpy as np

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
        self.pairs_considered: int = 0
        self.pairs_kept: int = 0
        self.pairs_added: int = 0
        self.pairs_rough: int = 0
        self.pairs_smooth: int = 0

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
        self.trade.logger.info("Pairs spun up: " + str(self.pairs_primed) + ", pairs considered: " + str(self.pairs_considered) +
                               ", pairs kept: " + str(self.pairs_kept) + ", pairs added: " + str(self.pairs_added))
        self.trade.logger.info("Pairs passing rough BTN upper bound: " + str(self.pairs_rough) + ", pairs passing smooth BTN upper bound: " + str(self.pairs_smooth))

        return hi_hi_ranges

    def _hi_lo_ranges(self, hiball, loball, offsets: list[tuple[int, int, int]]):
        # Count the shorter of hiball and loball as hiball for this, since the main loop depends on hiball length
        if len(hiball) > len(loball):
            hiball, loball = loball, hiball
        m: int = len(hiball)
        lob_map = {(s.hex.q, s.hex.r): s for s in loball}
        hi_lo_ranges: list[tuple[Star, Star]] = []

        for i in range(m):
            histar = hiball[i]
            q1 = histar.hex.q
            r1 = histar.hex.r

            for dq, dr, _ in offsets:
                lostar = lob_map.get((q1 + dq, r1 + dr))
                if lostar is not None:
                    hi_lo_ranges.append((histar, lostar))

        return hi_lo_ranges

    def _lo_lo_ranges(self, loball, offsets: list[tuple[int, int, int]]):
        n: int = len(loball)
        lob_map = {(s.hex.q, s.hex.r): s for s in loball}
        lo_lo_ranges: set[tuple[Star, Star]] = set()

        for i in range(n):
            histar: Star = loball[i]
            q1: int = histar.hex.q
            r1: int = histar.hex.r

            for dq, dr, _ in offsets:
                lostar: Optional[Star] = lob_map.get((q1 + dq, r1 + dr))
                if lostar is not None:
                    # Skip self
                    if dq == 0 and dr == 0:
                        continue
                    if lostar.name < histar.name:
                        lo_lo_ranges.add((lostar, histar))
                    else:
                        lo_lo_ranges.add((histar, lostar))

        return list(lo_lo_ranges)

    def _base_ranges(self, hiball: list[Star], max_range: int, min_btn: int):
        n: int = len(hiball)
        pairs_primed: int = 0
        pairs_considered: int = 0
        pairs_kept: int = 0
        pairs_added: int = 0
        pairs_rough: int = 0
        pairs_smooth: int = 0
        world_wtn = np.zeros(n, dtype=np.int64)
        q_array = np.zeros(n, dtype=np.int64)
        r_array = np.zeros(n, dtype=np.int64)
        max_wtn_distances = np.zeros(n, dtype=np.int64)
        offsets: dict[int, list[tuple[int, int, int]]] = {}
        base_btn: dict[int, int] = {}
        i_map: dict[tuple[int, int], int] = {}
        ag_boost_array = np.zeros(n, dtype=np.uint8)
        ag_array = np.zeros(n, dtype=np.uint8)
        in_boost_array = np.zeros(n, dtype=np.uint8)
        in_array = np.zeros(n, dtype=np.uint8)
        alg_code_array: list[Optional[str]] = [None] * n

        get_rough = self._get_rough_btn_upper_bound
        get_upper = self._get_btn_upper_bound

        for i in range(n):
            histar: Star = hiball[i]
            world_wtn[i] = histar.wtn
            q_array[i] = histar.hex.q
            r_array[i] = histar.hex.r
            max_dist: int = self.trade._max_dist(world_wtn[i], world_wtn[i], True)
            max_wtn_distances[i] = max_dist
            i_map[(q_array[i], r_array[i])] = i
            hi_trade: TradeCodes = histar.tradeCode
            ag_boost_array[i] = 1 if hi_trade.ag_code_boost else 0
            ag_array[i] = 1 if hi_trade.agricultural else 0
            in_boost_array[i] = 1 if hi_trade.in_code_boost else 0
            in_array[i] = 1 if hi_trade.industrial else 0
            alg_code_array[i] = histar.alg_code

        half_offset = max(max_wtn_distances)
        max_q = max(q_array) + half_offset
        min_q = min(q_array) - half_offset
        max_r = max(r_array) + half_offset
        min_r = min(r_array) - half_offset
        q_size = (max_q - min_q) + 1
        r_size = (max_r - min_r) + 1
        idx_map = array('i', [-1]) * q_size * r_size

        for i in range(n):
            q = q_array[i] - min_q
            r = r_array[i] - min_r
            idx_map[q * r_size + r] = i
            max_dist = max_wtn_distances[i]
            if max_dist not in offsets:
                offsets[max_dist] = TradeCalculationRawRoutes._axial_offsets_within(max_dist, r_size=int(r_size))
                offsets[max_dist] = [(dq, dr, dist, delta) for (dq, dr, dist, delta) in offsets[max_dist] if
                                     not (dq == 0 and dr == 0)]
                base_btn[max_dist] = min_btn if max_range > max_range else 0

        hi_hi_ranges_list: list[tuple[int, int]] = []
        append_pair = hi_hi_ranges_list.append

        for i in range(n):
            hi_wtn: int = world_wtn[i]
            hi_ag_boost = ag_boost_array[i]
            hi_in_boost = in_boost_array[i]
            hi_ag = ag_array[i]
            hi_in = in_array[i]
            hi_alg = alg_code_array[i]

            offset = offsets[max_wtn_distances[i]]
            btn_min = base_btn[max_wtn_distances[i]]
            base_idx = (q_array[i] - min_q) * r_size + (r_array[i] - min_r)
            for _, _, dist, delta in offset:
                j = idx_map[base_idx + delta]
                if -1 == j:
                    continue

                pairs_primed += 1
                lo_wtn = world_wtn[j]

                pairs_considered += 1
                upbound = get_rough(hi_wtn, lo_wtn, max_range, min_btn, distance=dist)
                pairs_rough += 1
                if upbound < min_btn:
                    continue

                upbound = get_upper(hi_wtn, lo_wtn, hi_alg, alg_code_array[j], max_range, min_btn, distance=dist)
                pairs_smooth += 1
                if upbound < min_btn:
                    continue

                # ag_code_boost: bool = hi_ag_boost and ag_boost_array[j] and (hi_ag or ag_array[j])
                # Case 1 - hi_ag is true, thus (hi_ag or X) is true no matter X
                # Case 2 - hi_ag is false, thus (hi_ag or X) is X
                if hi_ag == 1:
                    ag_code_boost: bool = hi_ag_boost & ag_boost_array[j]
                else:
                    ag_code_boost: bool = hi_ag_boost & ag_boost_array[j] & ag_array[j]
                # in_code_boost: bool = hi_in_boost and in_boost_array[j] and (hi_in or in_array[j])
                # Case 1 - hi_in is true, thus (hi_in or X) is true no matter X
                # Case 2 - hi_in is false, thus (hi_in or X) is X
                if hi_in == 1:
                    in_code_boost: bool = hi_in_boost & in_boost_array[j]
                else:
                    in_code_boost: bool = hi_in_boost & in_boost_array[j] & in_array[j]
                if ag_code_boost & in_code_boost:
                    pairs_added += 1
                    if j < i:
                        append_pair((j, i))
                    else:
                        append_pair((i, j))
                elif ag_code_boost ^ in_code_boost:
                    upper1 = max(btn_min, upbound - 1)
                    if upper1 >= min_btn:
                        pairs_added += 1
                        if j < i:
                            append_pair((j, i))
                        else:
                            append_pair((i, j))
                else:
                    upper0 = max(btn_min, upbound - 2)
                    if upper0 >= min_btn:
                        pairs_added += 1
                        if j < i:
                            append_pair((j, i))
                        else:
                            append_pair((i, j))
                pairs_kept += 1

        hi_hi_ranges_list.sort()
        w = 1
        for r in range(1, len(hi_hi_ranges_list)):
            if hi_hi_ranges_list[r] != hi_hi_ranges_list[w - 1]:
                hi_hi_ranges_list[w] = hi_hi_ranges_list[r]
                w += 1
        hi_hi_ranges = hi_hi_ranges_list[:w]

        self.pairs_primed = pairs_primed
        self.pairs_considered = pairs_considered
        self.pairs_kept = pairs_kept
        self.pairs_added = pairs_added
        self.pairs_rough = pairs_rough
        self.pairs_smooth = pairs_smooth

        return [(hiball[a], hiball[b]) for (a, b) in hi_hi_ranges]

    @staticmethod
    def _get_btn_upper_bound(wtn1: int, wtn2: int, alg_code1: Optional[str], alg_code2: Optional[str], max_range: int,
                             min_btn: int, distance: int, offset: int = 2):
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
        btn = TradeCalculationRawRoutes._get_btn_upper_bound_core(wtn1, wtn2, alg_code1, alg_code2) \
              + offset + TradeCalculationRawRoutes.btn_offset(distance)

        btn = min(btn, TradeCalculationRawRoutes.max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    @functools.cache
    def _get_btn_upper_bound_core(wtn1: int, wtn2: int, ally1: Optional[str], ally2: Optional[str]):
        return wtn1 + wtn2 + RouteCalculation.get_btn_allies(ally1, ally2)

    @staticmethod
    @functools.cache
    def btn_offset(dist: int) -> int:
        return RouteCalculation.get_btn_offset(dist)

    @staticmethod
    @functools.cache
    def max_btn(w1: int, w2: int) -> int:
        return RouteCalculation.get_max_btn(w1, w2)

    @staticmethod
    def _get_rough_btn_upper_bound(wtn1: int, wtn2: int, max_range: int, min_btn: int, distance: int):
        btn = wtn1 + wtn2 + 2 + TradeCalculationRawRoutes.btn_offset(distance)
        btn = min(btn, TradeCalculationRawRoutes.max_btn(wtn1, wtn2))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    def _axial_offsets_within(R: int, r_size: Optional[int] = None):
        offsets: list[tuple[int, int, int]] = []
        good_r = isinstance(r_size, int) and 0 < r_size
        for dq in range(-R, R + 1):
            for dr in range(-R, R + 1):
                dx = dq
                dz = dr
                dy = -dx - dz
                if (abs(dx) + abs(dy) + abs(dz)) // 2 <= R:
                    dist = (abs(dq) + abs(dr) + abs(dq + dr)) // 2
                    if good_r:
                        delta = dq * r_size + dr
                        offsets.append((dq, dr, dist, delta))
                    else:
                        offsets.append((dq, dr, dist))
        return offsets
