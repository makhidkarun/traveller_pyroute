'''
Created on Mar 17, 2014

@author: tjoneslo
'''
import logging
from wikistats import WikiStats
from collections import OrderedDict
from AllyGen import AllyGen

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
        self.sum_ru     = 0
        self.shipyards  = 0
        

class StatCalculation(object):
    '''
    Statistics calculations and output.
    '''


    def __init__(self, galaxy):
        self.logger = logging.getLogger('PyRoute.StatCalculation')

        self.galaxy = galaxy
        self.uwp    = OrderedDict()
        self.uwp['Starport'] = {}
        self.uwp['Size'] = {}
        self.uwp['Atmosphere'] = {}
        self.uwp['Hydrographics'] = {}
        self.uwp['Population'] = {}
        self.uwp['Government'] = {}
        self.uwp['Law Level'] = {}
        self.uwp['Tech Level'] = {}
        self.uwp['Pop Code'] = {}
        
    def calculate_statistics(self):
        self.logger.info('Calculating statistics for {:d} worlds'.format(len(self.galaxy.stars)))
        for sector in self.galaxy.sectors:
            if sector is None: continue
            for star in sector.worlds:
                self.add_stats(sector.stats, star)
                self.add_stats(self.galaxy.stats, star)
                self.add_stats(sector.subsectors[star.subsector()].stats, star)
                algStats = self.galaxy.alg.setdefault(AllyGen.same_align(star.alg), ("Unknown", ObjectStatistics()))[1]
                self.add_stats(algStats, star)
                self.max_tl (algStats, star)
                
                for uwpCode, uwpValue in star.uwpCodes.iteritems():
                    stats = self.uwp[uwpCode].setdefault(uwpValue, ObjectStatistics())
                    self.add_stats(stats, star)
                
            self.per_capita(sector.stats) # Per capital sector stats
            for subsector in sector.subsectors.itervalues():
                self.per_capita(subsector.stats)
                
        self.per_capita(self.galaxy.stats)
        
        for stats in self.galaxy.alg.itervalues():
            self.per_capita(stats[1])

    def add_stats(self, stats, star):
        stats.population += star.population
        stats.economy += star.gwp
        stats.number += 1
        stats.sum_ru += star.ru
        stats.shipyards += star.ship_capacity
        stats.tradeVol += star.tradeOver
        
    def max_tl (self, stats, star):
        stats.maxTL = max(stats.maxTL, star.tl)
        stats.maxPort = 'ABCDEX'[min('ABCDEX'.index(star.uwpCodes['Starport']), 'ABCDEX'.index(stats.maxPort))]
    
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
        
            
    def write_statistics(self, ally_count):
        self.logger.info('Charted star count: ' + str(self.galaxy.stats.number))
        self.logger.info('Charted population {:,d}'.format(self.galaxy.stats.population))
        
        for sector in self.galaxy.sectors:
            if sector is None: continue
            self.logger.debug('Sector ' + sector.name + ' star count: ' + str(sector.stats.number))
            
        for aleg, stats in self.galaxy.alg.iteritems():
            s = u'Allegiance {0} ({1}) star count: {2:,d}'.format(stats[0], aleg, stats[1].number)
            self.logger.debug(s)
            
        wiki = WikiStats(self.galaxy, self.uwp, ally_count)
        wiki.write_statistics()
        