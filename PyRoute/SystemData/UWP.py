"""
Created on Nov 21, 2023

@author: CyberiaResurrection

Along the lines of TradeCodes, pull all the UWP handling, checking, etc into one single class that _just_ does UWP,
rather than the multiple concerns the Star class has evolved to embody.
"""
import re

from PyRoute.SystemData.Utilities import Utilities


class UWP(object):
    # Port code, size, atmo, hydro, pop, gov, law, the all-important hyphen, then TL
    match_string = '^([A-HXYa-hxy\?])([0-9A-Fa-f\?])([0-9A-Fa-f\?])([0-9Aa])([0-9A-Fa-f\?])([0-9A-Za-z\?])([0-9A-Ja-j\?])-([0-9A-Za-z\?])'

    match = re.compile(match_string)

    # various limits
    flux = 5
    atmo_limit = 15
    hydro_limit = 10
    hydro_atm_mod = -4
    gov_limit = 15
    law_limit = 18
    tl_limit = 33

    def __init__(self, uwp_line):
        matches = UWP.match.match(uwp_line)
        if not matches:
            raise ValueError('Input UWP malformed')
        line = str(matches[0]).upper()
        self.port = line[0]
        self.size = line[1]
        self.atmo = line[2]
        self.hydro = line[3]
        self.pop = line[4]
        self.gov = line[5]
        self.law = line[6]
        self.tl = line[8]
        self.size_code = self._ehex_to_int(self.size)
        self.atmo_code = self._ehex_to_int(self.atmo)
        self.hydro_code = self._ehex_to_int(self.hydro)
        self.pop_code = self._ehex_to_int(self.pop)
        self.gov_code = self._ehex_to_int(self.gov)
        self.law_code = self._ehex_to_int(self.law)
        self.tl_code = self._ehex_to_int(self.tl)

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line

    @property
    def line(self):
        return str(self.port) + str(self.size) + str(self.atmo) + str(self.hydro) + str(self.pop) + str(self.gov) + str(self.law) + '-' + str(self.tl)

    def _regenerate_line(self):
        self.size_code = self._ehex_to_int(str(self.size))
        self.atmo_code = self._ehex_to_int(str(self.atmo))
        self.hydro_code = self._ehex_to_int(str(self.hydro))
        self.pop_code = self._ehex_to_int(str(self.pop))
        self.gov_code = self._ehex_to_int(str(self.gov))
        self.law_code = self._ehex_to_int(str(self.law))
        self.tl_code = self._ehex_to_int(str(self.tl))

    def is_well_formed(self):
        msg = ""
        rep = str(self)
        if 9 != len(rep):
            msg = "String representation wrong length"
            return False, msg
        if rep.islower():
            msg = "String representation not uppercased"
            return False, msg

        return True, msg

    @property
    def size_is_zero(self):
        return '?' != self.size and 0 == self.size_code

    def check_canonical(self):
        msg = []
        self._check_canonical_physicals(msg)
        self._check_canonical_socials(msg)
        self._check_canonical_tl(msg)

        return 0 == len(msg), msg

    def _check_canonical_physicals(self, msg):
        size_is_zero = self.size_is_zero
        if size_is_zero and 0 != self.atmo_code:
            line = 'UWP Calculated atmo "{}" does not match generated atmo {}'.format(str(self.atmo), 0)
            msg.append(line)
        if size_is_zero and 0 != self.hydro_code:
            line = 'UWP Calculated hydro "{}" does not match generated hydro {}'.format(str(self.hydro), 0)
            msg.append(line)
        if not size_is_zero and '?' != self.atmo:
            max_atmo, min_atmo = self._get_atmo_bounds()
            if not min_atmo <= self.atmo_code <= max_atmo:
                line = 'UWP Calculated atmo "{}" not in expected range {}-{}'.format(self.atmo, min_atmo, max_atmo)
                msg.append(line)
        if 1 == self.size_code:
            if 0 != self.hydro_code:
                line = 'UWP Calculated hydro "{}" does not match generated hydro {}'.format(str(self.hydro), 0)
                msg.append(line)
        elif not size_is_zero and '?' != self.atmo and '?' != self.hydro:
            max_hydro, min_hydro = self._get_hydro_bounds()
            if not min_hydro <= self.hydro_code <= max_hydro:
                line = 'UWP Calculated hydro "{}" not in expected range {}-{}'.format(self.hydro, min_hydro, max_hydro)
                msg.append(line)

    def _check_canonical_socials(self, msg):
        # For some reason, Lintsec treats gov code X as 0 _for TL calc_, so we need to do the same here
        if 'X' == self.gov:
            pass
        elif '?' != self.pop and '?' != self.gov:
            max_gov, min_gov = self._get_gov_bounds()
            if not min_gov <= self.gov_code <= max_gov:
                line = 'UWP Calculated gov "{}" not in expected range {}-{}'.format(self.gov, min_gov, max_gov)
                msg.append(line)

        if '?' != self.pop and '?' != self.law:
            max_law, min_law = self._get_law_bounds()
            if not min_law <= self.law_code <= max_law:
                line = 'UWP Calculated law "{}" not in expected range {}-{}'.format(self.law, min_law, max_law)
                msg.append(line)

    def _check_canonical_tl(self, msg):
        if '?' != self.tl:
            max_tl, min_tl = self._get_tl_bounds()
            if not min_tl <= self.tl_code <= max_tl:
                line = 'UWP Calculated TL "{}" not in expected range {}-{}'.format(self.tl, min_tl, max_tl)
                msg.append(line)

    def _get_hydro_bounds(self):
        # Mod is _already_ negative - it gets _added_ to the bounds!
        mod = UWP.hydro_atm_mod if 2 > self.atmo_code or 9 < self.atmo_code else 0
        min_hydro = max(0, self.atmo_code - UWP.flux + mod)
        max_hydro = min(UWP.hydro_limit, self.atmo_code + UWP.flux + mod)
        return max_hydro, min_hydro

    def _get_atmo_bounds(self):
        min_atmo = max(0, self.size_code - UWP.flux)
        max_atmo = min(UWP.atmo_limit, self.size_code + UWP.flux)
        return max_atmo, min_atmo

    def _get_gov_bounds(self):
        min_gov = max(0, self.pop_code - UWP.flux)
        max_gov = min(UWP.gov_limit, self.pop_code + UWP.flux)

        return max_gov, min_gov

    def _get_law_bounds(self):
        # Flux is doubled because gov is pop + flux, and law is then gov + flux
        min_law = max(0, self.pop_code - 2 * UWP.flux)
        max_law = min(UWP.law_limit, self.pop_code + 2 * UWP.flux)

        if str(self.gov) not in '?X':
            min_law = max(min_law, self.gov_code - UWP.flux)
            max_law = min(max_law, self.gov_code + UWP.flux)

        return max_law, min_law

    def _get_tl_bounds(self):
        mod = 0
        if self.gov in '01X':
            mod += 1
        elif 'D' == self.gov:
            mod -= 1
        if self.pop in '12345':
            mod += 1
        elif '9' == self.pop:
            mod += 2
        elif self.pop in 'ABCDEF':
            mod += 4
        if '9' == self.hydro:
            mod += 1
        elif 'A' == self.hydro:
            mod += 2
        if self.atmo in '0123ABCDEF':
            mod += 1
        if self.size in '01':
            mod += 2
        elif self.size in '234':
            mod += 1

        min_tl = max(mod + 1, 0)
        max_tl = min(UWP.tl_limit, mod + 6)

        return max_tl, min_tl

    def canonicalise(self):
        self._canonicalise_physicals()
        self._canonicalise_socials()
        self._canonicalise_tl()

    def _canonicalise_physicals(self):
        size_is_zero = self.size_is_zero
        if '0' == str(self.size) and '0' != str(self.atmo):
            self.atmo = '0'
        if '0' == str(self.size) and '0' != str(self.hydro):
            self.hydro = '0'
        if not size_is_zero and '?' != self.atmo:
            max_atmo, min_atmo = self._get_atmo_bounds()
            if self.atmo_code < min_atmo:
                self.atmo = self._int_to_ehex(min_atmo)
            elif self.atmo_code > max_atmo:
                self.atmo = self._int_to_ehex(max_atmo)
        self._regenerate_line()
        # Handle short-circuit values first, then (if needed) drop to the general case
        if '1' == str(self.size):
            if '0' != str(self.hydro):
                self.hydro = '0'

        elif not size_is_zero and '?' != self.atmo and '?' != self.hydro:
            max_hydro, min_hydro = self._get_hydro_bounds()
            if self.hydro_code < min_hydro:
                self.hydro = self._int_to_ehex(min_hydro)
            elif self.hydro_code > max_hydro:
                self.hydro = self._int_to_ehex(max_hydro)
        self._regenerate_line()

    def _canonicalise_socials(self):
        if 'X' == self.gov:
            pass
        elif '?' != self.pop and '?' != self.gov:
            max_gov, min_gov = self._get_gov_bounds()
            if self.gov_code < min_gov:
                self.gov = self._int_to_ehex(min_gov)
            elif self.gov_code > max_gov:
                self.gov = self._int_to_ehex(max_gov)

        self._regenerate_line()

        if '?' != self.pop and '?' != self.law:
            max_law, min_law = self._get_law_bounds()
            if self.law_code < min_law:
                self.law = self._int_to_ehex(min_law)
            elif self.law_code > max_law:
                self.law = self._int_to_ehex(max_law)

        self._regenerate_line()

    def _canonicalise_tl(self):
        if '?' != self.tl:
            max_tl, min_tl = self._get_tl_bounds()
            if self.tl_code < min_tl:
                self.tl = self._int_to_ehex(min_tl)
            elif self.tl_code > max_tl:
                self.tl = self._int_to_ehex(max_tl)

        self._regenerate_line()

    def _ehex_to_int(self, value):
        return Utilities.ehex_to_int(value)

    def _int_to_ehex(self, value):
        return Utilities.int_to_ehex(value)
