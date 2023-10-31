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

        if self.economics is not None:
            infrastructure = self._ehex_to_int(self.economics[3] if self.economics is not None else '0')
            if self.tradeCode.barren and infrastructure != 0:
                line = '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self,
                                                                                                                infrastructure,
                                                                                                                0)
                msg.append(line)
            elif self.tradeCode.low and infrastructure != max(self.importance, 0):
                generated = max(self.importance, 0)
                line = '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self,
                                                                                                                infrastructure,
                                                                                                                generated)
                msg.append(line)
            elif self.tradeCode.nonindustrial and not 0 <= infrastructure <= 6 + self.importance:
                line = '{} - EX Calculated infrastructure {} not in NI range 0 - {}'.format(self, infrastructure,
                                                                                            6 + self.importance)
                msg.append(line)
            elif not 0 <= infrastructure <= 12 + self.importance:
                line = '{} - EX Calculated infrastructure {} not in range 0 - {}'.format(self, infrastructure,
                                                                                         12 + self.importance)
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

        if self.social is not None:
            symbols = self._ehex_to_int(self.social[4] if self.social is not None else '1')  # TL + flux, min 1
            strangeness = self._ehex_to_int(self.social[3] if self.social is not None else '1')  # flux + 5
            acceptance = self._ehex_to_int(self.social[2] if self.social is not None else '1')  # pop + Ix, min 1
            homogeneity = self._ehex_to_int(self.social[1] if self.social is not None else '1')  # pop + flux, min 1
            labor = self._ehex_to_int(self.economics[2] if self.economics is not None else '0')
            pop = self.popCode
            if pop == 0 and symbols != 0:
                line = '{} - CX Calculated symbols {} should be 0 for barren worlds'.format(self, symbols)
                msg.append(line)
            elif pop != 0 and not max(1, self.tl - 5) <= symbols <= self.tl + 5:
                line = '{} - CX Calculated symbols {} not in range {} - {}'.format(self, symbols, max(1, self.tl - 5),
                                                                               self.tl + 5)
                msg.append(line)
            if pop == 0 and strangeness != 0:
                line = '{} - CX Calculated strangeness {} should be 0 for barren worlds'.format(self, strangeness)
                msg.append(line)
            elif pop != 0 and not 1 <= strangeness <= 10:
                line = '{} - CX Calculated strangeness {} not in range {} - {}'.format(self, strangeness, 1, 10)
                msg.append(line)
            pop_plus_imp = min(33, max(1, pop + self.importance))  # Cap out at 33 - converts to ehex as Z
            if pop == 0 and acceptance != 0:
                line = '{} - CX Calculated acceptance {} should be 0 for barren worlds'.format(self, acceptance)
                msg.append(line)
            elif pop != 0 and not pop_plus_imp == acceptance:
                line = '{} - CX Calculated acceptance {} does not match generated acceptance {}'.format(self, acceptance,
                                                                                                    max(1,
                                                                                                        pop + self.importance))
                msg.append(line)
            if pop == 0 and homogeneity != 0:
                line = '{} - CX Calculated homogeneity {} should be 0 for barren worlds'.format(self, homogeneity)
                msg.append(line)
            elif pop != 0 and not max(1, pop - 5) <= homogeneity <= pop + 5:
                line = '{} - CX Calculated homogeneity {} not in range {} - {}'.format(self, homogeneity, max(1, pop - 5),
                                                                                   pop + 5)
                msg.append(line)
            if self.economics is not None and labor != max(self.popCode - 1, 0):
                line = '{} - EX Calculated labor {} does not match generated labor {}'.format(self, labor,
                                                                                          max(self.popCode - 1, 0))
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

        code_match = code in self.tradeCode.codeset
        system_match = self.size in size and self.atmo in atmo and self.hydro in hydro

        if code_match and not system_match:
            line = '{}-{} Found invalid "{}" in trade codes: {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)
        elif system_match and not code_match:
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

    def _fix_trade_code(self, code, size, atmo, hydro):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro

        code_match = code in self.tradeCode.codeset
        system_match = self.size in size and self.atmo in atmo and self.hydro in hydro
        if code_match == system_match:
            return

        if code_match and not system_match:
            self._drop_invalid_trade_code(code)
        elif system_match and not code_match:
            self._add_missing_trade_code(code)

    def _check_pop_code(self, msg, code, pop):
        check = True

        pop_match = self.pop in pop
        code_match = code in self.tradeCode.codeset

        if pop_match and not code_match:
            line = '{} - Calculated "{}" not in trade codes {}'.format(self, code, self.tradeCode.codeset)
            msg.append(line)
        if code_match and not pop_match:
            line = '{} - Found invalid "{}" code on world with {} population: {}'.format(self, code, self.pop,
                                                                                       self.tradeCode.codeset)
            msg.append(line)
            check = False
        return check

    def _fix_pop_code(self, code, pop):
        pop_match = self.pop in pop
        code_match = code in self.tradeCode.codeset

        if pop_match == code_match:
            return

        if code_match and not pop_match:
            self._drop_invalid_trade_code(code)
        elif pop_match and not code_match:
            self._add_missing_trade_code(code)

    def _check_econ_code(self, msg, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop

        code_match = code in self.tradeCode.codeset
        phys_match = self.atmo in atmo and self.hydro in hydro and self.pop in pop

        if phys_match and not code_match:
            line = '{}-{} Calculated "{}" not in trade codes {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)
        if code_match and not phys_match:
            line = '{}-{} Found invalid "{}" in trade codes: {}'.format(self, self.uwp, code, self.tradeCode.codeset)
            msg.append(line)

    def _fix_econ_code(self, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop

        code_match = code in self.tradeCode.codeset
        phys_match = self.atmo in atmo and self.hydro in hydro and self.pop in pop

        if code_match == phys_match:
            return

        if code_match and not phys_match:
            self._drop_invalid_trade_code(code)
        elif phys_match and not code_match:
            self._add_missing_trade_code(code)

    def canonicalise(self):
        self._fix_trade_code('De', '0123456789ABC', '23456789', '0')
        self._fix_trade_code('Ga', '678', '568', '567')
        self._fix_trade_code('Fl', None, 'ABC', '123456789A')
        self._fix_trade_code('He', '3456789ABC', '2479ABC', '012')
        self._fix_trade_code('As', '0', '0', '0')
        self._fix_trade_code('Ic', None, '01', '123456789A')
        self._fix_trade_code('Oc', 'ABCD', '3456789DEF', 'A')
        self._fix_trade_code('Po', None, '2345', '0123')
        self._fix_trade_code('Va', None, '0', None)
        self._fix_trade_code('Wa', '3456789', '3456789DEF', 'A')

        self._fix_econ_code('Na', '0123', '0123', '6789ABCD')
        self._fix_econ_code('Ag', '456789', '45678', '567')
        self._fix_econ_code('Pa', '456789', '45678', '48')
        self._fix_econ_code('Pi', '012479', None, '78')
        self._fix_econ_code('Pr', '68', None, '59')
        self._fix_econ_code('In', '012479ABC', None, '9ABCD')
        self._fix_econ_code('Ri', '68', None, '678')

        self._fix_pop_code('Ba', '0')
        self._fix_pop_code('Lo', '123')
        self._fix_pop_code('Ni', '456')
        self._fix_pop_code('Ph', '8')
        self._fix_pop_code('Hi', '9ABCD')

        self._fix_economics()
        self._fix_social()

    def _fix_economics(self):
        if self.economics is None:
            return
        econ = self.economics
        if '0' == str(self.pop):
            self.social = '[0000]'

            econ = econ[:2] + '00' + econ[4:]

        elif self.tradeCode.low:
            econ = self.economics
            infrastructure = str(self._int_to_ehex(max(0, self.importance)))
            econ = econ[:3] + infrastructure + econ[4:]

        elif self.tradeCode.nonindustrial:
            old_infrastructure = self._ehex_to_int(self.economics[3])
            infrastructure = old_infrastructure
            if infrastructure > 6 + self.importance:
                infrastructure = str(self._int_to_ehex(6 + self.importance))
                econ = econ[:3] + infrastructure + econ[4:]

        else:
            old_infrastructure = self._ehex_to_int(self.economics[3])
            infrastructure = old_infrastructure
            if infrastructure > 12 + self.importance:
                infrastructure = str(self._int_to_ehex(12 + self.importance))
                econ = econ[:3] + infrastructure + econ[4:]
        labour = str(self._int_to_ehex(max(self.popCode - 1, 0)))
        econ = econ[:2] + labour + econ[3:]
        self.economics = econ

    def _fix_social(self):
        if self.social is None:
            return
        social = self.social
        pop = self.popCode

        old_strangeness = self._ehex_to_int(social[3])
        old_homogeneity = self._ehex_to_int(self.social[1])
        old_symbols = self._ehex_to_int(social[4])

        if '0' == str(self.pop) or '?' == str(self.pop):
            social = '[0000]'
        else:
            homogeneity = old_homogeneity
            if max(1, pop - 5) > homogeneity:
                homogeneity = max(1, pop - 5)
            elif (pop + 5) < homogeneity:
                homogeneity = pop + 5
            homogeneity = str(self._int_to_ehex(homogeneity))
            social = social[:1] + homogeneity + social[2:]

            pop_plus_imp = min(33, max(1, pop + self.importance))  # Cap out at 33 - converts to ehex as Z
            acceptance = str(self._int_to_ehex(pop_plus_imp))
            social = social[:2] + acceptance + social[3:]

            strangeness = old_strangeness
            if 1 > strangeness:
                strangeness = 1
            elif 10 < strangeness:
                strangeness = 10

            strangeness = str(self._int_to_ehex(strangeness))

            social = social[:3] + strangeness + social[4:]

            symbols = old_symbols
            if max(1, self.tl - 5) > symbols:
                symbols = max(1, self.tl - 5)
            elif self.tl + 5 < symbols:
                symbols = self.tl + 5

            symbols = str(self._int_to_ehex(symbols))

            social = social[:4] + symbols + social[5:]

        assert 6 == len(social), "Unexpected social code length"

        self.social = social

    def _drop_invalid_trade_code(self, targcode):
        self.tradeCode.codes = [code for code in self.tradeCode.codes if code != targcode]
        self.tradeCode.codeset = [code for code in self.tradeCode.codeset if code != targcode]

    def _add_missing_trade_code(self, targcode):
        self.tradeCode.codes.append(targcode)
        self.tradeCode.codeset.append(targcode)