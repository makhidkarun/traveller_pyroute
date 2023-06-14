"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.Galaxy import Sector
from PyRoute.Star import Star, Nobles
from PyRoute.TradeCodes import TradeCodes


class DeltaStar(Star):

    @staticmethod
    def reduce(starline, drop_routes=False, drop_trade_codes=False, drop_noble_codes=False, drop_base_codes=False, drop_trade_zone=False, drop_extra_stars=False, reset_pbg=False, reset_worlds=False, reset_port=False, reset_tl=False):
        sector = Sector("dummy", " 0, 0")
        star = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        if not isinstance(star, DeltaStar):
            return None

        if drop_routes:
            star.reduce_routes()
        if drop_trade_codes:
            star.reduce_trade_codes()
        if drop_noble_codes:
            star.reduce_noble_codes()
        if drop_base_codes:
            star.reduce_base_codes()
        if drop_trade_zone:
            star.reduce_trade_zone()
        if drop_extra_stars:
            star.reduce_extra_stars()
        if reset_pbg:
            star.reduce_pbg()
        if reset_worlds:
            star.reduce_worlds()
        if reset_port:
            star.reduce_port()
        if reset_tl:
            star.reduce_tl()

        star.calculate_importance()
        return star.parse_to_line()

    @staticmethod
    def reduce_all(original):
        return DeltaStar.reduce(original, drop_routes=True, drop_trade_codes=True, drop_noble_codes=True, drop_base_codes=True, drop_trade_zone=True, drop_extra_stars=True, reset_pbg=True, reset_worlds=True, reset_port=True, reset_tl=True)

    @staticmethod
    def reduce_auxiliary(original):
        return DeltaStar.reduce(original, drop_routes=True, drop_noble_codes=True, drop_trade_zone=True, drop_extra_stars=True, reset_pbg=True, reset_worlds=True)

    @staticmethod
    def parse_line_into_star(line, sector, pop_code, ru_calc):
        star = DeltaStar()
        return Star._parse_line_into_star_core(star, line, sector, pop_code, ru_calc)

    def reduce_routes(self):
        self.routes = []

    def reduce_trade_codes(self):
        self.tradeCode = TradeCodes('')

    def reduce_noble_codes(self):
        self.nobles = Nobles()

    def reduce_base_codes(self):
        self.baseCode = '-'

    def reduce_trade_zone(self):
        self.zone = '-'

    def reduce_extra_stars(self):
        if 0 < len(self.star_list):
            self.star_list = [self.star_list[0]]

    def reduce_pbg(self):
        self.popM = 1
        self.ggCount = 0
        self.belts = 0

    def reduce_worlds(self):
        self.worlds = 0

    def reduce_port(self):
        self.port = 'C'

    def reduce_tl(self):
        self.tl = 8
