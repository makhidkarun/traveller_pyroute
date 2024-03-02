"""
Created on May 21, 2023

@author: CyberiaResurrection
"""
import codecs
import copy
import logging
import os

from PyRoute.DeltaDebug.DeltaLogicError import DeltaLogicError
from PyRoute.AllyGen import AllyGen
from PyRoute.Galaxy import Sector, Allegiance
from PyRoute.Star import Star


class DeltaDictionary(dict):

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SectorDictionary), "Values must be SectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SectorDictionary), "Values must be SectorDictionary objects"
        super().__setitem__(item, value)

    def sector_subset(self, sectors):
        overlap = list()
        for sector_name in sectors:
            if sector_name in self:
                overlap.append(sector_name)

        new_dict = DeltaDictionary()
        for sector_name in overlap:
            new_dict[sector_name] = copy.deepcopy(self[sector_name])
            pass

        return new_dict

    def subsector_subset(self, subsectors):
        overlap = dict()
        # Not sure if duplicate subsector names are a real problem to worry about,
        # as a reducer doesn't have to be perfect.  If a same-named subsector is
        # redundantly picked up from another sector, so be it - it will get cleaned
        # up during line-level reduction.
        for sector_name in self:
            for subsector_name in self[sector_name]:
                if subsector_name in subsectors:
                    if sector_name not in overlap:
                        overlap[sector_name] = list()
                    overlap[sector_name].append(subsector_name)

        new_dict = DeltaDictionary()
        for sector_name in overlap:
            new_dict[sector_name] = self[sector_name].subsector_subset(overlap[sector_name])

        return new_dict

    def allegiance_subset(self, allegiances):
        new_dict = DeltaDictionary()
        for sector_name in self:
            subset_sector = self[sector_name].allegiance_subset(allegiances)
            if 0 == len(subset_sector.allegiances):
                continue
            new_dict[sector_name] = subset_sector

        return new_dict

    def sector_list(self):
        result = list(self.keys())
        result.sort()

        return result

    def subsector_list(self):
        result = list()

        for sector_name in self:
            keys = self[sector_name].subsector_list()
            result.extend(list(keys))

        result.sort()

        return result

    def allegiance_list(self):
        result = set()

        for sector_name in self:
            sublist = self[sector_name].allegiance_list()
            result.update(sublist)

        return result

    @property
    def lines(self):
        result = list()
        for sub_name in self.keys():
            result.extend(self[sub_name].lines)

        return result

    def drop_lines(self, lines_to_drop):
        foo = DeltaDictionary()
        for sector_name in self:
            if self[sector_name].skipped:
                continue
            else:
                foo[sector_name] = self[sector_name].drop_lines(lines_to_drop)

        return foo

    def switch_lines(self, lines_to_drop):
        foo = DeltaDictionary()
        for sector_name in self:
            if self[sector_name].skipped:
                continue
            else:
                foo[sector_name] = self[sector_name].switch_lines(lines_to_drop)

        return foo

    def write_files(self, output_dir):
        for sector_name in self:
            self[sector_name].write_file(output_dir)

    def skip_void_subsectors_if_half(self):
        # if at least half of read-in subsectors are void, assume this is a follow-up on a previous reduction run
        # and mark all void subsectors as skipped
        void_subsec = 0
        for secname in self:
            void_subsec += self[secname].void_subsectors

        if void_subsec * 2 >= 16 * len(self):
            for secname in self:
                self[secname].skip_void_subsectors()


class SectorDictionary(dict):

    def __init__(self, name, filename):
        super().__init__()
        self.name = name
        self.filename = filename
        self.position = None
        self.allegiances = dict()
        self.headers = list()

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().__setitem__(item, value)

    def __deepcopy__(self, memodict={}):
        foo = self._setup_clone_sector_dict()

        foo.headers = copy.deepcopy(self.headers)
        foo.position = self.position

        for subsector_name in self:
            foo[subsector_name] = copy.deepcopy(self[subsector_name])

        for label in foo.allegiances:
            allegiance = foo.allegiances[label]
            if not hasattr(allegiance.stats, 'high_pop_worlds'):
                allegiance.stats.high_pop_worlds = []
            DeltaLogicError.delta_assert(
                0 == allegiance.stats.passengers,
                "Passenger stats not reset on SectorDictionary deepcopy"
            )
            DeltaLogicError.delta_assert(
                0 == allegiance.stats.trade,
                "Trade stats not reset on SectorDictionary deepcopy"
            )
            DeltaLogicError.delta_assert(
                0 == allegiance.stats.tradeExt,
                "TradeExt stats not reset on SectorDictionary deepcopy"
            )

        return foo

    def subsector_subset(self, subsectors):
        overlap = list()
        missed = list()
        for subsector_name in subsectors:
            if subsector_name in self:
                overlap.append(subsector_name)

        for subsector_name in self:
            if subsector_name not in overlap:
                missed.append(subsector_name)

        new_dict = self._setup_clone_sector_dict()

        for subsector_name in overlap:
            new_dict[subsector_name] = copy.deepcopy(self[subsector_name])

        for subsector_name in missed:
            new_dict[subsector_name] = SubsectorDictionary(self[subsector_name].name, self[subsector_name].position)
            new_dict[subsector_name].items = None

        return new_dict

    def allegiance_subset(self, allegiances):
        raw_lines = self.lines

        for alg in allegiances:
            raw_lines = [line for line in raw_lines if ' ' + alg + ' ' not in line]

        result = self.drop_lines(raw_lines)
        result.allegiances = {key: alg for (key, alg) in self.allegiances.items() if key in allegiances}

        nu_headers = []
        processed = set()

        for line in self.headers:
            if 'Alleg:' not in line:
                nu_headers.append(line)
                continue
            for alg in allegiances:
                if alg in line:
                    if alg in processed:
                        continue
                    nu_headers.append(line)
                    processed.add(alg)
                    continue

        result.headers = nu_headers

        return result

    def subsector_list(self):
        result = list()
        for subsector_name in self:
            if not self[subsector_name].skipped:
                result.append(subsector_name)

        return result

    def allegiance_list(self):
        result = set()
        for allegiance_name in self.allegiances:
            result.add(allegiance_name)
        return result

    def drop_lines(self, lines_to_drop):
        new_dict = self._setup_clone_sector_dict()

        for subsector_name in self:
            new_dict[subsector_name] = self[subsector_name].drop_lines(lines_to_drop)

        return new_dict

    def _setup_clone_sector_dict(self):
        new_dict = SectorDictionary(self.name, self.filename)
        new_dict.position = self.position
        new_dict.headers = self.headers
        new_dict.allegiances = self.allegiances
        for alg in new_dict.allegiances:
            new_dict.allegiances[alg].homeworlds = []
            stats = new_dict.allegiances[alg].stats
            stats.homeworlds = []
            stats.passengers = 0
            stats.trade = 0
            stats.tradeExt = 0

        return new_dict

    def switch_lines(self, lines_to_switch):
        new_dict = self._setup_clone_sector_dict()

        for subsector_name in self:
            new_dict[subsector_name] = self[subsector_name].switch_lines(lines_to_switch)

        return new_dict

    @property
    def lines(self):
        result = list()
        for sub_name in self.keys():
            if self[sub_name].items is not None:
                result.extend(self[sub_name].items)

        return result

    @property
    def skipped(self):
        for sub_name in self.keys():
            if self[sub_name].skipped is False:
                return False
        return True

    @property
    def void_subsectors(self):
        counter = 0
        for sub_name in self.keys():
            if self[sub_name].skipped is False and 0 == len(self[sub_name].items):
                counter += 1

        return counter

    def skip_void_subsectors(self):
        for sub_name in self.keys():
            if self[sub_name].skipped is False and 0 == len(self[sub_name].items):
                self[sub_name].items = None

    def write_file(self, output_dir):
        exists = os.path.exists(output_dir)
        if not exists:
            os.makedirs(output_dir)

        out_name = os.path.join(output_dir, self.filename) + "-min"

        handle = codecs.open(out_name, 'w', 'utf-8')
        for line in self.headers:
            handle.write(line)

        for line in self.lines:
            line = line.strip() + '\n'
            handle.write(line)

        handle.close()

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

        # dig out allegiances
        allegiances = [line for line in headers if '# Alleg:' in line]
        for line in allegiances:
            alg_code = line[8:].split(':', 1)[0].strip()
            alg_name = line[8:].split(':', 1)[1].strip().strip('"')
            alg_race = AllyGen.population_align(alg_code, alg_name)
            base = AllyGen.same_align(alg_code)
            if base not in sector.allegiances:
                sector.allegiances[base] = Allegiance(base, AllyGen.same_align_name(base, alg_name), base=True,
                                                      population=alg_race)
            if alg_code not in sector.allegiances:
                sector.allegiances[alg_code] = Allegiance(alg_code, alg_name, base=False, population=alg_race)

        # dig out subsector names, and use them to seed the dict entries
        sublines = [line for line in headers if '# Subsector ' in line]
        subsector_names = dict()

        for line in sublines:
            bitz = line.split(':')
            alpha = bitz[0][-1]
            subname = bitz[1].strip()
            if '' == subname:
                subname = name.strip() + ' ' + bitz[0][2:]
            subsector_names[alpha] = subname
            subsec = SubsectorDictionary(subname, alpha)
            sector[subname] = subsec

        # now subsectors are seeded, run thru the elements of starlines and deal them out to their respective subsector
        # dicts
        dummy = Sector('# dummy', '# 0,0')
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
                starlines.append(line.strip())
        return headers, starlines


class SubsectorDictionary(dict):

    def __init__(self, name, position):
        self.name = name
        self.items = list()
        self.position = position
        super().__init__()

    @property
    def lines(self):
        return self.items

    @property
    def skipped(self):
        return self.items is None

    @property
    def num_lines(self):
        if self.skipped:
            return 0
        return len(self.items)

    def __deepcopy__(self, memodict={}):
        foo = SubsectorDictionary(self.name, self.position)
        if self.skipped:
            foo.items = None
            return foo

        for item in self.items:
            foo.items.append(copy.deepcopy(item))
        return foo

    def drop_lines(self, lines_to_drop):
        foo = SubsectorDictionary(self.name, self.position)
        if self.skipped:
            foo.items = None
            return foo

        nonempty = 0 < len(self.items)

        for item in self.items:
            if item in lines_to_drop:
                continue
            foo.items.append(copy.deepcopy(item))

        if nonempty and 0 == len(foo.items):
            foo.items = None

        return foo

    def switch_lines(self, lines_to_switch):
        foo = SubsectorDictionary(self.name, self.position)
        if self.skipped:
            foo.items = None
            return foo

        # assemble shortlist
        shortlist = []
        switchlist = []
        # assuming lines_to_switch is a list of 2-element tuples
        for line in lines_to_switch:
            if line[0] in self.items:
                shortlist.append(line[0])
                switchlist.append(line[1])

        for line in self.items:
            if line not in shortlist:
                foo.items.append(line)

        for line in switchlist:
            foo.items.append(line)

        return foo
