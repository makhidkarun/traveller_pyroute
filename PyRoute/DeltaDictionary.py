"""
Created on May 21, 2023

@author: CyberiaResurrection
"""
import codecs
import logging
import os
import string
from pathlib import Path

from PyRoute.Galaxy import Sector
from PyRoute.Star import Star


class DeltaDictionary(dict):

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SectorDictionary), "Values must be SectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SectorDictionary), "Values must be SectorDictionary objects"
        super().__setitem__(item, value)


class SectorDictionary(dict):

    def __init__(self, name, filename):
        super().__init__()
        self.name = name
        self.filename = filename
        self.position = None

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().__setitem__(item, value)

    @property
    def lines(self):
        result = list()
        for sub_name in self.keys():
            result.extend(self[sub_name].items)

        return result

    @staticmethod
    def load_traveller_map_file(filename):
        basename = os.path.basename(filename)
        lines = None

        # read travellermap file in, line by line
        with codecs.open(filename, 'r', 'utf-8') as infile:
            lines = [line for line in infile]

        nameline = lines[3]  # assuming the definitive name line is the 4th line in what got read in
        name = nameline.strip('#')
        position = lines[4]

        sector = SectorDictionary(name.strip(), basename)
        headers, starlines = SectorDictionary._partition_file(lines)
        sector.headers = headers
        sector.position = position.strip()

        # dig out subsector names, and use them to seed the dict entries
        sublines = [line for line in headers if '# Subsector ' in line]
        subsector_names = dict()

        for line in sublines:
            bitz = line.split(':')
            alpha = bitz[0][-1]
            subname = bitz[1].strip()
            subsector_names[alpha] = subname
            subsec = SubsectorDictionary(subname)
            sector[subname] = subsec

        # now subsectors are seeded, run thru the elements of starlines and deal them out to their respective subsector
        # dicts
        dummy = Sector('', '# 0,0')
        logging.disable(logging.WARNING)
        for line in starlines:
            # Re-use the existing, battle-tested, validation logic rather than scraping something new and buggy together
            star = Star.parse_line_into_star(line, dummy, 'scaled', 'scaled')
            if not star:
                continue
            subsec = star.subsector()
            subname = subsector_names[subsec]
            sector[subname].items.append(line)

        return sector

    @staticmethod
    def _partition_file(lines):
        """
            Break lines out into headers section, which is retained, and starlines, which gets minimised later on
            - this assumes downloaded-from-TravellerMap sector file
        """
        headers = []
        starlines = []
        isheader = True
        for line in lines:
            if isheader:
                headers.append(line)
                if line.startswith('----'):
                    isheader = False
            else:
                starlines.append(line)
        return headers, starlines


class SubsectorDictionary(dict):

    def __init__(self, name):
        self.name = name
        self.items = list()
        super().__init__()

    @property
    def lines(self):
        return self.items
