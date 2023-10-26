"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Galaxy import Sector
from PyRoute.Nobles import Nobles
from PyRoute.Star import Star
from PyRoute.TradeCodes import TradeCodes


class DeltaStar(Star):

    @staticmethod
    def reduce(starline, drop_routes=False, drop_trade_codes=False, drop_noble_codes=False, drop_base_codes=False, drop_trade_zone=False, drop_extra_stars=False, reset_pbg=False, reset_worlds=False, reset_port=False, reset_tl=False, reset_sophont=False, reset_capitals=False, canonicalise=False):
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        if not isinstance(star, DeltaStar):
            return None

        if canonicalise:
            star.canonicalise()
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
        if reset_sophont:
            star.reduce_sophonts()
        if reset_capitals:
            star.reduce_capitals()

        star.calculate_importance()
        return star.parse_to_line()

    @staticmethod
    def reduce_all(original):
        return DeltaStar.reduce(original, drop_routes=True, drop_trade_codes=True, drop_noble_codes=True, drop_base_codes=True, drop_trade_zone=True, drop_extra_stars=True, reset_pbg=True, reset_worlds=True, reset_port=True, reset_tl=True, reset_sophont=True)

    @staticmethod
    def reduce_auxiliary(original):
        return DeltaStar.reduce(original, drop_routes=True, drop_noble_codes=True, drop_trade_zone=True, drop_extra_stars=True, reset_pbg=True, reset_worlds=True, reset_sophont=True)

    @staticmethod
    def reduce_importance(original):
        return DeltaStar.reduce(original, drop_trade_codes=True, drop_base_codes=True, reset_port=True, reset_tl=True)

    @staticmethod
    def parse_line_into_star(line, sector, pop_code, ru_calc, fix_pop=False):
        star = DeltaStar()
        return ParseStarInput.parse_line_into_star_core(star, line, sector, pop_code, ru_calc, fix_pop=fix_pop)

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
            self.star_list_object.stars_list = [self.star_list_object.stars_list[0]]

    def reduce_pbg(self):
        self.popM = 1
        self.ggCount = 0
        self.belts = 0

    def reduce_worlds(self):
        self.worlds = 1

    def reduce_port(self):
        self.port = 'C'

    def reduce_tl(self):
        self.tl = 8

    def reduce_sophonts(self):
        nu_codes = []

        for code in self.tradeCode.codes:
            if code not in self.tradeCode.sophont_list and not code.startswith('Di('):
                nu_codes.append(code)

        self.tradeCode = TradeCodes(' '.join(nu_codes))

    def reduce_capitals(self):
        cap_codes = ['Cs', 'Cp', 'Cx']

        nu_codes = []
        for code in self.tradeCode.codes:
            if code not in cap_codes:
                nu_codes.append(code)

        self.tradeCode = TradeCodes(' '.join(nu_codes))

    def check_canonical(self):
        msg = []

        infrastructure = self._ehex_to_int(self.economics[3])

        if self.tradeCode.barren and infrastructure != 0:
            line = '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self, infrastructure, 0)
            msg.append(line)
        elif self.tradeCode.low and infrastructure != max(self.importance, 0):
            generated = max(self.importance, 0)
            line = '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self, infrastructure, generated)
            msg.append(line)
        elif self.tradeCode.nonindustrial and not 0 <= infrastructure <= 6 + self.importance:
            line = '{} - EX Calculated infrastructure {} not in NI range 0 - {}'.format(self, infrastructure, 6 + self.importance)
            msg.append(line)
        elif not 0 <= infrastructure <= 12 + self.importance:
            line = '{} - EX Calculated infrastructure {} not in range 0 - {}'.format(self, infrastructure, 12 + self.importance)
            msg.append(line)

        if '0' == str(self.atmo) and 'Va' not in self.tradeCode.codeset:
            code = 'Va'
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

        if '0' == str(self.atmo) and '0' == str(self.size) and '0' == str(self.hydro) and 'As' not in self.tradeCode.codeset:
            code = 'As'
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)
        elif 'As' in self.tradeCode.codeset and not ('0' == str(self.atmo) and '0' == str(self.size) and '0' == str(self.hydro)):
            code = 'As'
            line = '{}-{} Found invalid "{}" in trade codes: {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

        symbols = self._ehex_to_int(self.social[4] if self.social is not None else '1')  # TL + flux, min 1
        strangeness = self._ehex_to_int(self.social[3] if self.social is not None else '1')  # flux + 5
        acceptance = self._ehex_to_int(self.social[2] if self.social is not None else '1')  # pop + Ix, min 1
        homogeneity = self._ehex_to_int(self.social[1] if self.social is not None else '1')  # pop + flux, min 1
        labor = self._ehex_to_int(self.economics[2])
        pop = self.popCode
        if pop == 0 and symbols != 0:
            line = '{} - CX calculated symbols {} should be 0 for barren worlds'.format(self, symbols)
            msg.append(line)
        elif pop != 0 and not max(1, self.tl - 5) <= symbols <= self.tl + 5:
            line = '{} - CX calculated symbols {} not in range {} - {}'.format(self, symbols, max(1, self.tl - 5), self.tl + 5)
            msg.append(line)
        if pop == 0 and strangeness != 0:
            line = '{} - CX calculated strangeness {} should be 0 for barren worlds'.format(self, strangeness)
            msg.append(line)
        elif pop != 0 and not 1 <= strangeness <= 10:
            line = '{} - CX calculated strangeness {} not in range {} - {}'.format(self, strangeness, 1, 10)
            msg.append(line)
        if pop == 0 and acceptance != 0:
            line = '{} - CX calculated acceptance {} should be 0 for barren worlds'.format(self, acceptance)
            msg.append(line)
        elif pop != 0 and not max(1, pop + self.importance) == acceptance:
            line = '{} - CX Calculated acceptance {} does not match generated acceptance {}'.format(self, acceptance, max(1, pop + self.importance))
            msg.append(line)
        if pop == 0 and homogeneity != 0:
            line = '{} - CX calculated homogeneity {} should be 0 for barren worlds'.format(self, homogeneity)
            msg.append(line)
        elif pop != 0 and not max(1, pop - 5) <= homogeneity <= pop + 5:
            line = '{} - CX calculated homogeneity {} not in range {} - {}'.format(self, homogeneity, max(1, pop - 5), pop + 5)
            msg.append(line)
        if labor != max(self.popCode - 1, 0):
            line = '{} - EX Calculated labor {} does not match generated labor {}'.format(self, labor, max(self.popCode - 1, 0))
            msg.append(line)

        self._check_trade_code(msg, 'De', '0123456789ABC', '23456789', '0')
        self._check_trade_code(msg, 'Ga', '678', '568', '567')
        self._check_trade_code(msg, 'Fl', None, 'ABC', '123456789A')
        self._check_trade_code(msg, 'Ic', None, '01', '123456789A')
        self._check_trade_code(msg, 'Po', None, '2345', '0123')
        self._check_trade_code(msg, 'He', '3456789ABC', '2479ABC', '012')
        self._check_trade_code(msg, 'Wa', '3456789', '3456789DEF', 'A')
        self._check_trade_code(msg, 'Oc', 'ABCD', '3456789DEF', 'A')
        self._check_trade_code(msg, 'Va', None, '0', None)

        code = 'Ba'
        pop = '0'
        self._check_pop_code(msg, code, pop)

        code = 'Lo'
        pop = '123'
        self._check_pop_code(msg, code, pop)

        code = 'Ni'
        pop = '456'
        self._check_pop_code(msg, code, pop)

        code = 'Ph'
        pop = '8'
        self._check_pop_code(msg, code, pop)

        code = 'Hi'
        pop = '9ABCD'
        self._check_pop_code(msg, code, pop)

        self._check_econ_code(msg, 'Na', '0123', '0123', '6789ABCD')
        self._check_econ_code(msg, 'Pi', '012479', None, '78')
        self._check_econ_code(msg, 'In', '012479ABC', None, '9ABCD')
        self._check_econ_code(msg, 'Pr', '68', None, '59')
        self._check_econ_code(msg, 'Pa', '456789', '45678', '48')
        self._check_econ_code(msg, 'Ri', '68', None, '678')
        self._check_econ_code(msg, 'Ag', '456789', '45678', '567')

        return 0 == len(msg), msg

    def _check_trade_code(self, msg, code, size, atmo, hydro):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro

        if code in self.tradeCode.codeset and \
                not (self.size in size and self.atmo in atmo and self.hydro in hydro):
            line = '{}-{} Found invalid "{}" in trade codes: {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)
        elif (self.size in size and self.atmo in atmo and self.hydro in hydro) and code not in self.tradeCode.codeset:
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

    def _check_pop_code(self, msg, code, pop):
        check = True
        if self.pop in pop and code not in self.tradeCode.codeset:
            line = '{} - Calculated "{}" not in trade codes {}'.format(self, code, self.tradeCode.codeset)
            msg.append(line)
        if code in self.tradeCode.codeset and self.pop not in pop:
            line = '{} - Found invalid "{}" code on world with {} population: {}'.format(self, code, self.pop,
                                                                                       self.tradeCode.codeset)
            msg.append(line)
            check = False
        return check

    def _check_econ_code(self, msg, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop

        if self.atmo in atmo and self.hydro in hydro and self.pop in pop \
                and code not in self.tradeCode.codeset:
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)
        if code in self.tradeCode.codeset and \
                not (self.atmo in atmo and self.hydro in hydro and self.pop in pop):
            line = '{}-{} Found invalid "{}" in trade codes: {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

    def canonicalise(self):
        pass
