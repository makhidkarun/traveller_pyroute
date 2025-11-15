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
    match_string = r'^([A-HXYa-hxy\?])([0-9A-Fa-f\?])([0-9A-Za-z\?])([0-9A-Za-z\?])([0-9A-Fa-f\?])([0-9A-Xa-x\?])([0-9A-Ka-k\?])-([0-9A-Za-z\?])'

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
        if line[5] not in Utilities.tax_rate:
            raise ValueError('Input UWP malformed')
        self._port = line[0]
        self._size = line[1]
        self._atmo = line[2]
        self._hydro = line[3]
        self._pop = line[4]
        self._gov = line[5]
        self._law = line[6]
        self._tl = line[8]

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line

    @property
    def line(self) -> str:
        return str(self.port) + str(self.size) + str(self.atmo) + str(self.hydro) + str(self.pop) + str(self.gov) + str(self.law) + '-' + str(self.tl)

    def is_well_formed(self) -> tuple[bool, str]:
        msg = ""
        rep = str(self)
        if 9 != len(rep):
            msg = "String representation wrong length"
            return False, msg

        return True, msg

    @property
    def size_is_zero(self) -> bool:
        return '?' != self.size and 0 == self.size_code

    @property
    def port(self) -> str:
        return self._port.upper()

    @port.setter
    def port(self, value) -> None:
        self._port = value

    @property
    def size(self) -> str:
        return self._size.upper()

    @size.setter
    def size(self, value) -> None:
        self._size = str(value)

    @property
    def size_code(self) -> int:
        return self._ehex_to_int(self._size)

    @size_code.setter
    def size_code(self, value) -> None:
        self._size = self._int_to_ehex(value)

    @property
    def atmo(self) -> str:
        return self._atmo.upper()

    @atmo.setter
    def atmo(self, value) -> None:
        self._atmo = str(value)

    @property
    def atmo_code(self) -> int:
        return self._ehex_to_int(self._atmo)

    @atmo_code.setter
    def atmo_code(self, value) -> None:
        self._atmo = self._int_to_ehex(value)

    @property
    def hydro(self) -> str:
        return self._hydro.upper()

    @hydro.setter
    def hydro(self, value) -> None:
        self._hydro = str(value)

    @property
    def hydro_code(self) -> int:
        return self._ehex_to_int(self._hydro)

    @hydro_code.setter
    def hydro_code(self, value) -> None:
        self._hydro = self._int_to_ehex(value)

    @property
    def pop(self) -> str:
        return self._pop.upper()

    @pop.setter
    def pop(self, value) -> None:
        self._pop = str(value)

    @property
    def pop_code(self) -> int:
        return self._ehex_to_int(self._pop)

    @pop_code.setter
    def pop_code(self, value) -> None:
        self._pop = self._int_to_ehex(value)

    @property
    def gov(self) -> str:
        return self._gov.upper()

    @gov.setter
    def gov(self, value) -> None:
        self._gov = str(value)

    @property
    def gov_code(self) -> int:
        return self._ehex_to_int(self._gov)

    @gov_code.setter
    def gov_code(self, value) -> None:
        self._gov = self._int_to_ehex(value)

    @property
    def law(self) -> str:
        return self._law.upper()

    @law.setter
    def law(self, value) -> None:
        self._law = str(value)

    @property
    def law_code(self) -> int:
        return self._ehex_to_int(self._law)

    @law_code.setter
    def law_code(self, value) -> None:
        self._law = self._int_to_ehex(value)

    @property
    def tl(self) -> str:
        return self._tl.upper()

    @tl.setter
    def tl(self, value) -> None:
        self._tl = str(value)

    @property
    def tl_code(self) -> int:
        return self._ehex_to_int(self._tl)

    @tl_code.setter
    def tl_code(self, value) -> None:
        self._tl = self._int_to_ehex(value)

    @property
    def oldskool(self) -> bool:
        return '?' in self.line

    def check_canonical(self) -> tuple[bool, list[str]]:
        msg: list[str] = []
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
        elif '?' != self.gov:
            max_gov, min_gov = self._get_gov_bounds()
            if not min_gov <= self.gov_code <= max_gov:
                line = 'UWP Calculated gov "{}" not in expected range {}-{}'.format(self.gov, min_gov, max_gov)
                msg.append(line)

        if ('?' != self.pop or '?' != self.gov) and '?' != self.law:
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
        min_gov = 0
        max_gov = UWP.gov_limit

        if '?' != self.pop:
            min_gov = max(min_gov, self.pop_code - UWP.flux)
            max_gov = min(max_gov, self.pop_code + UWP.flux)

        return max_gov, min_gov

    def _get_law_bounds(self):
        min_law = 0
        max_law = UWP.law_limit

        if '?' != self.pop:
            # Flux is doubled because gov is pop + flux, and law is then gov + flux
            min_law = max(min_law, self.pop_code - 2 * UWP.flux)
            max_law = min(max_law, self.pop_code + 2 * UWP.flux)

        if str(self.gov) not in '?X':
            min_law = max(min_law, self.gov_code - UWP.flux)
            max_law = min(max_law, self.gov_code + UWP.flux)

        return max_law, min_law

    def _get_tl_bounds(self):
        mod = 0
        if self.gov in '01X':  # pragma: no mutate
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

    def canonicalise(self) -> None:
        self._canonicalise_physicals()
        self._canonicalise_socials()
        self._canonicalise_tl()

    def _canonicalise_physicals(self):
        size_is_zero = self.size_is_zero
        if '0' == self.size:
            self.atmo_code = 0
            self.hydro_code = 0

        if not size_is_zero and '?' != self.atmo:
            max_atmo, min_atmo = self._get_atmo_bounds()
            self.atmo_code = max(min_atmo, min(max_atmo, self.atmo_code))

        # Handle short-circuit values first, then (if needed) drop to the general case
        if '1' == str(self.size):
            self.hydro_code = 0

        elif not size_is_zero and '?' != self.atmo and '?' != self.hydro:
            max_hydro, min_hydro = self._get_hydro_bounds()
            self.hydro_code = max(min_hydro, min(max_hydro, self.hydro_code))

    def _canonicalise_socials(self):
        if 'X' == self.gov:
            if 0 < self.pop_code:
                self.gov_code = 0
                max_gov, min_gov = self._get_gov_bounds()
                self.gov_code = max(min_gov, min(max_gov, self.gov_code))
        elif '?' != self.gov:
            max_gov, min_gov = self._get_gov_bounds()
            self.gov_code = max(min_gov, min(max_gov, self.gov_code))

        if ('?' != self.pop or '?' != self.gov) and '?' != self.law:
            max_law, min_law = self._get_law_bounds()
            self.law_code = max(min_law, min(max_law, self.law_code))

    def _canonicalise_tl(self):
        if '?' != self.tl:
            max_tl, min_tl = self._get_tl_bounds()
            self.tl_code = max(min_tl, min(max_tl, self.tl_code))

    def _ehex_to_int(self, value):
        return Utilities.ehex_to_int(value)

    def _int_to_ehex(self, value):
        return Utilities.int_to_ehex(value)
