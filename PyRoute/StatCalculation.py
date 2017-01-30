'''
Created on Mar 17, 2014

@author: tjoneslo
'''
import logging
import math
from wikistats import WikiStats
from collections import OrderedDict, defaultdict
from AllyGen import AllyGen
from Star import UWPCodes

class ObjectStatistics(object):
    def __init__(self):
        self.population = 0
        self.economy    = 0
        self.trade      = 0
        self.tradeExt   = 0
        self.tradeVol   = 0
        self.percapita  = 0
        self.number     = 0
        self.milBudget  = 0
        self.maxTL      = 0
        self.maxPort    = 'X'
        self.maxPop     = 0
        self.sum_ru     = 0
        self.shipyards  = 0
        self.col_be     = 0
        self.im_be      = 0
        self.passengers = 0
        self.spa_people = 0
        
        self.code_counts = defaultdict(int)
        self.gg_count   = 0
        self.naval_bases = 0
        self.scout_bases = 0
        self.way_stations = 0
        
        self.eti_worlds = 0
        self.eti_cargo = 0
        self.eti_pass = 0

class UWPCollection(object):
    def __init__(self):
        self.uwp = OrderedDict()
        for uwpCode in UWPCodes.uwpCodes:
            self.uwp[uwpCode] = {}

    def stats(self, code, value):
        return self.uwp[code].setdefault(value, ObjectStatistics())

    def __getitem__ (self,index):
        return self.uwp[index]

    def __setitem__ (self, index, value):
        self.uwp[index] = value

class StatCalculation(object):
    '''
    Statistics calculations and output.
    '''

    def __init__(self, galaxy):
        self.logger = logging.getLogger('PyRoute.StatCalculation')

        self.galaxy = galaxy
        self.all_uwp = UWPCollection()
        self.imp_uwp = UWPCollection()
        
    def calculate_statistics(self, match):
        self.logger.info('Calculating statistics for {:d} worlds'.format(len(self.galaxy.stars)))
        for sector in self.galaxy.sectors.itervalues():
            if sector is None: continue
            for star in sector.worlds:
                star.starportSize = max(self.trade_to_btn(star.tradeIn + star.tradeOver) - 5,0)
                star.starportBudget = \
                    ((star.tradeIn / 10000) * 150 +\
                    (star.tradeOver/10000) * 140 +\
                    (star.passIn) * 500 + \
                    (star.passOver) * 460) / 1000000
                    
                star.starportPop = int(star.starportBudget / 0.2)
                
                self.add_stats(sector.stats, star)
                self.add_stats(self.galaxy.stats, star)
                self.add_stats(sector.subsectors[star.subsector()].stats, star)
                self.max_tl(sector.stats, star)
                self.max_tl(sector.subsectors[star.subsector()].stats, star)
                if match == 'collapse':
                    self.add_alg_stats(self.galaxy, star, AllyGen.same_align(star.alg))
                    self.add_alg_stats(sector, star, AllyGen.same_align(star.alg))
                    self.add_alg_stats(sector.subsectors[star.subsector()], star,AllyGen.same_align(star.alg))
                    
                    if AllyGen.imperial_align(star.alg):
                        for uwpCode, uwpValue in star.uwpCodes.iteritems():
                            self.add_stats(self.imp_uwp.stats(uwpCode, uwpValue), star)
                    
                elif match == 'separate':
                    self.add_alg_stats(self.galaxy, star, star.alg)
                    self.add_alg_stats(sector, star, star.alg)
                    self.add_alg_stats(sector.subsectors[star.subsector()], star, star.alg)

                    self.add_alg_stats(self.galaxy, star, AllyGen.same_align(star.alg))
                    self.add_alg_stats(sector, star, AllyGen.same_align(star.alg))
                    self.add_alg_stats(sector.subsectors[star.subsector()], star,AllyGen.same_align(star.alg))
                    
                for uwpCode, uwpValue in star.uwpCodes.iteritems():
                    self.add_stats(self.all_uwp.stats(uwpCode, uwpValue), star)
                
            self.per_capita(sector.stats) # Per capita sector stats
            for subsector in sector.subsectors.itervalues():
                self.per_capita(subsector.stats)
        self.per_capita(self.galaxy.stats)
        
        for alg in self.galaxy.alg.itervalues():
            self.per_capita(alg.stats)

    def add_alg_stats(self, area, star, alg):
        algStats = area.alg[alg].stats
        self.add_stats(algStats, star)
        self.max_tl(algStats, star)
       
        
    def add_stats(self, stats, star):
        stats.population += star.population
        stats.economy += star.gwp
        stats.number += 1
        stats.sum_ru += star.ru
        stats.shipyards += star.ship_capacity
        stats.tradeVol += (star.tradeOver + star.tradeIn)
        stats.col_be += star.col_be
        stats.im_be += star.im_be
        stats.passengers  += star.passIn
        stats.spa_people += star.starportPop
        for code in star.tradeCode:
            stats.code_counts[code] += 1
        if star.ggCount:
            stats.gg_count += 1
        if 'N' in star.baseCode or 'K' in star.baseCode:
            stats.naval_bases += 1
        if 'S' in star.baseCode or 'V' in star.baseCode:
            stats.scout_bases += 1
        if 'W' in star.baseCode:
            stats.way_stations += 1
        if star.eti_cargo_volume > 0 or star.eti_pass_volume > 0 :
            stats.eti_worlds += 1
        stats.eti_cargo += star.eti_cargo_volume
        stats.eti_pass += star.eti_pass_volume
   
    def max_tl (self, stats, star):
        stats.maxTL = max(stats.maxTL, star.tl)
        stats.maxPort = 'ABCDEX'[min('ABCDEX'.index(star.uwpCodes['Starport']), 'ABCDEX'.index(stats.maxPort))]
        stats.maxPop = max (stats.maxPop, star.popCode)
    
    def per_capita(self, stats):
        stats.percapita = stats.economy
        if stats.population > 100000:
            stats.percapita = stats.economy / (stats.population/1000)
        elif stats.population > 0:
            stats.percapita = stats.economy * 1000 / stats.population
        else:
            stats.percapita = 0
            
        if stats.shipyards > 1000000:
            stats.shipyards /= 1000000
        else:
            stats.shipyards = 0
        
    def find_colonizer(self, world, owner_hex):
        for target in self.galaxy.ranges.neighbors_iter(world):
            if target.position == owner_hex:
                target.tradeCode.append("C:{}-{}".format(world.sector[0:4], world.position))
                pass
            
    def write_statistics(self, ally_count):
        self.logger.info('Charted star count: ' + str(self.galaxy.stats.number))
        self.logger.info('Charted population {:,d}'.format(self.galaxy.stats.population))
        
        for sector in self.galaxy.sectors.itervalues():
            self.logger.debug('Sector ' + sector.name + ' star count: ' + str(sector.stats.number))
            
        for code,aleg in self.galaxy.alg.iteritems():
            s = u'Allegiance {0} ({1}) star count: {2:,d}'.format(aleg.name, code, aleg.stats.number)
            self.logger.debug(s)
            
        wiki = WikiStats(self.galaxy, self.all_uwp, ally_count)
        wiki.write_statistics()
        
    @staticmethod
    def trade_to_btn(trade):
        if trade == 0:
            return 0
        return int(math.log(trade,10))
