"""
Created on Nov 29, 2023

@author: CyberiaResurrection
"""


class Nobles(object):
    __slots__ = 'nobles'

    codes = {'B': 'Knights',
             'c': 'Baronets',
             'C': 'Barons',
             'D': 'Marquis',
             'e': 'Viscounts',
             'E': 'Counts',
             'f': 'Dukes',
             'F': 'Sector Dukes',
             'G': 'Archdukes',
             'H': 'Emperor'}

    key_list = list(codes.keys())
    value_list = list(codes.values())

    def __init__(self):
        self.nobles = {'Knights': 0,
                       'Baronets': 0,
                       'Barons': 0,
                       'Marquis': 0,
                       'Viscounts': 0,
                       'Counts': 0,
                       'Dukes': 0,
                       'Sector Dukes': 0,
                       'Archdukes': 0,
                       'Emperor': 0}

    def __str__(self):
        # If there's absolutely no nobles, return '-':
        if 0 == self.max_value:
            return '-'

        nobility = ""
        for rank, count in self.nobles.items():
            if count > 0:
                nobility += Nobles.key_list[Nobles.value_list.index(rank)]
        return ''.join(sorted(nobility, key=lambda v: (v.lower(), v[0].isupper())))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['codes']
        return state

    def count(self, nobility) -> None:
        for code, rank in Nobles.codes.items():
            if code in nobility:
                self.nobles[rank] += 1

    def accumulate(self, nobles) -> None:
        for rank, count in nobles.nobles.items():
            self.nobles[rank] += count

    @property
    def max_value(self) -> int:
        return max(self.nobles.values())

    @property
    def min_value(self) -> int:
        return min(self.nobles.values())

    @property
    def sum_value(self) -> int:
        return sum(self.nobles.values())

    def is_well_formed(self) -> tuple[bool, str]:
        msg = ''
        if 0 > self.max_value:
            msg = 'Noble count values cannot be negative'
            return False, msg

        return True, msg
