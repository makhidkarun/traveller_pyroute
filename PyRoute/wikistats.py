'''
Created on Mar 22, 2014

@author: tjoneslo
'''
import os
import numpypy
import numpy
import codecs
from AllyGen import AllyGen

class WikiStats(object):
    '''
    classdocs
    '''
    stat_header='{| class=\"wikitable sortable\"\n!Sector!! X,Y !! Worlds !! Population (millions) !! Economy (Bcr) !! Per Capita (Cr) !! Trade Volume (BCr) !! Int. Trade (BCr) !! Ext. Trade (BCr) !! RU !! Shipyard Capacity (MTons) !! Colonial Army (BEs)\n'

    def __init__(self, galaxy, uwp, min_alg_count=10):
        '''
        Constructor
        '''
        self.galaxy = galaxy
        self.uwp  = uwp
        self.min_alg_count = min_alg_count

    def write_statistics(self):
        self.summary_statistics()
        self.top_summary()
        self.tcs_statistics()
        #self.ru_statistics()
        self.subsector_statistics()
        self.write_allegiances(self.galaxy.alg)
        
    def summary_statistics(self):
        path = os.path.join(self.galaxy.output_path, 'summary.wiki')
        with open (path, 'w+') as f:
            f.write('==Economic Summary==\n')
            f.write('===Statistical Analysis===\n')
            f.write(self.stat_header)
            for sector in self.galaxy.sectors:
                f.write('|-\n')
                f.write('|{0}\n'.format(sector.wiki_name()))
                f.write('|| {:d},{:d}\n'.format(sector.x, sector.y))
                self.write_stats(f, sector.stats)
                
            if 'Im' in self.galaxy.alg:
                f.write('|-\n')
                f.write('| Imperial Total ||\n')
                imStats = self.galaxy.alg['Im'].stats
                self.write_stats(f, imStats)
            
            f.write('|-\n')
            f.write('| Global Total || \n')
            self.write_stats(f, self.galaxy.stats) 
            f.write('|}\n')
            
            area_type = "Sector"
            f.write('=== {} Statistics ===\n'.format(area_type))
            f.write('{| class="wikitable sortable"\n')
            f.write('! {} !! statistics\n'.format(area_type))
            for sector in self.galaxy.sectors:
                self.text_area_statistics(f, "sector", sector)
            f.write('|}\n')
        
            
    def write_stats(self, f, stats):
        f.write('|align="right"|{:d}\n'.format(stats.number))
        f.write('|align="right"|{:,d}\n'.format(stats.population))
        f.write('|align="right"|{:,d}\n'.format(stats.economy))
        f.write('|align="right"|{:,d}\n'.format(stats.percapita))
        f.write('|align="right"|{:,d}\n'.format(int(stats.tradeVol/1e9)))
        f.write('|align="right"|{:,d}\n'.format(int(stats.trade/1e9)))
        f.write('|align="right"|{:,d}\n'.format(int(stats.tradeExt/1e9)))
        f.write('|align="right"|{:,d}\n'.format(stats.sum_ru))
        f.write('|align="right"|{:,d}\n'.format(stats.shipyards))
        f.write('|align="right"|{:,.2f}\n'.format(stats.col_be))
        

    def top_summary(self):
        path = os.path.join(self.galaxy.output_path, 'top_summary.wiki')
        with open (path, 'w+') as f:
            f.write('==Top level Summary==\n')
            f.write('{|\n')
            f.write('|Systems || {}\n'.format(self.galaxy.stats.number))
            f.write('|-\n')
            f.write('|Population || {:,d} million\n'.format(self.galaxy.stats.population))
            f.write('|-\n')
            f.write('|Gross Total Product || {:,d} billion\n'.format(self.galaxy.stats.economy))
            f.write('|-\n')
            f.write('|Per Capita GSP || Cr {:,d}\n'.format(self.galaxy.stats.percapita))
            f.write('|-\n')
            f.write('|Trade || {:,d} billion\n'.format(int(self.galaxy.stats.trade/1e9)))
            f.write('\n|}\n')
            f.write('===Summary Report===\n')
            self.write_uwp_counts(f)
            f.write('|-\n|colspan=20 align=center|Percent by Population\n')
            self.write_uwp_populations(f)
        
    def write_allegiances (self, alg):
        path = os.path.join(self.galaxy.output_path, 'alleg_summary.wiki')
        with open (path, 'w+') as f:
            f.write('===[[Allegiance Code|Allegiance Information]]===\n')
            alg_sort = sorted(alg.iterkeys())
            f.write('{| class=\"wikitable sortable\"\n!Code ||Name||Worlds||Population (millions)||GNP (BCr)|| RU ||Shipyard Capacity (MTons)||Armed Forces (BE)\n')
            for code in alg_sort:
                if alg[code].stats.number < self.min_alg_count:
                    continue
                f.write('|-\n| {} || {} '.format(code, alg[code].wiki_name()))
                stats = alg[code].stats
                f.write('|| {:,d} || {:,d} || {:,d} || {:,d} || {:,d} '.format(stats.number, stats.population, stats.economy, stats.sum_ru, stats.shipyards))
                if AllyGen.are_allies(u'Im', code):
                    f.write('|| {:,.2f} (IA) + {:,.2F} (CA)\n'.format(stats.im_be, stats.col_be))
                else:
                    f.write('|| {:,.2f}\n'.format(stats.col_be))
            f.write('|}\n')
            
            area_type = "Allegiance"
            f.write('=== {} Statistics ===\n'.format(area_type))
            f.write('{| class=\"wikitable sortable\"\n')
            f.write('! {} !! statistics\n'.format(area_type))
            for code in alg_sort:
                self.text_area_statistics(f, "", alg[code])
            f.write('|}\n')
                
            
    
    def write_uwp_counts(self,f):
        from StatCalculation import ObjectStatistics
        default_stats = ObjectStatistics()
        f.write('{|\n!Component')
        for x in range(18):
            f.write('||{}'.format(baseN(x,18)))
        f.write('||I-Z')
        for name in self.uwp.iterkeys():
            f.write('\n|- \n| {}'.format(name))
            for x in range(18):
                index = baseN(x,18)
                stats = self.uwp.get(name, {}).get(index, default_stats)
                value = stats.number
                f.write('||{}'.format(value))
            if self.uwp[name].keys() in ['X']:
                index = 'X'
                stats = self.uwp.get(name, {}).get(index, default_stats)
                value = stats.number
                f.write ('||{}'.format(value))
            else:
                f.write('||0')
        f.write('\n')
        
    def write_uwp_populations(self,f):
        from StatCalculation import ObjectStatistics
        population = self.galaxy.stats.population
        default_stats = ObjectStatistics()

        for name in self.uwp.iterkeys():
            f.write('\n|- \n| {}'.format(name))
            for x in range(18):
                index = baseN(x,18)
                stats = self.uwp.get(name, {}).get(index, default_stats)
                value = int(stats.population / (population / 100)) if population > 0 else 0
                f.write('||{:d}%'.format(value))
            if self.uwp[name].keys() in ['X']:
                index = 'X'
                stats = self.uwp.get(name, {}).get(index, default_stats)
                value = int(stats.population / (population / 100)) if population > 0 else 0
                f.write ('||{:d}%'.format(value))
            else:
                f.write('||0')
        f.write('\n|}')
        
    def ru_statistics (self):
        path = os.path.join(self.galaxy.output_path, 'ru_summary.wiki')
        with open (path, 'w+') as f:
            f.write('=== Resource Units statistics by sector ===\n')
            f.write('{| class=\"wikitable sortable\"\n!Sector!!X,Y!!Worlds !! negative RUs !! positive RUs !! sum(RU) !! avg(RU) !! min(RU) !! max(RU) \n')
            for sector in self.galaxy.sectors:
                star_ru = [star.ru for star in sector.worlds]
                neg_ru = [star.ru for star in sector.worlds if star.ru <= 0]
                pos_ru = [star.ru for star in sector.worlds if star.ru >0]
                ru_sum = sum(star_ru)
                if ru_sum != 0 :
                    f.write('|-\n')
                    f.write('|{0}\n'.format(sector.wiki_name()))
                    f.write('| {:d},{:d}\n'.format(sector.x, sector.y))
                    f.write('|align="right"|{:d}\n'.format(sector.stats.number))
                    f.write('|align="right"|{:d}\n'.format(len(neg_ru)))
                    f.write('|align="right"|{:d}\n'.format(len(pos_ru)))
                    f.write('|align="right"|{:,d}\n'.format(ru_sum))
                    f.write('|align="right"|{:10.4f}\n'.format(numpy.average(star_ru)))
                    f.write('|align="right"|{:10.0f}\n'.format(numpy.amin(star_ru)))
                    f.write('|align="right"|{:10.0f}\n'.format(numpy.amax(star_ru)))
            f.write('|}\n')
        
    def tcs_statistics (self):
        path = os.path.join(self.galaxy.output_path, 'tcs_summary.wiki')
        with open (path, 'w+') as f:
            f.write('=== TCS Military budgets by sector ===\n')
            f.write('budgets in BCr, capacity in MegaTons\n')
            f.write('{| class=\"wikitable sortable\"\n!Sector!!X,Y!!Worlds !! Budget (BCr) !! Shipyard Capacity (MTons)\n')
            for sector in self.galaxy.sectors:
                budget = [star.budget/1000 for star in sector.worlds]
                capacity = [star.ship_capacity/1000000 for star in sector.worlds]
                budget_sum = sum(budget)
                capacity_sum = sum(capacity)
                
                f.write('|-\n')
                f.write('|{0}\n'.format(sector.wiki_name()))
                f.write('| {:d},{:d}\n'.format(sector.x, sector.y))
                f.write('|align="right"|{:d}\n'.format(sector.stats.number))
                f.write('|align="right"|{:,d}\n'.format(budget_sum))
                f.write('|align="right"|{:,d}\n'.format(capacity_sum))
                
            f.write('|}\n')
            
    def subsector_statistics(self):
        path = os.path.join(self.galaxy.output_path, 'subsector_summary.wiki')
        with codecs.open (path, 'w+','utf-8') as f:
            f.write('=== Economic Summary by Subsector ===\n')
            f.write(self.stat_header)
            for sector in self.galaxy.sectors:
                for subsector in sector.subsectors.itervalues():
                    f.write('|-\n')
                    f.write(u'|{}\n'.format(subsector.wiki_title()))
                    f.write('|| {:d},{:d}: {}\n'.format(sector.x, sector.y, subsector.position))
                    self.write_stats(f, subsector.stats)
            f.write('|}\n')
            area_type = "Subsector"
            f.write('=== {} Statistics ===\n'.format(area_type))
            f.write('{| class="wikitable sortable"\n')
            f.write('! {} !! statistics\n'.format(area_type))
            for sector in self.galaxy.sectors:
                for subsector in sector.subsectors.itervalues():
                    self.text_area_statistics(f, "subsector", subsector)
            f.write('|}\n')
                    
    def text_area_statistics(self, f, area_type, area):
            f.write('|-\n')
            f.write(u'|{0}\n'.format(area.wiki_title()))
            f.write('|| The {} {} contains {:d} worlds with a population of'.format(area.wiki_name(), area_type, 
                                                     area.stats.number))
            if area.stats.population >= 1000 :
                f.write(' {:,d} billion.'.format(area.stats.population/1000))
            else:
                f.write(' {:,d} million.'.format(area.stats.population))
            
            if len(area.worlds) > 0:
                popWorld = sorted(area.worlds, key=lambda world : world.population)[-1]
                f.write(' The highest population is ')
                if popWorld.popCode >= 9:
                    f.write('{:,d} billion'.format(popWorld.population/1000))
                elif popWorld.popCode >=6 :
                    f.write('{:,d} million'.format(popWorld.population))
                else:
                    f.write('less than 1 million')

                f.write(u', at {}.'.format(popWorld.wiki_name()))
                
                TLWorlds = [world for world in area.worlds if world.tl == area.stats.maxTL]
                if len(TLWorlds) > 0 and len(TLWorlds) < 6:
                    f.write(' The highest tech level is {} at '.format(baseN(area.stats.maxTL,18)))
                    f.write (", ".join(w.wiki_name() for w in TLWorlds))
                    f.write (".")
                
                subsectorCp = [world for world in area.worlds if 'Cp' in world.tradeCode]
                sectorCp = [world for world in area.worlds if 'Cs' in world.tradeCode]
                capital = [world for world in area.worlds if 'Cx' in world.tradeCode]
                
                if len(capital) > 0 :
                    for world in capital: 
                        alg = self.galaxy.alg[AllyGen.same_align(world.alg)]
                        f.write('\n* The capital of {} is at {}.'.format(alg.wiki_name(), world.wiki_name()))
                elif len(sectorCp) > 0 :
                    f.write(u' The sector capital is at ')
                    f.write(sectorCp[0].wiki_name())
                    f.write('.')
                elif len (subsectorCp) > 0 :
                    f.write(u' The subsector capital is at ')
                    f.write(subsectorCp[0].wiki_name())
                    f.write(".")
            f.write('\n')

def baseN(num,b,numerals="0123456789ABCDEFGHijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])        