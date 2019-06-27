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
        self.code_counts = defaultdict(int)
        self.gg_count = 0
        self.naval_bases = 0
        self.scout_bases = 0
        self.military_bases = 0
        self.way_stations = 0
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
                star.starportBudget = \
                    ((star.tradeIn // 10000) * 150 + (star.tradeOver // 10000) * 140 +
                     (star.passIn) * 500 + (star.passOver) * 460) // 1000000

                star.starportPop = int(star.starportBudget / 0.2)

                self.add_stats(sector.stats, star)
                self.add_stats(self.galaxy.stats, star)
                self.add_stats(sector.subsectors[star.subsector()].stats, star)

                self.max_tl(sector.stats, star)
                self.max_tl(sector.subsectors[star.subsector()].stats, star)

                self.add_alg_stats(self.galaxy, star, star.alg)
                self.add_alg_stats(sector, star, star.alg)
                self.add_alg_stats(sector.subsectors[star.subsector()], star, star.alg)

                if star.alg_base != star.alg:
                    self.add_alg_stats(self.galaxy, star, star.alg_base)
                    self.add_alg_stats(sector, star, star.alg_base)
                    self.add_alg_stats(sector.subsectors[star.subsector()], star, star.alg_base)

                if AllyGen.imperial_align(star.alg):
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

    def add_pop_to_sophont(self, stats, sophont, star):
        soph_code = sophont[0:4]
        soph_pct = sophont[4:]
        soph_pct = 100.0 if soph_pct == 'W' else 0.0 if soph_pct == 'X' else \
            5.0 if soph_pct == '0' else 10.0 * int(soph_pct)

        home = None
        if star.tradeCode.homeworld and any([soph for soph in star.tradeCode.homeworld_list if soph.startswith(soph_code[:4])]):
            home = star
        
        stats.populations[soph_code].add_population(int(star.population * (soph_pct / 100.0)), home)
        # Soph_pct == 'X' is diback or extinct. 
        if sophont[4:] == 'X':
            stats.populations[soph_code].population = -1

        return soph_pct
    
    def add_pop_to_alg(self, stats, alg, population):
        stats.populations[AllyGen.population_align(alg)].add_population(population, None)
        

    def add_stats(self, stats, star):
        stats.population += star.population

        if star.tradeCode.homeworld:
            stats.homeworlds.append(star)

        if star.tradeCode.sophonts is None:
            self.add_pop_to_alg(stats, star.alg, star.population)
        else:
            total_pct = 100
            for sophont in star.tradeCode.sophonts:
                total_pct -= self.add_pop_to_sophont(stats, sophont, star)
                
            if total_pct < 0:
                self.logger.warn("{} has sophont percent over 100%: {}".format(star, total_pct))
            elif total_pct > 0:
                self.add_pop_to_alg(stats, star.alg, int(star.population * (total_pct / 100.0)))

        stats.economy += star.gwp
        stats.number += 1
        stats.sum_ru += star.ru
        stats.shipyards += star.ship_capacity
        stats.tradeVol += (star.tradeOver + star.tradeIn)
        stats.col_be += star.col_be
        stats.im_be += star.im_be
        stats.passengers += star.passIn
        stats.spa_people += star.starportPop
        for code in star.tradeCode.codes:
            stats.code_counts[code] += 1
        if star.ggCount:
            stats.gg_count += 1
        if 'N' in star.baseCode or 'K' in star.baseCode:
            stats.naval_bases += 1
        if 'S' in star.baseCode or 'V' in star.baseCode:
            stats.scout_bases += 1
        if 'W' in star.baseCode:
            stats.way_stations += 1
        if 'M' in star.baseCode:
            stats.military_bases += 1
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
