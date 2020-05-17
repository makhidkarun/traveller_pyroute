"""
Created on Mar 17, 2014

@author: tjoneslo
"""
import logging
import math
from wikistats import WikiStats
from collections import OrderedDict, defaultdict
from AllyGen import AllyGen
from Star import UWPCodes


class Populations(object):
    def __init__(self):
        self.code = ""
        self.homeworlds = []
        self.count = 0
        self.population = 0
        
    def add_population(self, population, homeworld):
        self.count += 1
        self.population += population
        if homeworld:
            self.homeworlds.append(homeworld)

    def __lt__(self, other):
        return self.population < other.population

class ObjectStatistics(object):
    base_mapping = {'C':'Corsair base', 'D':'Naval depot', 'E': 'Embassy', 'K': 'Naval base', 'M': 'Military base',
                    'N': 'Naval base', 'O': 'Naval outpost',
                    'R': 'Clan base', 'S': 'Scout base', 'T':'Tlaukhu base', 'V': 'Scout base', 'W': 'Way station',
                    '*': 'Unknown', 'I': 'Unknown',
                    'G': 'Vargr Naval base',  'J': 'Naval base',
                    'L': 'Hiver naval base', 'P': 'Droyne Naval base', 'Q': 'Droyne military garrison',
                    'X': 'Zhodani relay station', 'Y': 'Zhodani depot',
                    'A': 'Split', 'B': 'Split', 'F': 'Split','H': 'Split', 'U': 'Split', 'Z': 'Split' }

    def __init__(self):
        self.population = 0
        self.populations = defaultdict(Populations)

        self.economy = 0
        self.trade = 0
        self.tradeExt = 0
        self.tradeVol = 0
        self.percapita = 0
        self.number = 0
        self.milBudget = 0
        self.maxTL = 0
        self.maxPort = 'X'
        self.maxPop = 0
        self.sum_ru = 0
        self.shipyards = 0
        self.col_be = 0
        self.im_be = 0
        self.passengers = 0
        self.spa_people = 0
        self.port_size = defaultdict(int)
        self.code_counts = defaultdict(int)
        self.bases = defaultdict(int)
        self.eti_worlds = 0
        self.eti_cargo = 0
        self.eti_pass = 0
        self.homeworlds = []
        self.high_pop_worlds = []
        self.high_tech_worlds = []
        self.TLmean = 0
        self.TLstddev = 0
        self.subsectorCp = []
        self.sectorCp = []
        self.otherCp = []
        self.gg_count = 0
        self.worlds = 0
        self.stars = 0
        self.star_count = defaultdict(int)
        self.primary_count = defaultdict(int)

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['high_pop_worlds']
        del state['high_tech_worlds']
        del state['subsectorCp']
        del state['sectorCp']
        del state['otherCp']
        del state['homeworlds']
        return state
    
    def homeworld_count(self):
        return len(self.homeworlds)

    def high_pop_worlds_count(self):
        return len(self.high_pop_worlds)

    def high_pop_worlds_list(self):
        return [world.wiki_name() for world in self.high_pop_worlds[0:6]]

    def high_tech_worlds_count(self):
        return len(self.high_tech_worlds)

    def high_tech_worlds_list(self):
        return [world.wiki_name() for world in self.high_tech_worlds[0:6]]

    def populations_count(self):
        return len(self.populations)


class UWPCollection(object):
    def __init__(self):
        self.uwp = OrderedDict()
        for uwpCode in UWPCodes.uwpCodes:
            self.uwp[uwpCode] = {}

    def stats(self, code, value):
        return self.uwp[code].setdefault(value, ObjectStatistics())

    def __getitem__(self, index):
        return self.uwp[index]

    def __setitem__(self, index, value):
        self.uwp[index] = value


class StatCalculation(object):
    """
    Statistics calculations and output.
    """

    def __init__(self, galaxy):
        self.logger = logging.getLogger('PyRoute.StatCalculation')

        self.galaxy = galaxy
        self.all_uwp = UWPCollection()
        self.imp_uwp = UWPCollection()

    def calculate_statistics(self, ally_match):
        self.logger.info('Calculating statistics for {:d} worlds'.format(len(self.galaxy.stars)))
        for sector in self.galaxy.sectors.values():
            if sector is None:
                continue
            for star in sector.worlds:
                star.starportSize = max(self.trade_to_btn(star.tradeIn + star.tradeOver) - 5, 0)
                star.uwpCodes['Starport Size'] = star.starportSize
                # Budget in MCr
                star.starportBudget = \
                    ((star.tradeIn // 10000) * 150 + (star.tradeOver // 10000) * 140 +
                     (star.passIn) * 500 + (star.passOver) * 460) // 1000000

                # Population in people employed.
                star.starportPop = int(star.starportBudget / 0.2)

                self.add_stats(sector.stats, star)
                self.add_stats(self.galaxy.stats, star)
                self.add_stats(sector.subsectors[star.subsector()].stats, star)

                self.max_tl(sector.stats, star)
                self.max_tl(sector.subsectors[star.subsector()].stats, star)

                self.add_alg_stats(self.galaxy, star, star.alg_code)
                self.add_alg_stats(sector, star, star.alg_code)
                self.add_alg_stats(sector.subsectors[star.subsector()], star, star.alg_code)

                if star.alg_base_code != star.alg_code:
                    self.add_alg_stats(self.galaxy, star, star.alg_base_code)
                    self.add_alg_stats(sector, star, star.alg_base_code)
                    self.add_alg_stats(sector.subsectors[star.subsector()], star, star.alg_base_code)

                if AllyGen.imperial_align(star.alg_code):
                    for uwpCode, uwpValue in star.uwpCodes.items():
                        self.add_stats(self.imp_uwp.stats(uwpCode, uwpValue), star)

                for uwpCode, uwpValue in star.uwpCodes.items():
                    self.add_stats(self.all_uwp.stats(uwpCode, uwpValue), star)

            self.per_capita(sector.worlds, sector.stats)  # Per capita sector stats
            sector.alg_sorted = AllyGen.sort_allegiances(sector.alg, ally_match)
            for alg in sector.alg_sorted:
                self.per_capita(alg.worlds, alg.stats)

            for subsector in sector.subsectors.values():
                self.per_capita(subsector.worlds, subsector.stats)
                subsector.alg_sorted = AllyGen.sort_allegiances(subsector.alg, ally_match)
                for alg in subsector.alg_sorted:
                    self.per_capita(alg.worlds, alg.stats)

        self.per_capita(None, self.galaxy.stats)

        self.galaxy.alg_sorted = AllyGen.sort_allegiances(self.galaxy.alg, ally_match)
        for alg in self.galaxy.alg_sorted:
            self.per_capita(alg.worlds, alg.stats)

        for uwpName in self.all_uwp.uwp.values():
            for uwpStats in uwpName.values():
                self.per_capita(None, uwpStats)

        for uwpName in self.imp_uwp.uwp.values():
            for uwpStats in uwpName.values():
                self.per_capita(None, uwpStats)

    def add_alg_stats(self, area, star, alg):
        algStats = area.alg[alg].stats
        self.add_stats(algStats, star)
        self.max_tl(algStats, star)

    def add_pop_to_sophont(self, stats, star):

        total_pct = 100
        default_soph = 'Huma'
        home = None
        for sophont in star.tradeCode.sophonts:
            soph_code = sophont[0:4]
            soph_pct = sophont[4:]

            if soph_pct == 'A':
                default_soph = soph_code
                continue

            soph_pct = 100.0 if soph_pct == 'W' else 0.0 if soph_pct in ['X', 'A'] else \
                5.0 if soph_pct == '0' else 10.0 * int(soph_pct)

            if any([soph for soph in star.tradeCode.homeworld if soph.startswith(soph_code)]):
                home = star

            # Soph_pct == 'X' is dieback or extinct.
            if soph_pct == 'X':
                stats.populations[soph_code].population = -1
            # skip the empty worlds
            elif not star.tradeCode.barren:
                stats.populations[soph_code].add_population(int(star.population * (soph_pct / 100.0)), home)

            total_pct -= soph_pct

        if total_pct < -5:
            self.logger.warning("{} has sophont percent over 100%: {}".format(star, total_pct))
        elif total_pct < 0:
            self.logger.info("{} has a sophont percent just over 100%: {}".format(star, total_pct))
        elif not star.tradeCode.barren:
            stats.populations[default_soph].add_population(int(star.population * (total_pct / 100.0)), None)

    def add_stats(self, stats, star):
        stats.population += star.population

        if star.tradeCode.homeworld:
            stats.homeworlds.append(star)

        self.add_pop_to_sophont(stats, star)

        stats.economy += star.gwp
        stats.number += 1
        stats.sum_ru += star.ru
        stats.shipyards += star.ship_capacity
        stats.tradeVol += (star.tradeOver + star.tradeIn)
        stats.col_be += star.col_be
        stats.im_be += star.im_be
        stats.passengers += star.passIn
        stats.spa_people += star.starportPop
        stats.port_size[star.starportSize] += 1
        stats.port_size[star.port] += 1
        for code in star.tradeCode.codes:
            stats.code_counts[code] += 1
        if star.ggCount:
            stats.gg_count += 1

        stats.worlds += star.worlds

        if star.star_list:
            stats.stars += len(star.star_list)
            stats.star_count[len(star.star_list)] += 1
            stats.primary_count[star.star_list[0][0]] += 1

        for code in star.baseCode:
            if code != '-':
                if code == 'A':
                    stats.bases[ObjectStatistics.base_mapping['N']] += 1
                    stats.bases[ObjectStatistics.base_mapping['S']] += 1
                elif code == 'B':
                    stats.bases[ObjectStatistics.base_mapping['N']] += 1
                    stats.bases[ObjectStatistics.base_mapping['W']] += 1
                elif code == 'F':
                    stats.bases[ObjectStatistics.base_mapping['K']] += 1
                    stats.bases[ObjectStatistics.base_mapping['M']] += 1
                elif code == 'H':
                    stats.bases[ObjectStatistics.base_mapping['C']] += 1
                    stats.bases[ObjectStatistics.base_mapping['K']] += 1
                elif code == 'U':
                    stats.bases[ObjectStatistics.base_mapping['T']] += 1
                    stats.bases[ObjectStatistics.base_mapping['R']] += 1
                elif code == 'Z':
                    stats.bases[ObjectStatistics.base_mapping['K']] += 1
                    stats.bases[ObjectStatistics.base_mapping['M']] += 1
                else:
                    stats.bases[ObjectStatistics.base_mapping[code]] += 1


        if star.eti_cargo_volume > 0 or star.eti_pass_volume > 0:
            stats.eti_worlds += 1
        stats.eti_cargo += star.eti_cargo_volume
        stats.eti_pass += star.eti_pass_volume

    def max_tl(self, stats, star):
        stats.maxTL = max(stats.maxTL, star.tl)
        stats.maxPort = 'ABCDEX?'[min('ABCDEX?'.index(star.uwpCodes['Starport']), 'ABCDEX?'.index(stats.maxPort))]
        stats.maxPop = max(stats.maxPop, star.popCode)

    def per_capita(self, worlds, stats):
        if stats.population > 100000:
            stats.percapita = stats.economy // (stats.population // 1000)
        elif stats.population > 0:
            stats.percapita = stats.economy * 1000 // stats.population
        else:
            stats.percapita = 0

        if stats.shipyards > 1000000:
            stats.shipyards //= 1000000
        else:
            stats.shipyards = 0
        if worlds:
            stats.high_pop_worlds = [world for world in worlds if world.popCode == stats.maxPop]
            stats.high_pop_worlds.sort(key=lambda star: star.popM, reverse=True)
            stats.high_tech_worlds = [world for world in worlds if world.tl == stats.maxTL]
            stats.subsectorCp = [world for world in worlds if world.tradeCode.subsector_capital]
            stats.sectorCp = [world for world in worlds if world.tradeCode.sector_capital]
            stats.otherCp = [world for world in worlds if world.tradeCode.other_capital]

            TLList = [world.tl for world in worlds]
            if len(TLList) > 3:
                stats.TLmean = sum(TLList) / len(TLList)
                TLVar = [math.pow(tl - stats.TLmean, 2) for tl in TLList]
                stats.TLstddev = math.sqrt(sum(TLVar) / len(TLVar))

    def find_colonizer(self, world, owner_hex):
        for target in self.galaxy.ranges.neighbors_iter(world):
            if target.position == owner_hex:
                target.tradeCode.append("C:{}-{}".format(world.sector[0:4], world.position))
                pass

    def write_statistics(self, ally_count, ally_match, json_data):
        self.logger.info('Charted star count: ' + str(self.galaxy.stats.number))
        self.logger.info('Charted population {:,d}'.format(self.galaxy.stats.population))

        if self.logger.isEnabledFor(logging.DEBUG):
            for sector in self.galaxy.sectors.values():
                self.logger.debug('Sector {} star count: {:,d}'.format(sector.name, sector.stats.number))

            for code, aleg in self.galaxy.alg.items():
                if aleg.base:
                    s = 'Allegiance {0} ({1}: base {3}) star count: {2:,d}'.format(aleg.name, code, aleg.stats.number,
                                                                                aleg.base)
                else:
                    s = 'Allegiance {0} ({1}: base {3} -> {4}) star count: {2:,d}'.format(aleg.name, code, aleg.stats.number,
                                                                                aleg.base, AllyGen.same_align(aleg.code))
                self.logger.debug(s)

            self.logger.debug("min count: {}, match: {}".format(ally_count, ally_match))

        wiki = WikiStats(self.galaxy, self.all_uwp, ally_count, ally_match, json_data)
        wiki.write_statistics()

    @staticmethod
    def trade_to_btn(trade):
        if trade == 0:
            return 0
        return int(math.log(trade, 10))
