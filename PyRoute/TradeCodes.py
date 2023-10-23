"""
Created on Oct 3, 2017

@author: tjoneslo
"""
import itertools
import re
import logging
import sys


class TradeCodes(object):
    """
    Trade Codes manage the complete set of trade codes for a world
    """
    pcodes = ['As', 'De', 'Ga', 'Fl', 'He', 'Ic', 'Oc', 'Po', 'Va', 'Wa']
    dcodes = ['Cp', 'Cx', 'Cs', 'Mr', 'Da', 'Di', 'Pz', 'An', 'Ab', 'Fo', 'Px',
              'Re', 'Rs', 'Sa', 'Tz', 'Lk',
              'RsA', 'RsB', 'RsG', 'RsD', 'RsE', 'RsZ', 'RsT', 'RsI', 'RsK',
              'Fr', 'Co', 'Tp', 'Ho', 'Tr', 'Tu',
              'Cm', 'Tw']
    ex_codes = {'As', 'Fl', 'Ic', 'De', 'Na', 'Va', 'Wa', 'He', 'Oc'}
    research = {'RsA': '\u0391', 'RsB': '\u0392', 'RsG': '\u0393',
                'RsD': '\u0394', 'RdE': '\u0395', 'RsZ': '\u0396',
                'RsT': '\u0398', 'RsI': '\u0399', 'RsK': '\u039A'}
    pcolor = {'As': '#8E9397', 'De': '#d17533', 'Fl': '#e37dff', 'He': '#ff6f0c', 'Ic': '#A5F2F3',
              'Oc': '#0094ED', 'Po': '#6a986a', 'Va': '#c9c9c9', 'Wa': '#4abef4'}
    ext_codes = {'Lt', 'Ht', 'Lg', 'Hg'}
    weird_codes = {'{Anomaly}', '{Fuel}', '{Ringworld}', '{Rosette}'}
    allowed_residual_codes = {'Ag', 'Ba', 'Bo', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'Cl', 'Cw',
                              'Cy', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'Dw', 'Ex', 'Fr', 'Ga',
                              'Hi', 'In', 'Lo', 'N1', 'Na', 'Ni', 'o', 'Pa', 'Ph', 'Pi', 'Po', 'Pr', 'Ri', 'Rn', 'Rv',
                              's', 'Sp', 'St', 'Tn', 'Za'}
    ok_pairs = {('Ni', 'Po'), ('Ni', 'Pa'), ('Ni', 'Wa'), ('Ph', 'Ri'), ('Lo', 'Va'), ('Ni', 'Va'), ('Lo', 'Po'),
                ('De', 'He'), ('De', 'Ni'), ('De', 'Po'), ('He', 'Ni'), ('He', 'Po'), ('Hi', 'In'), ('De', 'Lo'),
                ('Ic', 'Na'), ('Ic', 'Ni'), ('Ic', 'Va'), ('Na', 'Ni'), ('Na', 'Va'), ('As', 'Ni'), ('As', 'Va'),
                ('De', 'Na'), ('He', 'Na'), ('Na', 'Po'), ('Hi', 'Pr'), ('Ga', 'Hi'), ('Ag', 'Ni'), ('Na', 'Pi'),
                ('Ni', 'Oc'), ('Ag', 'Ga'), ("Ag", "Ri"), ("Ga", "Ni"), ("Ga", "Ri"), ("Ni", "Ri"), ("Ag", "Pi"),
                ("He", "Lo"), ("Ag", "Pr"), ("Ni", "Pr"), ("As", "Hi"), ("As", "In"), ("As", "Na"), ("Hi", "Na"),
                ("Hi", "Va"), ("In", "Na"), ("In", "Va"), ("De", "Ph"), ("De", "Pi"), ("He", "Ph"), ("He", "Pi"),
                ("Na", "Ph"), ("Ph", "Pi"), ("Ph", "Po"), ("Pi", "Po"), ("Ic", "Lo"), ("Fl", "He"), ("Fl", "Ni"),
                ("As", "Lo"), ("Pa", "Ph"), ("Pa", "Ri"), ("Pa", "Pi"), ("Hi", "Wa"), ("In", "Wa"), ("Ga", "Lo"),
                ("Ga", "Pa"), ("Ph", "Va"), ("Pi", "Va"), ("As", "Ph"), ("As", "Pi"), ("Ga", "Pr"), ("Ic", "Pi"),
                ("Ba", "Va"), ("Hi", "Po"), ("Hi", "Ic"), ("Ic", "In"), ("Fl", "Lo"), ("De", "Ri"), ("Pi", "Wa"),
                ("Ga", "Ph"), ("Ba", "Fl"), ("Ba", "Lo"), ("Ba", "Ni"), ("De", "Hi"), ("De", "In"), ("He", "Hi"),
                ("He", "In"), ("In", "Po"), ("Ph", "Wa"), ("Ri", "Wa"), ("Pr", "Wa"), ("Ba", "Wa"), ("Lo", "Ni"),
                ("Ic", "Ph"), ("Ba", "Po"), ("Lo", "Wa"), ("Ba", "De"), ("Fl", "Ph"), ("Oc", "Ri"), ("Lo", "Oc"),
                ("Fl", "Hi"), ("Fl", "In"), ("De", "Pr"), ("Oc", "Ph"), ("Oc", "Pi"), ("Hi", "Oc"), ("In", "Oc"),
                ("Oc", "Pr"), ("Ba", "Ic"), ("Ba", "He"), ("Ba", "Ga"), ("Ba", "Oc"), ("As", "Ba"), ("Ag", "Hi"),
                ("Ag", "D3"), ("De", "Va"), ("Ag", "In"), ("Fl", "Wa"), ("Hi", "Sp"), ("In", "Sp"), ("Po", "Pr"),
                ("Fl", "Pr"), ("Ic", "Wa"), ("Ba", "Bo"), ("Bo", "De"), ("Bo", "He"), ("Ba", "o"), ("Bo", "Lo"),
                ("Oc", "Wa"), ("Bo", "Fl"), ("Ag", "Cy"), ("Cy", "Ni"), ("Cy", "Fl"), ("Cy", "Pr"), ("Cy", "Po"),
                ("Cy", "He"), ("Cy", "Pi"), ("Cy", "Ri"), ("Cy", "Wa"), ("Cy", "Pa"), ("Cy", "Ph"), ("Cy", "De"),
                ("Ag", "Po"), ("As", "Cy"), ("Cy", "Na"), ("Cy", "Va"), ("Cy", "Ga"), ("Cy", "Ic"), ("Cy", "Hi"),
                ("Cy", "In"), ("Bo", "Ni"), ("Bo", "Va"), ("Cy", "Lo"), ("Ag", "Lo"), ("Hi", "s"), ("Ag", "Wa"),
                ("Hi", "Ri"), ("In", "Ri"), ("Ag", "Fl"), ("Lo", "Na"), ("Lo", "Ri"), ("Fl", "Ri"), ("In", "Lo"),
                ("Ag", "Va"), ("Na", "Wa"), ("Fl", "Na"), ("Ag", "C1"), ("C1", "Ni"), ("Dw", "Hi"), ("Dw", "Na"),
                ("Dw", "Po"), ("Ag", "St"), ("Ag", "Tn"), ("Ni", "St"), ("Ni", "Tn"), ("St", "Tn"), ("Ag", "C3"),
                ("C3", "Ni"), ("Lo", "St"), ("C0", "Lo"), ("C0", "Ni"), ("Ag", "C6"), ("C6", "Ni"), ("C1", "Fl"),
                ("D1", "Lo"), ("D1", "Ni"), ("C4", "Ni"), ("C4", "Po"), ("Ag", "D1"), ("D1", "Ri"), ("Ri", "Tn"),
                ("Hi", "St"), ("C5", "Po"), ("D3", "Ri"), ("D3", "Tn"), ("C1", "Lo"), ("C9", "Lo"), ("C9", "Ni"),
                ("C9", "Po"), ("D1", "Po"), ("Dw", "Lo"), ("Dw", "Ni"), ("Ag", "C9"), ("Ag", "C5"), ("Hi", "Tn"),
                ("C4", "Lo"), ("Ag", "Dw"), ("Lo", "Tn"), ("C1", "Wa"), ("C4", "Wa"), ("C9", "Na"), ("C9", "Va"),
                ("D0", "Ni"), ("Ag", "Cw"), ("Cw", "Ri"), ("D4", "Lo"), ("D4", "Ni"), ("C2", "Lo"), ("C2", "Ni"),
                ("C0", "Fl"), ("Cy", "Oc"), ("Hi", "Ni"), ("Hi", "Lo"), ("Va", "Wa"), ("Ba", "Na"), ("Na", "Ri"),
                ("De", "Fl"), ("As", "Po"), ("Ic", "Po"), ("Hi", "Za"), ("Pr", "Za"), ("Ag", "D0"), ("Cw", "Ni"),
                ("D4", "De"), ("Ag", "D7"), ("D7", "Ni"), ("D7", "Ri"), ("Ag", "C0"), ("Ag", "D8"), ("D8", "Ni"),
                ("D8", "Ri"), ("Hi", "Rn"), ("Ic", "Rn"), ("In", "Rn"), ("Rn", "Va"), ("C3", "Lo"), ("C3", "Hi"),
                ("Ag", "C2"), ("Fl", "Rv"), ("Lo", "Rv"), ("Ni", "Rv"), ("C2", "Hi"), ("D2", "Lo"), ("D2", "Ni"),
                ("D2", "Wa"), ("C8", "Ri"), ("C8", "Wa"), ("Ex", "Lo"), ("Ex", "Ni"), ("Ex", "Pr"), ("Lo", "Pr"),
                ("C2", "Ri"), ("D2", "Ri"), ("C7", "Ni"), ("D8", "Hi"), ("C2", "Po"), ("Ag", "C4"), ("D0", "Hi"),
                ("C0", "Hi"), ("C0", "Po"), ("C2", "Na"), ("C6", "Ri"), ("Po", "Wa"), ("Ag", "D2"), ("C1", "Ri"),
                ("D3", "Ni"), ("C5", "Ni"), ("Ag", "N1"), ("D6", "Ni"), }

    __slots__ = '__dict__', 'codeset', 'pcode', 'dcode', 'xcode'

    def __init__(self, initial_codes):
        """
        Constructor
        """
        self.logger = logging.getLogger('PyRoute.TradeCodes')
        self.codes = initial_codes.split()
        self.pcode = set(TradeCodes.pcodes) & set(self.codes)
        self.dcode = set(TradeCodes.dcodes) & set(self.codes)
        self.xcode = TradeCodes.ext_codes & set(self.codes)

        self.owned = [code for code in self.codes if code.startswith('O:') or code.startswith('C:')]

        self.homeworld_list = []
        self.sophont_list = []
        homeworlds_found = []

        self.sophont_list = [code for code in self.codes if re.match(r"[\w\']{4}(\d|W)", code, re.U)]

        for homeworld in re.findall(r"[Di]*\([^)]+\)\d?", initial_codes, re.U):
            full_name = re.sub(r'\(([^)]+)\)\d?', r'\1', homeworld)
            homeworlds_found.append(homeworld)
            match = re.match(r'\w{,2}\(([^)]{,4})[^)]*\)(\d|W)?', homeworld)
            if match is None:
                self.logger.error("Unable to process %s", initial_codes)
                sys.exit(1)
            if full_name.startswith("Di"):
                sophont = "{code: <4}{pop}".format(code=match.group(1), pop='X')
            else:
                sophont = "{code: <4}{pop}".format(code=match.group(1), pop=match.group(2) if match.group(2) else 'W')

            sophont = sophont.replace("'", "X")
            sophont = sophont.replace("!", "X")
            sophont = sophont.replace(" ", "X")
            self.sophont_list.append(sophont)
            self.homeworld_list.append(sophont)

        self.codeset = set(self.codes) - self.dcode - set(self.owned) - set(self.sophont_list)\
            - set(homeworlds_found) - self.xcode
        self.codeset = sorted(list(self.codeset))

        if len(self.pcode) > 0:
            self.pcode = sorted(list(self.pcode))[0]
        else:
            self.pcode = None

        self.owner = self.owners(None)
        self.colony = self.colonies(None)

        self.dcode = list(self.dcode) + self.colony + self.owner
        self.dcode = sorted(self.dcode)

    def _process_homeworld(self, homeworld, homeworlds_found, initial_codes):
        full_name = re.sub(r'\(([^)]+)\)\d?', r'\1', homeworld)
        homeworlds_found.append(homeworld)
        match = re.match(r'\w{,2}\(([^)]{,4})[^)]*\)(\d|W)?', homeworld)
        if match is None:
            self.logger.error("Unable to process %s", initial_codes)
            sys.exit(1)
        if full_name.startswith("Di"):
            sophont = "{code: <4}{pop}".format(code=match.group(1), pop='X')
        else:
            sophont = "{code: <4}{pop}".format(code=match.group(1), pop=match.group(2) if match.group(2) else 'W')
        sophont = sophont.replace("'", "X")
        sophont = sophont.replace("!", "X")
        sophont = sophont.replace(" ", "X")
        self.sophont_list.append(sophont)
        self.homeworld_list.append(sophont)
        self.codes = [code for code in self.codes if code != homeworld]

    def _process_major_race_homeworld(self, homeworld, homeworlds_found):
        """
        Homeworld processing using codes like [Solomani] - can make more assumptions than in the original case

        @type homeworld: string
        @type homeworlds_found: list
        """
        full_name = re.sub(r'\(([^)]+)\)\d?', r'\1', homeworld)
        homeworlds_found.append(homeworld)
        sophont = "{code: <4}{pop}".format(code=full_name[0:4], pop='W')
        sophont = sophont.replace("'", "X")
        sophont = sophont.replace("!", "X")
        sophont = sophont.replace(" ", "X")
        self.sophont_list.append(sophont)
        self.homeworld_list.append(sophont)
        self.codes = [code for code in self.codes if code != '[' + homeworld + "]"]

    def __str__(self):
        return " ".join(sorted(self.codes))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['logger']
        del state['ownedBy']
        return state

    def planet_codes(self):
        return " ".join(self.codeset)

    def calculate_pcode(self):
        return self.pcode

    def _check_planet_code(self, star, code, size, atmo, hydro):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        check = True
        if star.size in size and star.atmo in atmo and star.hydro in hydro \
                and code not in self.codeset:
            self.logger.error('{}-{} Calculated "{}" not in trade codes {}'.format(star, star.uwp, code, self.codeset))
            check = False
        if code in self.codeset and \
                not (star.size in size and star.atmo in atmo and star.hydro in hydro):
            self.logger.error('{}-{} Found invalid "{}" in trade codes: {}'.format(star, star.uwp, code, self.codeset))
            check = False
        return check

    def _check_pop_code(self, star, code, pop):
        check = True
        if star.pop in pop and code not in self.codeset:
            self.logger.error('{} - Calculated "{}" not in trade codes {}'.format(star, code, self.codeset))
            check = False
        if code in self.codeset and star.pop not in pop:
            self.logger.error(
                '{} - Found invalid "{}" code on world with {} population: {}'.format(star, code, star.pop,
                                                                                       self.codeset))
            check = False
        return check

    def _check_econ_code(self, star, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop
        check = True
        if star.atmo in atmo and star.hydro in hydro and star.pop in pop \
                and code not in self.codeset:
            self.logger.error('{}-{} Calculated "{}" not in trade codes {}'.format(star, star.uwp, code, self.codeset))
            check = False
        if code in self.codeset and \
                not (star.atmo in atmo and star.hydro in hydro and star.pop in pop):
            self.logger.error('{}-{} Found invalid "{}" in trade codes: {}'.format(star, star.uwp, code, self.codeset))
            check = False
        return check

    def check_world_codes(self, star):
        check = True
        check = self._check_planet_code(star, 'As', '0', '0', '0') and check
        check = self._check_planet_code(star, 'De', None, '23456789', '0') and check
        check = self._check_planet_code(star, 'Fl', None, 'ABC', '123456789A') and check
        check = self._check_planet_code(star, 'Ga', '678', '568', '567') and check
        check = self._check_planet_code(star, 'He', '3456789ABC', '2479ABC', '012') and check
        check = self._check_planet_code(star, 'Ic', None, '01', '123456789A') and check
        check = self._check_planet_code(star, 'Po', None, '2345', '0123') and check
        check = self._check_planet_code(star, 'Oc', 'ABCD', '3456789DEF', 'A') and check
        check = self._check_planet_code(star, 'Va', None, '0', None) and check
        check = self._check_planet_code(star, 'Wa', '3456789', '3456789DEF', 'A') and check

        # self._check_pop_code('Ba', '0')
        check = self._check_pop_code(star, 'Lo', '123') and check
        check = self._check_pop_code(star, 'Ni', '456') and check
        check = self._check_pop_code(star, 'Ph', '8') and check
        check = self._check_pop_code(star, 'Hi', '9ABCD') and check

        check = self._check_econ_code(star, 'Pa', '456789', '45678', '48') and check
        check = self._check_econ_code(star, 'Ag', '456789', '45678', '567') and check
        check = self._check_econ_code(star, 'Na', '0123', '0123', '6789ABCD') and check
        check = self._check_econ_code(star, 'Pi', '012479', None, '78') and check
        check = self._check_econ_code(star, 'In', '012479ABC', None, '9ABCD') and check
        check = self._check_econ_code(star, 'Pr', '68', None, '59') and check
        check = self._check_econ_code(star, 'Ri', '68', None, '678') and check
        return check

    def owned_by(self, star):
        self.ownedBy = star
        if star.gov == '6':
            self.ownedBy = None
        for code in self.dcode:
            if code.startswith('O:'):
                if len(code) == 2:
                    self.ownedBy = 'XXXX'
                else:
                    self.ownedBy = code[2:]
                break
            elif code.startswith('Mr'):
                self.ownedBy = 'Mr'
            elif code.startswith('Re'):
                self.ownedBy = 'Re'
            elif code.startswith('Px'):
                self.ownedBy = 'Px'
        if (star.gov == '6' and not self.ownedBy) or (star.gov != '6' and self.ownedBy != star):
            self.logger.debug("{} has incorrect government code {} - {}".format(star, star.gov, self.dcode))
        return self.ownedBy

    def owners(self, sector_name):
        if not sector_name:
            return [code for code in self.owned if code.startswith('O:')]
        else:
            return [code if len(code) > 6 else 'O:' + sector_name[0:4] + '-' + code[2:]
                    for code in self.owned if code.startswith('O:')]

    def colonies(self, sector_name):
        if not sector_name:
            return [code for code in self.owned if code.startswith('C:')]
        else:
            return [code if len(code) > 6 else 'C:' + sector_name[0:4] + '-' + code[2:]
                    for code in self.owned if code.startswith('C:')]

    @property
    def homeworld(self):
        return self.homeworld_list

    @property
    def sophonts(self):
        return self.sophont_list

    @property
    def rich(self):
        return 'Ri' in self.codeset

    @property
    def industrial(self):
        return 'In' in self.codeset

    @property
    def agricultural(self):
        return 'Ag' in self.codeset

    @property
    def poor(self):
        return 'Po' in self.codeset

    @property
    def nonagricultural(self):
        return 'Na' in self.codeset

    @property
    def barren(self):
        return 'Ba' in self.codeset or 'Di' in self.codeset

    @property
    def low(self):
        return 'Lo' in self.codeset

    @property
    def nonindustrial(self):
        return 'Ni' in self.codeset

    @property
    def high(self):
        return 'Hi' in self.codeset

    @property
    def asteroid(self):
        return 'As' in self.codeset

    @property
    def desert(self):
        return 'De' in self.codeset

    @property
    def fluid(self):
        return 'Fl' in self.codeset

    @property
    def vacuum(self):
        return 'Va' in self.codeset and 'As' not in self.codeset

    @property
    def waterworld(self):
        return 'Wa' in self.codeset or 'Oc' in self.codeset

    @property
    def extreme(self):
        return len(self.ex_codes & set(self.codeset)) > 0

    @property
    def capital(self):
        return 'Cp' in self.dcode or 'Cx' in self.dcode or 'Cs' in self.dcode

    @property
    def subsector_capital(self):
        return 'Cp' in self.dcode

    @property
    def sector_capital(self):
        return 'Cs' in self.dcode

    @property
    def other_capital(self):
        return 'Cx' in self.dcode

    @property
    def research_station(self):
        return set(self.research.keys()).intersection(self.dcode)

    @property
    def research_station_char(self):
        stations = self.research_station
        if len(stations) == 1:
            station = next(iter(self.research_station))
            return self.research[station]
        else:
            return None

    @property
    def pcode_color(self):
        return self.pcolor.get(self.pcode, '#44ff44')

    @property
    def low_per_capita_gwp(self):
        return self.extreme or self.poor or self.nonindustrial or self.low

    def is_well_formed(self):
        msg = ""
        for code in self.codeset:
            if not self._check_residual_code_well_formed(code):
                msg = "Residual code " + str(code) + " not in allowed residual list"
                return False, msg

        result, msg = self._check_code_pairs_allowed()

        return result, msg

    def trim_ill_formed_residual_codes(self):
        nu_set = set()
        for code in self.codeset:
            if not self._check_residual_code_well_formed(code):
                msg = "Residual code " + str(code) + " not in allowed residual list - removing"
                self.logger.warning(msg)
                self.codes = [topcode for topcode in self.codes if topcode != code]
            else:
                nu_set.add(code)
        self.codeset = sorted(list(nu_set))

    def _check_residual_code_well_formed(self, code):
        max_code_len = 12
        if code not in TradeCodes.ext_codes and code not in TradeCodes.ex_codes:
            if code in TradeCodes.weird_codes:
                return True

            open_brackets = code.count('(')
            close_brackets = code.count(')')
            if open_brackets != close_brackets:
                return False
            open_braces = code.count('{')
            close_braces = code.count('}')
            if open_braces != close_braces:
                return False
            open_squares = code.count('[')
            close_squares = code.count(']')
            if open_squares != close_squares:
                return False

            if len(code) > max_code_len:
                return False
            if code.startswith('Di(') or code.startswith('(') or code.endswith(')') or code.endswith(')?'):
                if ')' not in code:
                    return False
                return True
            if code not in TradeCodes.allowed_residual_codes:
                return False
        return True

    def _check_code_pairs_allowed(self):
        msg = ""

        sortset = sorted([code for code in self.codeset if code not in TradeCodes.weird_codes])
        outside = set()

        for code, other in itertools.combinations(sortset, 2):
            pair = (code, other) if code < other else (other, code)
            if pair not in TradeCodes.ok_pairs:
                outside.add(pair)

        if 0 < len(outside):
            msg = "Code pair(s)"
            for pair in outside:
                pairline = ' ("' + pair[0] + '", "' + pair[1] + '"),'
                msg += pairline
            msg = msg.strip(',')
            msg += " not in allowed list"
            return False, msg

        return True, msg
