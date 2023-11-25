"""
Created on Nov 23, 2023

@author: CyberiaResurrection

"""


class SystemStar(object):

    sizes = ["Ia", "Ib", "II", "III", "IV", "V", "VI", "D", "NS", "PSR", "BH", "BD"]
    starsizes = ["Ia", "Ib", "II", "III", "IV", "V", "VI", "D"]
    spectrals = ['O', 'B', 'A', 'F', 'G', 'K', 'M']

    def __init__(self, size, spectral=None, digit=None):
        self.size = size
        self.spectral = spectral
        self.digit = digit

    def __str__(self):
        if self.spectral is None or self.digit is None:
            return self.size
        return self.spectral + str(self.digit) + ' ' + self.size

    @property
    def is_stellar(self):
        return self.size in SystemStar.starsizes

    @property
    def is_stellar_not_dwarf(self):
        return self.is_stellar and self.size != 'D'

    def is_bigger(self, other):
        if self.size != other.size:
            return SystemStar.sizes.index(self.size) < SystemStar.sizes.index(other.size)
        if self.spectral is None or other.spectral is None:
            return True
        if self.spectral != other.spectral:
            return SystemStar.spectrals.index(self.spectral) < SystemStar.spectrals.index(other.spectral)
        if self.digit is None or other.digit is None:
            return True
        if self.digit != other.digit:
            return self.digit < other.digit
        return True

    def check_canonical(self):
        msg = []

        # Most of these checks are implied by the "Spectral Type And Size" table on p28 of T5.10 Book 3

        if self.is_stellar_not_dwarf and (self.spectral not in 'OBA' and self.size in ['Ia', 'Ib']):
            line = "Only OBA class stars can be supergiants (Ia/Ib), not " + str(self)
            msg.append(line)

        return 0 == len(msg), msg

    def canonicalise(self):
        if self.is_stellar_not_dwarf and (self.spectral not in 'OBA' and self.size in ['Ia', 'Ib']):
            self.size = 'II'
