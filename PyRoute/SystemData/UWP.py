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

    def __init__(self, uwp_line):
        matches = UWP.match.match(uwp_line)
        if not matches:
            raise ValueError('Input UWP malformed')
        self.line = str(matches[0]).upper()
        self.port = self.line[0]
        self.size = self.line[1]
        self.atmo = self.line[2]
        self.hydro = self.line[3]
        self.pop = self.line[4]
        self.gov = self.line[5]
        self.law = self.line[6]
        self.tl = self.line[8]
        self._size_code = self._ehex_to_int(self.size)
        self._atmo_code = self._ehex_to_int(self.atmo)
        self._hydro_code = self._ehex_to_int(self.hydro)

    def __str__(self):
        return self.line

    def _regenerate_line(self):
        self.line = str(self.port) + str(self.size) + str(self.atmo) + str(self.hydro) + str(self.pop) + str(self.gov) + str(self.law) + '-' + str(self.tl)
        self._size_code = self._ehex_to_int(str(self.size))
        self._atmo_code = self._ehex_to_int(str(self.atmo))
        self._hydro_code = self._ehex_to_int(str(self.hydro))

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
        return '?' != self.size and 0 == self._size_code

    def check_canonical(self):
        msg = []
        self._check_canonical_physicals(msg)

        return 0 == len(msg), msg

    def _check_canonical_physicals(self, msg):
        size_is_zero = self.size_is_zero
        if size_is_zero and 0 != self._atmo_code:
            line = 'UWP Calculated atmo "{}" does not match generated atmo {}'.format(str(self.atmo), 0)
            msg.append(line)
        if size_is_zero and 0 != self._hydro_code:
            line = 'UWP Calculated hydro "{}" does not match generated hydro {}'.format(str(self.hydro), 0)
            msg.append(line)
        if not size_is_zero and '?' != self.atmo:
            max_atmo, min_atmo = self._get_atmo_bounds()
            if not min_atmo <= self._atmo_code <= max_atmo:
                line = 'UWP Calculated atmo "{}" not in expected range {}-{}'.format(self.atmo, min_atmo, max_atmo)
                msg.append(line)
        if 1 == self._size_code:
            if 0 != self._hydro_code:
                line = 'UWP Calculated hydro "{}" does not match generated hydro {}'.format(str(self.hydro), 0)
                msg.append(line)
        elif not size_is_zero and '?' != self.atmo and '?' != self.hydro:
            max_hydro, min_hydro = self._get_hydro_bounds()
            if not min_hydro <= self._hydro_code <= max_hydro:
                line = 'UWP Calculated hydro "{}" not in expected range {}-{}'.format(self.hydro, min_hydro, max_hydro)
                msg.append(line)

    def _get_hydro_bounds(self):
        # Mod is _already_ negative - it gets _added_ to the bounds!
        mod = UWP.hydro_atm_mod if 2 > self._atmo_code or 9 < self._atmo_code else 0
        min_hydro = max(0, self._atmo_code - UWP.flux + mod)
        max_hydro = min(UWP.hydro_limit, self._atmo_code + UWP.flux + mod)
        return max_hydro, min_hydro

    def _get_atmo_bounds(self):
        min_atmo = max(0, self._size_code - UWP.flux)
        max_atmo = min(UWP.atmo_limit, self._size_code + UWP.flux)
        return max_atmo, min_atmo

    def canonicalise(self):
        self._canonicalise_physicals()

    def _canonicalise_physicals(self):
        size_is_zero = self.size_is_zero
        if '0' == str(self.size) and '0' != str(self.atmo):
            self.atmo = '0'
        if '0' == str(self.size) and '0' != str(self.hydro):
            self.hydro = '0'
        if not size_is_zero and '?' != self.atmo:
            max_atmo, min_atmo = self._get_atmo_bounds()
            if self._atmo_code < min_atmo:
                self.atmo = self._int_to_ehex(min_atmo)
            elif self._atmo_code > max_atmo:
                self.atmo = self._int_to_ehex(max_atmo)
        self._regenerate_line()
        # Handle short-circuit values first, then (if needed) drop to the general case
        if '1' == str(self.size):
            if '0' != str(self.hydro):
                self.hydro = '0'

        elif not size_is_zero and '?' != self.atmo and '?' != self.hydro:
            max_hydro, min_hydro = self._get_hydro_bounds()
            if self._hydro_code < min_hydro:
                self.hydro = self._int_to_ehex(min_hydro)
            elif self._hydro_code > max_hydro:
                self.hydro = self._int_to_ehex(max_hydro)
        self._regenerate_line()

    def _ehex_to_int(self, value):
        return Utilities.ehex_to_int(value)

    def _int_to_ehex(self, value):
        return Utilities.int_to_ehex(value)
