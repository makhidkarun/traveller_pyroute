"""
Created on Nov 06, 2023

@author: CyberiaResurrection
"""


class Nobles(object):
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
        self.codes = {'B': 'Knights',
                      'c': 'Baronets',
                      'C': 'Barons',
                      'D': 'Marquis',
                      'e': 'Viscounts',
                      'E': 'Counts',
                      'f': 'Dukes',
                      'F': 'Sector Dukes',
                      'G': 'Archdukes',
                      'H': 'Emperor'}

    def __str__(self):
        # If there's absolutely no nobles, return '-':
        if 0 == max(self.nobles.values()):
            return '-'

        nobility = ""
        key_list = list(self.codes.keys())
        value_list = list(self.codes.values())
        for rank, count in self.nobles.items():
            if count > 0:
                nobility += key_list[value_list.index(rank)]
        return ''.join(sorted(nobility, key=lambda v: (v.lower(), v[0].isupper())))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['codes']
        return state

    def count(self, nobility):
        for code, rank in self.codes.items():
            if code in nobility:
                self.nobles[rank] += 1

    def accumulate(self, nobles):
        for rank, count in nobles.nobles.items():
            self.nobles[rank] += count

    @property
    def max_value(self):
        return max(self.nobles.values())

    @property
    def min_value(self):
        return min(self.nobles.values())

    @property
    def sum_value(self):
        return sum(self.nobles.values())

    def is_well_formed(self):
        msg = ''
        if 0 > self.max_value:
            msg = 'Noble count values cannot be negative'
            return False, msg

        return True, msg
