"""
Created on Jun 19, 2018

@author: tjoneslo
"""

import logging


class SpeculativeTrade(object):
    t5_trade_table = {
        "Ag": {"Ag": 1, "As": 1, "De": 1, "Hi": 1, "In": 1, "Ri": 1, "Va": 1},
        "As": {"As": 1, "In": 1, "Ri": 1, "Va": 1},
        "Ba": {"In": 1},
        "De": {"De": 1},
        "Fl": {"Fl": 1, "In": 1},
        "In": {"Ag": 1, "As": 1, "De": 1, "Fl": 1, "Hi": 1, "In": 1, "Ri": 1, "Va": 1},
        "Na": {"As": 1, "De": 1, "Va": 1},
        "Po": {"Ag": -1, "Hi": -1, "In": -1, "Ri": -1},
        "Ri": {"Ag": 1, "De": 1, "Hi": 1, "In": 1, "Ri": 1},
        "Va": {"As": 1, "In": 1, "Va": 1}}

    ct_trade_table = {
        "Ag": {"Ag": 1, "As": 1, "De": 1, "Hi": 1, "In": 1, "Lo": 1, "Na": 1, "Ri": 1},
        "As": {"As": 1, "In": 1, "Na": 1, "Ri": 1, "Va": 1},
        "Ba": {"Ag": 1, "In": 1},
        "De": {"De": 1, "Na": 1},
        "Fl": {"Fl": 1, "In": 1},
        "Hi": {"Hi": 1, "Lo": 1, "Ri": 1},
        "Ic": {"In": 1},
        "In": {"Ag": 1, "As": 1, "De": 1, "Fl": 1, "Hi": 1, "In": 1, "Ni": 1, "Po": 1, "Ri": 1, "Va": 1, "Wa": 1,
               "Oc": 1},
        "Lo": {"In": 1, "Ri": 1},
        "Na": {"As": 1, "De": 1, "Va": 1},
        "Ni": {"In": 1, "Ni": -1},
        "Po": {"Po": -1},
        "Ri": {"Ag": 1, "De": 1, "Hi": 1, "In": 1, "Na": 1, "Ri": 1},
        "Va": {"As": 1, "In": 1, "Va": 1},
        "Wa": {"In": 1, "Ri": 1, "Wa": 1, "Oc": 1},
        "Oc": {"In": 1, "Ri": 1, "Wa": 1, "Oc": 1}}

    def __init__(self, trade_version, stars):
        self.logger = logging.getLogger('PyRoute.SpeculativeTrade')
        self.trade_table = SpeculativeTrade.t5_trade_table if trade_version == "T5" else SpeculativeTrade.ct_trade_table
        self.stars = stars
        self.trade_version = trade_version

    def process_tradegoods(self):
        self.logger.info("Processing TradeGoods for worlds")
        for world in self.stars:
            self.get_source_tradegoods(world)
        if self.trade_version == 'None':
            return
        for (world, neighbor) in self.stars.edges():
            distance = world.hex_distance(neighbor)
            source_market = max(self.get_market_price(world, neighbor) - distance, 0)
            target_market = max(self.get_market_price(neighbor, world) - distance, 0)
            self.stars[world][neighbor]['SourceMarketPrice'] = int(source_market * 1000)
            self.stars[world][neighbor]['TargetMarketPrice'] = int(target_market * 1000)

    def get_market_price(self, source, market):
        price = 5.0
        actives_codes = ["Ag", "As", "Ba", "De", "Fl", "Hi", "Ic", "In", "Lo",
                         "Na", "Ni", "Po", "Ri", "Va", "Wa", "Oc"]

        source_codes = [code for code in source.tradeCode.codes if code in actives_codes]
        target_codes = [code for code in market.tradeCode.codes if code in actives_codes]
        for code in source_codes:
            target_list = self.trade_table.get(code, {})
            for market_code in target_codes:
                price += target_list.get(market_code, 0)

        if "As" in target_codes or "As" in source_codes:
            price -= 1
        if "Ba" in target_codes:
            price = 0
        if source.tl - market.tl > -10:
            price += (price * (source.tl - market.tl)) / 10.0
        else:
            price = 0

        price -= source.trade_cost
        return price

    def get_source_tradegoods(self, star):
        if self.trade_version == "T5":
            cost = self.T5_calculate_tradegoods(star)
        else:
            cost = self.CT_calculate_tradegoods(star)
        star.trade_cost = cost
        star.trade_id = "{}-{} {} Cr{}".format(star.port, star.uwpCodes['Tech Level'],
                                                star.tradeCode.planet_codes(), int(cost * 1000))

    def T5_calculate_tradegoods(self, star):
        cost = 3.0
        cost -= 1 if star.tradeCode.agricultural else 0
        cost -= 1 if star.tradeCode.asteroid else 0
        cost += 1 if star.tradeCode.barren else 0
        cost += 1 if star.tradeCode.desert else 0
        cost += 1 if star.tradeCode.fluid else 0
        cost -= 1 if star.tradeCode.high else 0
        cost -= 1 if star.tradeCode.industrial else 0
        cost += 1 if star.tradeCode.low else 0
        cost += 1 if star.tradeCode.nonindustrial else 0
        cost -= 1 if star.tradeCode.poor else 0
        cost += 1 if star.tradeCode.rich else 0
        cost += 1 if star.tradeCode.vacuum else 0
        cost += star.tl / 10.0

        return cost

    def CT_calculate_tradegoods(self, star):
        cost = 4.0
        cost -= 1 if star.tradeCode.agricultural else 0
        cost -= 1 if star.tradeCode.asteroid else 0
        cost += 1 if star.tradeCode.desert else 0
        cost += 1 if star.tradeCode.fluid else 0
        cost -= 1 if star.tradeCode.high else 0
        cost -= 1 if star.tradeCode else 0
        cost += 2 if star.tradeCode.low else 0
        cost += 1 if star.tradeCode.nonindustrial else 0
        cost -= 1 if star.tradeCode.poor else 0
        cost += 1 if star.tradeCode.rich else 0
        cost += 1 if star.tradeCode.vacuum else 0
        cost += star.tl / 10.0
        cost -= 1 if 'A' in star.port else 0
        cost += 1 if 'C' in star.port else 0
        cost += 2 if 'D' in star.port else 0
        cost += 3 if 'E' in star.port else 0
        cost += 5 if 'X' in star.port else 0
        return cost
