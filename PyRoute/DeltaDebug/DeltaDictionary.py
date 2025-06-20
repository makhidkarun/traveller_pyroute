"""
Created on May 21, 2023

@author: CyberiaResurrection
"""
import codecs
import copy
import logging
import os

from PyRoute.DeltaDebug.DeltaLogicError import DeltaLogicError


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
            subset_sector = copy.deepcopy(self[sector_name])
            if 0 == len(subset_sector.lines):
                continue
            new_dict[sector_name] = subset_sector
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
            subset_sector = self[sector_name].subsector_subset(overlap[sector_name])
            if 0 == len(subset_sector.lines):
                continue
            new_dict[sector_name] = subset_sector

        return new_dict

    def allegiance_subset(self, allegiances):
        new_dict = DeltaDictionary()
        for sector_name in self:
            subset_sector = self[sector_name].allegiance_subset(allegiances)
            if 0 == len(subset_sector.allegiances):
                continue
            if 0 == len(subset_sector.lines):
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
        result, msg = self.is_well_formed()
        if not result:
            raise DeltaLogicError(msg)

        for sector_name in self:
            if 0 == len(self[sector_name].lines):
                continue
            self[sector_name].write_file(output_dir)

    def skip_void_subsectors(self):
        # skip void subsectors unconditionally - all they do is take up space in subsector reduction
        for secname in self:
            self[secname].skip_void_subsectors()

    def trim_empty_allegiances(self):
        for sector in self:
            self[sector].trim_empty_allegiances()

    def is_well_formed(self):
        for sector in self:
            result, msg = self[sector].is_well_formed()
            if not result:
                return False, msg

        return True, ""


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

    def __deepcopy__(self, memodict: dict = {}):
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
            DeltaLogicError.delta_assert(
                0 == allegiance.stats.tradeDton,
                "Trade volume stats not reset on SectorDictionary deepcopy"
            )
            DeltaLogicError.delta_assert(
                0 == allegiance.stats.tradeDtonExt,
                "TradeDtonExt stats not reset on SectorDictionary deepcopy"
            )

        return foo

    def subsector_subset(self, subsectors):
        overlap = list()
        missed = list()
        for subsector_name in subsectors:
            if subsector_name in self:
                if not 0 == self[subsector_name].num_lines:
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
            # Cases like "Va", "As" can be ambiguous as trade codes or allegiances, so only exclude them
            # if the substring occurs in the rightmost half of the line
            if 2 == len(alg):
                raw_lines = [line for line in raw_lines if line.rfind(' ' + alg + ' ') < len(line) / 2]
            else:
                raw_lines = [line for line in raw_lines if ' ' + alg + ' ' not in line]

        result = self.drop_lines(raw_lines)
        result.allegiances = {key: copy.deepcopy(alg) for (key, alg) in self.allegiances.items() if key in allegiances}

        nu_allegiances = result.allegiances.keys()
        nu_headers = []
        processed = set()
        header_lines = set()

        for line in self.headers:
            if 'Alleg:' not in line:
                nu_headers.append(line)
                continue
            for alg in nu_allegiances:
                if alg + ":" in line:
                    if alg in processed:
                        continue
                    if line in header_lines:
                        continue
                    nu_headers.append(line)
                    processed.add(alg)
                    header_lines.add(line)
                    continue

        result.headers = nu_headers

        return result

    def subsector_list(self):
        result = list()
        for subsector_name in self:
            if 0 < self[subsector_name].num_lines:
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
        new_dict.allegiances = dict()
        for alg in self.allegiances:
            new_dict.allegiances[alg] = copy.deepcopy(self.allegiances[alg])
            new_dict.allegiances[alg].homeworlds = []
            stats = new_dict.allegiances[alg].stats
            stats.homeworlds = []
            stats.passengers = 0
            stats.trade = 0
            stats.tradeExt = 0
            stats.tradeDton = 0
            stats.tradeDtonExt = 0

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

        with codecs.open(out_name, 'w', encoding="utf-8") as handle:
            for line in self.headers:
                handle.write(line)

            for raw_line in self.lines:
                line = raw_line.strip('\n') + '\n'
                handle.write(line)

    @staticmethod
    def load_traveller_map_file(filename):
        from PyRoute.Inputs.ParseSectorInput import ParseSectorInput
        basename = os.path.basename(filename)
        logger = logging.getLogger('PyRoute.DeltaDictionary')
        headers, starlines = ParseSectorInput.read_sector_file(filename, logger)

        if 0 == len(headers):
            return None

        sector = ParseSectorInput.read_parsed_sector_to_sector_dict(basename, headers, starlines)
        sector.trim_empty_allegiances()

        return sector

    def trim_empty_allegiances(self):
        raw_lines = self.lines
        discard = []

        for alg in self.allegiances:
            matches = [line for line in raw_lines if line.rfind(' ' + alg + ' ') > len(line) / 2]
            if 0 == len(matches):
                discard.append(alg)

        if 0 == len(discard):
            return

        self.allegiances = {key: copy.deepcopy(alg) for (key, alg) in self.allegiances.items() if key not in discard}

        nu_headers = []
        processed = set()

        for line in self.headers:
            if 'Alleg:' not in line:
                nu_headers.append(line)
                continue
            for alg in self.allegiances:
                if alg + ":" in line:
                    if alg in processed:
                        continue
                    nu_headers.append(line)
                    processed.add(alg)
                    continue

        self.headers = nu_headers

    def is_well_formed(self):
        for subsec in self:
            result, msg = self[subsec].is_well_formed()
            if not result:
                return False, msg

        allegiances = [item[9:] for item in self.headers if "Alleg: " in item]
        allegiances = [item[0:4] if ":" == item[4] else item[0:2] for item in allegiances]
        raw_lines = self.lines
        for alg in allegiances:
            raw_lines = [line for line in raw_lines if ' ' + alg + ' ' not in line]

        if 0 < len(raw_lines):
            return False, str(len(raw_lines)) + " starlines not belonging to listed allegiances for " + self.name

        raw_lines = self.lines
        for alg in allegiances:
            matches = [line for line in raw_lines if line.rfind(' ' + alg + ' ') > len(line) / 2]
            if 0 == len(matches):
                return False, "Allegiance " + alg + " lacks matching starlines"

        return True, ""


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

    def __deepcopy__(self, memodict: dict = {}):
        foo = SubsectorDictionary(self.name, self.position)
        if self.skipped:
            foo.items = None
            return foo

        for item in self.items:
            foo.items.append(copy.deepcopy(item.strip('\n')))
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

    def is_well_formed(self):
        return True, ""
