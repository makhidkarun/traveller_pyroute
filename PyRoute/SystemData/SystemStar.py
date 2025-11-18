"""
Created on Nov 23, 2023

@author: CyberiaResurrection

"""
from typing import Optional


class SystemStar(object):

    sizes = ["Ia", "Ib", "II", "III", "IV", "V", "VI", "D", "NS", "PSR", "BH", "BD"]
    starsizes = ["Ia", "Ib", "II", "III", "IV", "V", "VI", "D"]
    spectrals = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    supersizes = ['Ia', 'Ib']

    star_fluxen = {
        'O': {-6: 'Ia', -5: 'Ia', -4: 'Ib', -3: 'II', -2: 'III', -1: 'III', 0: 'III', 1: 'V', 2: 'V', 3: 'V', 4: 'IV', 5: 'D', 6: 'IV', 7: 'IV', 8: 'IV'},
        'B': {-6: 'Ia', -5: 'Ia', -4: 'Ib', -3: 'II', -2: 'III', -1: 'III', 0: 'III', 1: 'III', 2: 'V', 3: 'V', 4: 'IV',
              5: 'D', 6: 'IV', 7: 'IV', 8: 'IV'},
        'A': {-6: 'Ia', -5: 'Ia', -4: 'Ib', -3: 'II', -2: 'III', -1: 'IV', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'V',
              5: 'D', 6: 'V', 7: 'V', 8: 'V'},
        'F0-4': {-6: 'II', -5: 'II', -4: 'III', -3: 'IV', -2: 'V', -1: 'V', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'V',
              5: 'D', 6: 'V', 7: 'V', 8: 'V'},
        'F5-9': {-6: 'II', -5: 'II', -4: 'III', -3: 'IV', -2: 'V', -1: 'V', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'VI',
              5: 'D', 6: 'VI', 7: 'VI', 8: 'VI'},
        'G': {-6: 'II', -5: 'II', -4: 'III', -3: 'IV', -2: 'V', -1: 'V', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'VI',
              5: 'D', 6: 'VI', 7: 'VI', 8: 'VI'},
        'K': {-6: 'II', -5: 'II', -4: 'III', -3: 'IV', -2: 'V', -1: 'V', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'VI',
              5: 'D', 6: 'VI', 7: 'VI', 8: 'VI'},
        'M': {-6: 'II', -5: 'II', -4: 'II', -3: 'II', -2: 'III', -1: 'V', 0: 'V', 1: 'V', 2: 'V', 3: 'V', 4: 'VI',
              5: 'D', 6: 'VI', 7: 'VI', 8: 'VI'}
    }

    def __init__(self, size, spectral=None, digit=None):
        self.size = size
        self.spectral = spectral
        self.digit = digit
        if 'VII' == self.size:  # Reclassify archaic degenerate dwarfs as plain dwarfs
            self.size = 'D'

    def __str__(self):
        if self.spectral is None or self.digit is None:
            return self.size
        return self.spectral + str(self.digit) + ' ' + self.size

    @property
    def is_stellar(self) -> bool:
        return self.size in SystemStar.starsizes

    @property
    def is_stellar_not_dwarf(self) -> bool:
        return self.is_stellar and self.size != 'D'

    @property
    def is_supergiant(self) -> bool:
        return self.size in SystemStar.supersizes

    def is_bigger(self, other) -> bool:
        if self.size != other.size:
            return SystemStar.sizes.index(self.size) < SystemStar.sizes.index(other.size)  # pragma: no mutate
        if self.spectral is None or other.spectral is None:
            return True
        if self.spectral != other.spectral:
            return SystemStar.spectrals.index(self.spectral) < SystemStar.spectrals.index(other.spectral)  # pragma: no mutate
        if self.digit is None or other.digit is None:
            return True
        if self.digit != other.digit:
            return self.digit < other.digit  # pragma: no mutate
        return True

    def check_canonical(self) -> tuple[bool, list[str]]:
        msg = []

        # Most of these checks are implied by the "Spectral Type And Size" table on p28 of T5.10 Book 3
        if self.is_stellar_not_dwarf and (self.spectral not in ['O', 'B', 'A'] and self.size in ['Ia', 'Ib']):
            line = "Only OBA class stars can be supergiants (Ia/Ib), not " + str(self)
            msg.append(line)
        if 'D' == self.size and self.spectral is not None and self.digit is not None:
            line = "D-size stars with non-empty spectral class _and_ spectral decimal should be V-size, not " + str(self)
            msg.append(line)
        if 'VI' == self.size and self.spectral in ['O', 'B', 'A']:
            line = "OBA class stars cannot be size VI, is " + str(self)
            msg.append(line)
        if 'VI' == self.size and 'F' == self.spectral and str(self.digit) in ['0', '1', '2', '3', '4']:
            line = "F0-F4 class stars cannot be size VI, is " + str(self)
            msg.append(line)
        if 'IV' == self.size and 'M' == self.spectral:
            line = "M class stars cannot be size IV, is " + str(self)
            msg.append(line)
        if 'IV' == self.size and 'K' == self.spectral and str(self.digit) in ['5', '6', '7', '8', '9']:
            line = "K5-K9 class stars cannot be size IV, is " + str(self)
            msg.append(line)

        return 0 == len(msg), msg

    def canonicalise(self) -> None:
        if self.is_stellar_not_dwarf and (self.spectral not in ['O', 'B', 'A'] and self.size in ['Ia', 'Ib']):
            self.size = 'II'

        if 'D' == self.size and self.spectral is not None and self.digit is not None:
            self.size = 'V'

        if 'VI' == self.size and self.spectral in ['O', 'B', 'A']:
            self.size = 'V'

        if 'VI' == self.size and 'F' == self.spectral and str(self.digit) in ['0', '1', '2', '3', '4']:
            self.size = 'V'

        if 'IV' == self.size and 'M' == self.spectral:
            self.size = 'V'

        if 'IV' == self.size and 'K' == self.spectral and str(self.digit) in ['5', '6', '7', '8', '9']:
            self.size = 'V'

    @property
    def flux_choice(self) -> str:
        if 'F' != self.spectral:
            return self.spectral
        else:
            if int(self.digit) < 5:
                return 'F0-4'
            else:
                return 'F5-9'

    def check_canonical_size(self, max_flux, min_flux) -> Optional[str]:
        choice = self.flux_choice
        flux_line = SystemStar.star_fluxen[choice]
        raw_line = {v for (k, v) in flux_line.items() if max_flux >= k >= min_flux}
        trim_line = sorted(raw_line)
        msg = None
        if self.size not in trim_line:
            msg = "Flux values {} to {} only permit sizes {} of {} class star - not {}".format(min_flux, max_flux, ' '.join(trim_line), choice, self.size)

        return msg

    def fix_canonical_size(self, max_flux, min_flux) -> None:
        choice = self.flux_choice
        flux_line = SystemStar.star_fluxen[choice]
        current_flux = [k for (k, v) in flux_line.items() if v == self.size]
        if not current_flux:
            current_flux = [-6]

        if max(current_flux) < min_flux:
            self.size = flux_line[min_flux]
        elif min(current_flux) > max_flux:
            self.size = flux_line[max_flux]
