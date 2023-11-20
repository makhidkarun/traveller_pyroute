"""
Created on Nov 21, 2023

@author: CyberiaResurrection

Along the lines of TradeCodes, pull all the UWP handling, checking, etc into one single class that _just_ does UWP,
rather than the multiple concerns the Star class has evolved to embody.
"""
import re


class UWP(object):
    # Port code, size, atmo, hydro, pop, gov, law, the all-important hyphen, then TL
    match_string = '^([A-HXYa-hxy\?])([0-9A-Fa-f\?])([0-9A-Fa-f\?])([0-9Aa])([0-9A-Fa-f\?])([0-9A-Za-z\?])([0-9A-Ja-j\?])-([0-9A-Za-z\?])'

    match = re.compile(match_string)

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

    def __str__(self):
        return self.line

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
