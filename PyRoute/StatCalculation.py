'''
Created on Mar 17, 2014

@author: tjoneslo
'''
import logging

class ObjectStatistics(object):
    def __init__(self):
        self.population = 0
        self.economy    = 0
        self.trade      = 0
        self.percapita  = 0
        self.number     = 0
        

class StatCalculation(object):
    '''
    classdocs
    '''


    def __init__(self, galaxy):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('PyRoute.StatCalculation')

        self.galaxy = galaxy
        self.aleg   = {}
        self.uwp    = {'starport': {},
                       'size': {},
                       'atmosphere': {},
                       'hydrographics': {},
                       'population': {},
                       'government': {},
                       'lawlevel': {},
                       'techlevel': {}}
        
    def calculate_statistics(self):
        for sector in self.galaxy.sectors.itervalues():
            stats = sector.stats
            for star in sector.worlds:
                self.add_stats(stats, star)
                self.add_stats(self.galaxy.stats, star)
                
                algStats = self.aleg.setdefault(star.alg, ObjectStatistics())
                self.add_stats(algStats, star)
                
                for uwpCode, uwpValue in star.uwpCodes.iteritems():
                    stats = self.uwp[uwpCode].setdefault(uwpValue, ObjectStatistics())
                    self.add_stats(stats, star)
                
            self.per_capita(stats) # Per capital sector stats
            
        self.per_capita(self.galaxy.stats)
        
        for stats in self.aleg.itervalues():
            self.per_capita(stats)

    def add_stats(self, stats, star):
        stats.population += star.population
        stats.economy += star.gwp
        stats.trade += star.tradeIn
        stats.number += 1
        
    def per_capita(self, stats):
        stats.percapita = stats.economy
        if stats.population > 100000:
            stats.percapita = stats.economy / (stats.population/1000)
        elif stats.population > 0:
            stats.percapita = stats.economy * 1000 / stats.population
        else:
            stats.percapita = 0
            
    def write_statistics(self):
        self.logger.info('Galaxy star count: ' + str(self.galaxy.stats.number))
        
        for sector in self.galaxy.sectors.itervalues():
            self.logger.info('Sector ' + sector.name + ' star count: ' + str(sector.stats.number))
            
        for aleg, stats in self.aleg.iteritems():
            self.logger.info('Allegance ' + aleg + ' star count: ' + str(stats.number))