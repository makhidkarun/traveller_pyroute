"""
Created on Oct 3, 2017

@author: tjoneslo
"""
import functools
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
              'RsA', 'RsB', 'RsG', 'RsD', 'RsE', 'RsZ', 'RsT', 'RsI', 'RsK', 'RsO',
              'Fr', 'Co', 'Tp', 'Ho', 'Tr', 'Tu',
              'Cm', 'Tw']
    ex_codes = {'As', 'Fl', 'Ic', 'De', 'Na', 'Va', 'Wa', 'He', 'Oc'}
    research = {'RsA': '\u0391', 'RsB': '\u0392', 'RsG': '\u0393',
                'RsD': '\u0394', 'RdE': '\u0395', 'RsO': '\u03A9', 'RsZ': '\u0396',
                'RsT': '\u0398', 'RsI': '\u0399', 'RsK': '\u039A'}
    pcolor = {'As': '#8E9397', 'De': '#d17533', 'Fl': '#e37dff', 'He': '#ff6f0c', 'Ic': '#A5F2F3',
              'Oc': '#0094ED', 'Po': '#6a986a', 'Va': '#c9c9c9', 'Wa': '#4abef4'}
    ext_codes = {'Lt', 'Ht', 'Lg', 'Hg'}
    weird_codes = {'{Anomaly}', '{Fuel}', '{Ringworld}', '{Rosette}'}
    allowed_residual_codes = {'Ag', 'Ba', 'Bo', 'Cl', 'Cw', 'Cy', 'Dw', 'Ex', 'Fr', 'Ga', 'Hi', 'In', 'Lo', 'N1', 'Na',
                              'Ni', 'o', 'Pa', 'Ph', 'Pi', 'Po', 'Pr', 'Ri', 'Rn', 'Rv', 's', 'Sp', 'St', 'Tn', 'Za'}
    # Whether any of these pairs are _permitted_ to occur together is _irrelevant_.  They _do_ occur together in the
    # TravellerMap raw data.
    ok_pairs = {
        ('Ag', 'Bo'), ('Ag', 'Cw'), ('Ag', 'Cy'), ('Ag', 'Dw'), ('Ag', 'Fl'), ('Ag', 'Ga'), ('Ag', 'Hi'), ('Ag', 'In'),
        ('Ag', 'Lo'), ('Ag', 'N1'), ('Ag', 'Ni'), ('Ag', 'Pi'), ('Ag', 'Po'), ('Ag', 'Pr'), ('Ag', 'Ri'), ('Ag', 'St'),
        ('Ag', 'Tn'), ('Ag', 'Va'), ('Ag', 'Wa'), ('As', 'Ba'), ('As', 'Bo'), ('As', 'Cy'), ('As', 'Hi'), ('As', 'Ic'),
        ('As', 'In'), ('As', 'Lo'), ('As', 'Na'), ('As', 'Ni'), ('As', 'Ph'), ('As', 'Pi'), ('As', 'Po'), ('As', 'Va'),
        ('Ba', 'Bo'), ('Ba', 'De'), ('Ba', 'Fl'), ('Ba', 'Ga'), ('Ba', 'He'), ('Ba', 'Ic'), ('Ba', 'Lo'), ('Ba', 'Na'),
        ('Ba', 'Ni'), ('Ba', 'Oc'), ('Ba', 'Po'), ('Ba', 'Va'), ('Ba', 'Wa'), ('Ba', 'o'), ('Bo', 'De'), ('Bo', 'Fl'),
        ('Bo', 'Ga'), ('Bo', 'He'), ('Bo', 'Hi'), ('Bo', 'Ic'), ('Bo', 'In'), ('Bo', 'Lo'), ('Bo', 'Na'), ('Bo', 'Ni'),
        ('Bo', 'Oc'), ('Bo', 'Pa'), ('Bo', 'Ph'), ('Bo', 'Pi'), ('Bo', 'Po'), ('Bo', 'Ri'), ('Bo', 'Va'), ('Cw', 'Ni'),
        ('Cw', 'Ri'), ('Cy', 'De'), ('Cy', 'Fl'), ('Cy', 'Ga'), ('Cy', 'He'), ('Cy', 'Hi'), ('Cy', 'Ic'), ('Cy', 'In'),
        ('Cy', 'Lo'), ('Cy', 'Na'), ('Cy', 'Ni'), ('Cy', 'Oc'), ('Cy', 'Pa'), ('Cy', 'Ph'), ('Cy', 'Pi'), ('Cy', 'Po'),
        ('Cy', 'Pr'), ('Cy', 'Ri'), ('Cy', 'Va'), ('Cy', 'Wa'), ('De', 'Fl'), ('De', 'He'), ('De', 'Hi'), ('De', 'Ic'),
        ('De', 'In'), ('De', 'Lo'), ('De', 'Na'), ('De', 'Ni'), ('De', 'Ph'), ('De', 'Pi'), ('De', 'Po'), ('De', 'Pr'),
        ('De', 'Ri'), ('De', 'Va'), ('Dw', 'Hi'), ('Dw', 'Lo'), ('Dw', 'Na'), ('Dw', 'Ni'), ('Dw', 'Po'), ('Ex', 'Lo'),
        ('Ex', 'Ni'), ('Ex', 'Pr'), ('Fl', 'He'), ('Fl', 'Hi'), ('Fl', 'In'), ('Fl', 'Lo'), ('Fl', 'Na'), ('Fl', 'Ni'),
        ('Fl', 'Oc'), ('Fl', 'Ph'), ('Fl', 'Pr'), ('Fl', 'Ri'), ('Fl', 'Rv'), ('Fl', 'Wa'), ('Ga', 'Hi'), ('Ga', 'Lo'),
        ('Ga', 'Ni'), ('Ga', 'Pa'), ('Ga', 'Ph'), ('Ga', 'Pr'), ('Ga', 'Ri'), ('He', 'Hi'), ('He', 'In'), ('He', 'Lo'),
        ('He', 'Na'), ('He', 'Ni'), ('He', 'Ph'), ('He', 'Pi'), ('He', 'Po'), ('Hi', 'Ic'), ('Hi', 'In'), ('Hi', 'Lo'),
        ('Hi', 'Na'), ('Hi', 'Ni'), ('Hi', 'Oc'), ('Hi', 'Po'), ('Hi', 'Pr'), ('Hi', 'Ri'), ('Hi', 'Rn'), ('Hi', 'Sp'),
        ('Hi', 'St'), ('Hi', 'Tn'), ('Hi', 'Va'), ('Hi', 'Wa'), ('Hi', 'Za'), ('Hi', 's'), ('Ic', 'In'), ('Ic', 'Lo'),
        ('Ic', 'Na'), ('Ic', 'Ni'), ('Ic', 'Ph'), ('Ic', 'Pi'), ('Ic', 'Po'), ('Ic', 'Rn'), ('Ic', 'Va'), ('Ic', 'Wa'),
        ('In', 'Lo'), ('In', 'Na'), ('In', 'Oc'), ('In', 'Po'), ('In', 'Ri'), ('In', 'Rn'), ('In', 'Sp'), ('In', 'Va'),
        ('In', 'Wa'), ('Lo', 'Na'), ('Lo', 'Ni'), ('Lo', 'Oc'), ('Lo', 'Po'), ('Lo', 'Pr'), ('Lo', 'Ri'), ('Lo', 'Rv'),
        ('Lo', 'St'), ('Lo', 'Tn'), ('Lo', 'Va'), ('Lo', 'Wa'), ('Na', 'Ni'), ('Na', 'Ph'), ('Na', 'Pi'), ('Na', 'Po'),
        ('Na', 'Ri'), ('Na', 'Va'), ('Na', 'Wa'), ('Ni', 'Oc'), ('Ni', 'Pa'), ('Ni', 'Po'), ('Ni', 'Pr'), ('Ni', 'Ri'),
        ('Ni', 'Rv'), ('Ni', 'St'), ('Ni', 'Tn'), ('Ni', 'Va'), ('Ni', 'Wa'), ('Oc', 'Ph'), ('Oc', 'Pi'), ('Oc', 'Pr'),
        ('Oc', 'Ri'), ('Oc', 'Wa'), ('Pa', 'Ph'), ('Pa', 'Pi'), ('Pa', 'Ri'), ('Ph', 'Pi'), ('Ph', 'Po'), ('Ph', 'Ri'),
        ('Ph', 'Va'), ('Ph', 'Wa'), ('Pi', 'Po'), ('Pi', 'Va'), ('Pi', 'Wa'), ('Po', 'Pr'), ('Po', 'Va'), ('Po', 'Wa'),
        ('Pr', 'Wa'), ('Pr', 'Za'), ('Ri', 'Tn'), ('Ri', 'Wa'), ('Rn', 'Va'), ('St', 'Tn'), ('Va', 'Wa')
    }

    # Search regexen
    search = re.compile(r'\w{,2}\(([^)]{,4})[^)]*\)(\d|W|\?)?')
    search_major = re.compile(r'\w{,2}\[([^)]{,4})[^)]*\](\d|W|\?)?')
    sophont = re.compile(r"[A-Za-z\'!]{1}[\w\'!]{2,4}(\d|W|\?)")
    dieback = re.compile(r"[Di]*\([^)]+\)\d?")

    __slots__ = '__dict__', 'codeset', 'pcode', 'dcode', 'xcode'

    def __init__(self, initial_codes):
        """
        Constructor
        """
        self.logger = logging.getLogger('PyRoute.TradeCodes')
        self.codes, initial_codes = self._preprocess_initial_codes(initial_codes)
        self.pcode = set(TradeCodes.pcodes) & set(self.codes)
        self.dcode = set(TradeCodes.dcodes) & set(self.codes)
        self.xcode = TradeCodes.ext_codes & set(self.codes)

        self.owned = [code for code in self.codes if code.startswith('O:') or code.startswith('C:')]

        homeworlds_found = self._process_sophonts_and_homeworlds(initial_codes)

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

        self.trim_ill_formed_residual_codes()

    def _process_sophonts_and_homeworlds(self, initial_codes):
        self.homeworld_list = []
        self.sophont_list = []
        homeworlds_found = []
        self.sophont_list = [code for code in self.codes if TradeCodes.sophont.match(code)]
        # Trim out overly-long values from sophont_list and return them to codeset later on
        self.sophont_list = [code for code in self.sophont_list if 5 >= len(code)]
        homeworld_matches = TradeCodes.dieback.findall(initial_codes)
        # bolt on direct [homeworld] candidates
        homeworld_major = [item for item in self.codes if item.startswith('[') and 1 == item.count('[') and 1 == item.count(']')]
        deadworlds = [item for item in self.codes if 5 == len(item) and 'X' == item[4]]
        for homeworld in homeworld_matches:
            self._process_homeworld(homeworld, homeworlds_found, initial_codes)
        for homeworld in homeworld_major:
            self._process_major_race_homeworld(homeworld, homeworlds_found)
        for deadworld in deadworlds:
            self._process_deadworld(deadworld, homeworlds_found)
        return homeworlds_found

    def _preprocess_initial_codes(self, initial_codes):
        raw_codes = initial_codes.split()
        # look for successive codes that should be part of the same name (eg  "(Carte" , then "Blanche)", becoming
        # "(Carte Blanche)", and bolt them together
        num_codes = len(raw_codes)
        codes = []
        for i in range(0, num_codes):
            raw = raw_codes[i]
            # Filter duplicates
            if raw in codes:
                continue
            if '' == raw:
                continue
            if ')' == raw:
                continue
            if raw.startswith('Di('):
                if not raw.endswith(')') and i < num_codes - 1:
                    next = raw_codes[i + 1]
                    if next.endswith(')'):
                        combo = raw + ' ' + next
                        codes.append(combo)
                        raw_codes[i + 1] = ''
                else:
                    codes.append(raw)
                continue
            if 7 < len(raw) and '(' == raw[0] and ')' == raw[-2]:  # Let older-style sophont codes through
                codes.append(raw)
                continue
            if 7 < len(raw) and '[' == raw[0] and ']' == raw[-2]:  # Let older-style sophont codes through
                codes.append(raw)
                continue
            if 2 == len(raw) and ('W' == raw[1] or raw[1].isdigit()):
                if 'C' == raw[0]:  # Compact chirper population
                    pop = raw[1]
                    codes.append('Chir' + pop)
                    continue
                if 'D' == raw[0]:  # Compact Droyne population
                    pop = raw[1]
                    codes.append('Droy' + pop)
                    continue
            if not raw.startswith('(') and '(' in raw and raw.endswith(')'):
                continue
            if not raw.endswith(')') and ')' in raw and raw.startswith('(') and 7 > len(raw):
                continue
            if not raw.startswith('(') and not raw.endswith(')') and '(' in raw and ')' in raw:
                continue
            if 7 == len(raw) and '(' == raw[0] and ')' == raw[5]:  # Let preprocessed sophont codes through
                codes.append(raw)
                continue
            if not raw.startswith('(') and not raw.startswith('['):  # this isn't a sophont code
                codes.append(raw)
                continue
            if raw.endswith(')') or raw.endswith(']'):  # this _is_ a sophont code
                if raw.startswith('[') and raw.endswith(']'):
                    raw = self._trim_overlong_homeworld_code(raw)  # trim overlong _major_ race homeworld
                elif raw.startswith('(') and raw.endswith(')'):
                    raw = self._trim_overlong_homeworld_code(raw)  # trim overlong _minor_ race homeworld
                codes.append(raw)
                continue
            if i < num_codes - 1:
                next = raw_codes[i + 1]
                if next.endswith(')') or next.endswith(']'):
                    combo = raw + ' ' + next
                    codes.append(combo)
                    raw_codes[i + 1] = ''
                continue

        codes = sorted(codes)

        initial_codes = ' '.join(codes)

        return codes, initial_codes

    def _trim_overlong_homeworld_code(self, raw):
        # We're assuming raw is a (homeworld) code - not handling pop codes at the moment
        # If the homeworld string itself exceeds 35 characters in length, it will jam up against the left side of
        # the importance code in the starline, which both looks ugly and causes re-parsing havoc.
        left_bracket = raw[0]
        right_bracket = ']' if '[' == left_bracket else ')'

        trim = raw[1:-1]
        if 35 < len(trim):
            trim = trim[0:35]

        return left_bracket + trim + right_bracket

    def _process_homeworld(self, homeworld, homeworlds_found, initial_codes):
        full_name = re.sub(r'\(([^)]+)\)\d?', r'\1', homeworld)

        homeworlds_found.append(homeworld)
        match = TradeCodes.search.match(homeworld)
        if match is None:  # try again with major-raceversion
            match = TradeCodes.search_major.match(homeworld)
        if match is None:
            self.logger.error("Unable to process %s", initial_codes)
            sys.exit(1)
        if full_name.startswith("Di"):
            code = match.group(1)
            pop = 'X'
        else:
            code = match.group(1)
            pop = match.group(2) if match.group(2) else 'W'
            if homeworld + '?' in initial_codes:
                homeworld += "?"
                pop = '0'
            elif homeworld + 'X' in initial_codes:
                pop = 'X'
                homeworld += str(pop)
            elif homeworld + str(pop) in initial_codes:
                homeworld += str(pop)
        self._process_sophont_homeworld(code, pop, full_name=full_name)

    def _process_major_race_homeworld(self, homeworld, homeworlds_found):
        """
        Homeworld processing using codes like [Solomani] - can make more assumptions than in the original case

        @type homeworld: string
        @type homeworlds_found: list
        """
        full_name = re.sub(r'\[([^)]+)\][\d|W]?', r'\1', homeworld)
        pop = 'W' if ']' == homeworld[-1] else homeworld[-1]
        homeworlds_found.append(homeworld)
        code = full_name[0:4]
        self._process_sophont_homeworld(code, pop, full_name=full_name)

    def _process_deadworld(self, deadworld, homeworlds_found):
        full_name = re.sub(r'\(([^)]+)\)\d?', r'\1', deadworld)
        homeworlds_found.append(deadworld)
        code = full_name[0:4]
        pop = 'X'
        self._process_sophont_homeworld(code, pop, full_name=full_name)

    def _process_sophont_homeworld(self, code, pop, full_name=None):
        sophont = "{code: <4}{pop}".format(code=code, pop=pop)
        sophont = sophont.replace("'", "X")
        sophont = sophont.replace("!", "X")
        sophont = sophont.replace(" ", "X")
        self.sophont_list.append(sophont)
        self.homeworld_list.append(full_name)

        return sophont

    def __str__(self):
        return " ".join(sorted(self.codes))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['logger']
        del state['ownedBy']
        return state

    def __deepcopy__(self, memodict={}):
        state = self.__dict__.copy()

        foo = TradeCodes('')
        for key in state:
            item = state[key]
            setattr(foo, key, item)

        return foo

    def planet_codes(self):
        return " ".join(self.codeset)

    def calculate_pcode(self):
        return self.pcode

    def _check_planet_code(self, star, code, size, atmo, hydro, listmsg=None):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        star_match = star.size in size and star.atmo in atmo and star.hydro in hydro
        code_match = code in self.codeset
        if star_match == code_match:
            return True
        msg = None
        if star_match and not code_match:
            msg = '{}-{} Calculated "{}" not in trade codes {}'.format(star, str(star.uwp), code, self.codeset)
        if code_match and not star_match:
            msg = '{}-{} Found invalid "{}" in trade codes: {}'.format(star, str(star.uwp), code, self.codeset)
        if isinstance(listmsg, list):
            listmsg.append(msg)
        else:
            self.logger.error(msg)
        return False

    def _check_pop_code(self, star, code, pop, listmsg=None):
        star_match = star.pop in pop
        code_match = code in self.codeset
        if star_match == code_match:
            return True
        msg = None
        if star_match and not code_match:
            msg = '{} - Calculated "{}" not in trade codes {}'.format(star, code, self.codeset)

        if code_match and not star_match:
            msg = '{} - Found invalid "{}" code on world with {} population: {}'.format(star, code, star.pop,
                                                                                       self.codeset)
        if isinstance(listmsg, list):
            listmsg.append(msg)
        else:
            self.logger.error(msg)
        return False

    def _check_econ_code(self, star, code, atmo, hydro, pop, listmsg=None):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop
        star_match = star.atmo in atmo and star.hydro in hydro and star.pop in pop
        code_match = code in self.codeset
        if star_match == code_match:
            return True
        msg = None
        if star_match and not code_match:
            msg = '{}-{} Calculated "{}" not in trade codes {}'.format(star, str(star.uwp), code, self.codeset)
        if code_match and not star_match:
            msg = '{}-{} Found invalid "{}" in trade codes: {}'.format(star, str(star.uwp), code, self.codeset)
        self.logger.error(msg)
        if isinstance(listmsg, list):
            listmsg.append(msg)
        else:
            self.logger.error(msg)
        return False

    def check_world_codes(self, star, msg=None, fix_pop=False):
        is_list = isinstance(msg, list)
        msg = msg if is_list else None

        check = True
        if fix_pop is True:
            self._fix_all_pop_codes(star)

        check = self._check_planet_code(star, 'As', '0', '0', '0', msg) and check
        check = self._check_planet_code(star, 'De', None, '23456789', '0', msg) and check
        check = self._check_planet_code(star, 'Fl', None, 'ABC', '123456789A', msg) and check
        check = self._check_planet_code(star, 'Ga', '678', '568', '567', msg) and check
        check = self._check_planet_code(star, 'He', '3456789ABC', '2479ABC', '012', msg) and check
        check = self._check_planet_code(star, 'Ic', None, '01', '123456789A', msg) and check
        check = self._check_planet_code(star, 'Po', None, '2345', '0123', msg) and check
        check = self._check_planet_code(star, 'Oc', 'ABCD', '3456789DEF', 'A', msg) and check
        check = self._check_planet_code(star, 'Va', None, '0', None, msg) and check
        check = self._check_planet_code(star, 'Wa', '3456789', '3456789DEF', 'A', msg) and check

        if fix_pop is not True:
            check = self._check_all_pop_codes(check, msg, star)

        check = self._check_econ_code(star, 'Pa', '456789', '45678', '48', msg) and check
        check = self._check_econ_code(star, 'Ag', '456789', '45678', '567', msg) and check
        check = self._check_econ_code(star, 'Na', '0123', '0123', '6789ABCD', msg) and check
        check = self._check_econ_code(star, 'Pi', '012479', None, '78', msg) and check
        check = self._check_econ_code(star, 'In', '012479ABC', None, '9ABCD', msg) and check
        check = self._check_econ_code(star, 'Pr', '68', None, '59', msg) and check
        check = self._check_econ_code(star, 'Ri', '68', None, '678', msg) and check
        if is_list:
            return msg
        return check

    def _check_all_pop_codes(self, check, msg, star):
        check = self._check_pop_code(star, 'Ba', '0', msg) and check
        check = self._check_pop_code(star, 'Lo', '123', msg) and check
        check = self._check_pop_code(star, 'Ni', '456', msg) and check
        check = self._check_pop_code(star, 'Ph', '8', msg) and check
        check = self._check_pop_code(star, 'Hi', '9ABCD', msg) and check
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

    @functools.cached_property
    def homeworld(self):
        return sorted(self.homeworld_list)

    @functools.cached_property
    def sophonts(self):
        return sorted(self.sophont_list)

    @functools.cached_property
    def rich(self):
        return 'Ri' in self.codeset

    @functools.cached_property
    def industrial(self):
        return 'In' in self.codeset

    @functools.cached_property
    def agricultural(self):
        return 'Ag' in self.codeset

    @functools.cached_property
    def needs_agricultural(self):
        return self.nonagricultural or self.extreme

    @functools.cached_property
    def poor(self):
        return 'Po' in self.codeset

    @functools.cached_property
    def nonagricultural(self):
        return 'Na' in self.codeset

    @functools.cached_property
    def barren(self):
        return 'Ba' in self.codeset or 'Di' in self.codeset

    @functools.cached_property
    def low(self):
        return 'Lo' in self.codeset

    @functools.cached_property
    def nonindustrial(self):
        return 'Ni' in self.codeset

    @functools.cached_property
    def high(self):
        return 'Hi' in self.codeset

    @functools.cached_property
    def asteroid(self):
        return 'As' in self.codeset

    @functools.cached_property
    def desert(self):
        return 'De' in self.codeset

    @functools.cached_property
    def fluid(self):
        return 'Fl' in self.codeset

    @functools.cached_property
    def vacuum(self):
        return 'Va' in self.codeset and 'As' not in self.codeset

    @functools.cached_property
    def waterworld(self):
        return 'Wa' in self.codeset or 'Oc' in self.codeset

    @functools.cached_property
    def extreme(self):
        return len(self.ex_codes & set(self.codeset)) > 0

    @functools.cached_property
    def capital(self):
        return 'Cp' in self.dcode or 'Cx' in self.dcode or 'Cs' in self.dcode

    @functools.cached_property
    def subsector_capital(self):
        return 'Cp' in self.dcode

    @functools.cached_property
    def sector_capital(self):
        return 'Cs' in self.dcode

    @functools.cached_property
    def other_capital(self):
        return 'Cx' in self.dcode

    @functools.cached_property
    def research_station(self):
        return set(self.research.keys()).intersection(self.dcode)

    @functools.cached_property
    def research_station_char(self):
        stations = self.research_station
        if len(stations) == 1:
            station = next(iter(self.research_station))
            return self.research[station]
        else:
            return None

    @functools.cached_property
    def pcode_color(self):
        return self.pcolor.get(self.pcode, '#44ff44')

    @functools.cached_property
    def low_per_capita_gwp(self):
        return self.extreme or self.poor or self.nonindustrial or self.low

    def match_ag_codes(self, code):
        return (self.agricultural and code.needs_agricultural) or (self.needs_agricultural and code.agricultural)

    def match_in_codes(self, code):
        return (self.industrial and code.nonindustrial) or (self.nonindustrial and code.industrial)

    def is_well_formed(self):
        msg = ""
        for code in self.codeset:
            if not self._check_residual_code_well_formed(code):
                msg = "Residual code " + str(code) + " not in allowed residual list"
                return False, msg

        # Check no duplicate codes
        codes_set = set(self.codes)
        if len(self.codes) != len(codes_set):
            msg = "At least one trade code duplicated"
            return False, msg

        research_stations = [code for code in self.codes if code.startswith('Rs')]
        if 1 < len(research_stations):
            msg = "At most one research station allowed"
            return False, msg

        result, msg = self._check_code_pairs_allowed()

        # now check that sophont list is well-formed
        bad_sophonts = [code for code in self.sophont_list if 5 < len(code)]
        if 0 < len(bad_sophonts):
            msg = "Sophont codes must be no more than 5 chars each - got at least " + bad_sophonts[0]
            return False, msg

        # explicitly exclude multiple W-pop (ie, 95+%) sophonts
        big_sophs = [code for code in self.sophont_list if code.endswith('W')]
        if 1 < len(big_sophs):
            sophs = ' '.join(big_sophs)
            msg = "Can have at most one W-pop sophont.  Have " + sophs
            return False, msg

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
        max_sophont_len = 35
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

            if code.startswith('['):
                if len(code) > max_sophont_len:
                    return False
                return True
            elif len(code) > max_code_len:
                return False

            if len(code) > max_code_len or (code.startswith('[') and len(code) > max_sophont_len):
                return False
            if code.startswith('Di(') or code.startswith('(') or code.endswith(')') or code.endswith(')?'):  # minor race homeworld
                if ')' not in code:
                    return False
                return True
            if code.startswith('[') and (code.endswith(']') or ']' == code[-2]):  # major race homeworld
                if ']' not in code:
                    return False
                return True
            if code not in TradeCodes.allowed_residual_codes:
                return False
        return True

    def _check_code_pairs_allowed(self):
        msg = ""

        # Exclude weird codes, sophont codes and military rule straight-up
        sortset = sorted([code for code in self.codeset if code not in TradeCodes.weird_codes and code[0] not in '([' and not code.startswith('Mr')])
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

    def check_canonical(self, star):
        msg = []
        self.check_world_codes(star, msg)

        return 0 == len(msg), msg

    def canonicalise(self, star):
        self._fix_trade_code(star, 'As', '0', '0', '0')
        self._fix_trade_code(star, 'Ic', None, '01', '123456789A')
        self._fix_trade_code(star, 'De', '0123456789ABC', '23456789', '0')
        self._fix_trade_code(star, 'Po', None, '2345', '0123')
        self._fix_trade_code(star, 'Fl', None, 'ABC', '123456789A')
        self._fix_trade_code(star, 'He', '3456789ABC', '2479ABC', '012')
        self._fix_trade_code(star, 'Wa', '3456789', '3456789DEF', 'A')
        self._fix_trade_code(star, 'Ga', '678', '568', '567')
        self._fix_trade_code(star, 'Oc', 'ABCD', '3456789DEF', 'A')
        self._fix_trade_code(star, 'Va', None, '0', None)

        self._fix_econ_code(star, 'Na', '0123', '0123', '6789ABCD')
        self._fix_econ_code(star, 'Pi', '012479', None, '78')
        self._fix_econ_code(star, 'Pa', '456789', '45678', '48')
        self._fix_econ_code(star, 'Ag', '456789', '45678', '567')
        self._fix_econ_code(star, 'Pr', '68', None, '59')
        self._fix_econ_code(star, 'In', '012479ABC', None, '9ABCD')
        self._fix_econ_code(star, 'Ri', '68', None, '678')

        self._fix_all_pop_codes(star)

    def _fix_trade_code(self, star, code, size, atmo, hydro):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro

        code_match = code in self.codeset
        system_match = star.size in size and star.atmo in atmo and star.hydro in hydro
        if code_match == system_match:
            return

        if code_match and not system_match:
            self._drop_invalid_trade_code(code)
        elif system_match and not code_match:
            self._add_missing_trade_code(code)

    def _fix_econ_code(self, star, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABCD' if pop is None else pop

        code_match = code in self.codeset
        phys_match = star.atmo in atmo and star.hydro in hydro and star.pop in pop

        if code_match == phys_match:
            return

        if code_match and not phys_match:
            self._drop_invalid_trade_code(code)
        elif phys_match and not code_match:
            self._add_missing_trade_code(code)

    def _fix_pop_code(self, star, code, pop):
        pop_match = star.pop in pop
        code_match = code in self.codeset

        if pop_match == code_match:
            return

        if code_match and not pop_match:
            self._drop_invalid_trade_code(code)
        elif pop_match and not code_match:
            self._add_missing_trade_code(code)

    def _fix_all_pop_codes(self, star):
        self._fix_pop_code(star, 'Ba', '0')
        self._fix_pop_code(star, 'Lo', '123')
        self._fix_pop_code(star, 'Ni', '456')
        self._fix_pop_code(star, 'Ph', '8')
        self._fix_pop_code(star, 'Hi', '9ABCD')

    def _drop_invalid_trade_code(self, targcode):
        self.codes = [code for code in self.codes if code != targcode]
        self.codeset = [code for code in self.codeset if code != targcode]

    def _add_missing_trade_code(self, targcode):
        self.codes.append(targcode)
        self.codeset.append(targcode)