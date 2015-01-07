'''
Created on Mar 22, 2014

@author: tjoneslo
'''
import os

import codecs
import datetime
from AllyGen import AllyGen
import urllib

class WikiStats(object):
    '''
    classdocs
    '''
    stat_header='{| class=\"wikitable sortable\"\n!Sector!! X,Y !! Worlds !! Population (millions) !! Economy (Bcr) !! Per Capita (Cr) !! Trade Volume (BCr) !! Int. Trade (BCr) !! Ext. Trade (BCr) !! RU !! Shipyard Capacity (MTons) !! Colonial Army (BEs) !! Travellers (M) !! SPA Pop\n'

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
        self.subsector_statistics()
        self.write_allegiances(self.galaxy.alg)
        self.write_world_statistics()
        
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
        f.write('|align="right"|{:,d}\n'.format(stats.passengers/1000000))
        f.write('|align="right"|{:,d}\n'.format(stats.spa_people))
        

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
        with codecs.open(path, "wb", 'utf_8') as f:
            f.write('===[[Allegiance Code|Allegiance Information]]===\n')
            alg_sort = sorted(alg.iterkeys())
            f.write('{| class=\"wikitable sortable\"\n!Code !! Name !! Worlds !! Population (millions) !! Economy (BCr) !! Per Capita (Cr) !!  RU !! Shipyard Capacity (MTons) !! Armed Forces (BEs) !! SPA Population\n')
            for code in alg_sort:
                if alg[code].stats.number < self.min_alg_count:
                    continue
                f.write(u'|-\n| {} || {} '.format(code, alg[code].wiki_name()))
                stats = alg[code].stats
                f.write('|| {:,d} '.format(stats.number))
                f.write('|| {:,d} '.format(stats.population))
                f.write('|| {:,d} '.format(stats.economy))
                f.write('|| {:,d} '.format(stats.percapita))
                f.write('|| {:,d} '.format(stats.sum_ru))
                f.write('|| {:,d} '.format(stats.shipyards))
                if AllyGen.are_allies(u'Im', code):
                    f.write('|| {:,.2f} (IA) + {:,.2F} (CA)'.format(stats.im_be, stats.col_be))
                else:
                    f.write('|| {:,.2f}'.format(stats.col_be))
                f.write ('|| {:,d}'.format(stats.spa_people))
                f.write('\n')
            f.write('|}\n')
            
            area_type = "Allegiance"
            f.write('=== {} Statistics ===\n'.format(area_type))
            f.write('{| class=\"wikitable sortable\"\n')
            f.write(u'! {} !! statistics\n'.format(area_type))
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
            found = False
            for index in self.uwp[name].iterkeys():
                if index not in '0123456789ABCDEFGH':
                    stats = self.uwp[name][index]
                    f.write ('||{:d}'.format(stats.number))
                    found = True
                    break
            if not found:
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
            
            found = False
            for index in self.uwp[name].iterkeys():
                if index not in '0123456789ABCDEFGH':
                    stats = self.uwp[name][index]
                    value = int(stats.population / (population / 100)) if population > 0 else 0
                    f.write ('||{:d}%'.format(value))
                    found = True
                    break
            if not found:
                f.write('||0%')
        f.write('\n|}')
        
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
                subsectors = [s for s in sector.subsectors.itervalues()]
                subsectors.sort(key=lambda s: s.position)
                for subsector in subsectors:
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
            
            if area_type == 'subsector':
                f.write(u'|| {}, {} {} of {},'.format(area.wiki_name(), area_type,
                                                    area.position, area.sector.wiki_name()))
            else:
                f.write(u'|| The {} {} '.format(area.wiki_name(), area_type))

            if len(area.worlds) > 0:
                f.write('contains {:d} worlds with a population of'.format(area.stats.number))
                self.write_population(area.stats.population, f)
                popWorld = max(area.worlds, key=lambda w : w.population)
                f.write(' The highest population is ')
                self.write_population(popWorld.population, f)
                f.write(u', at {}.'.format(popWorld.wiki_name()))
                
                TLWorlds = [world for world in area.worlds if world.tl == area.stats.maxTL]
                if len(TLWorlds) == 1:
                    f.write(' The highest tech level is {} at {}.'.format(baseN(area.stats.maxTL,18), 
                                                                          TLWorlds[0].wiki_name()))
                elif len(TLWorlds) > 1:
                    f.write(' The highest tech level is {} at '.format(baseN(area.stats.maxTL,18))) 
                    TLWorlds = TLWorlds[0:6]
                    f.write (", ".join(w.wiki_name() for w in TLWorlds[:-1]))
                    f.write (", and {}".format(TLWorlds[-1].wiki_name()))
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
            else:
                f.write (' contains no charted worlds.')
                
            #There are seven naval bases in the subsector and four scout bases.
            f.write('\n')
            
    def write_world_statistics(self):
        onespace = ' '
        twospace = '  '
        for sector in self.galaxy.sectors:
            
            path = os.path.join(self.galaxy.output_path, sector.filename)
            with codecs.open (path, 'w+','utf-8') as f:
                f.write('{{pre|scroll|\n')
                f.write('# Generated by traveller-pyroute\n')
                f.write('# {}\n\n'.format(datetime.datetime.now()))
                f.write('# {}\n'.format(sector.name))
                f.write('# {},{}\n\n'.format(sector.x, sector.y))
                
                params = urllib.urlencode({'sector': sector, 'type': 'SecondSurvey'})
                url = 'http://www.travellermap.com/api/sec?%s' % params
                url.replace('=', '&63;')
                f.write('# Source: {}\n'.format(url))
                f.write('# Key: [[Trade_map_key]]\n\n')

                subsector = [sub for sub in sector.subsectors.itervalues()]
                subsector.sort(key=lambda sub : sub.position)
                for s in subsector:
                    f.write('# Subsector {}: {}\n'.format(s.position, s.name))
                f.write('\n')
                f.write('Hex  Name                 UWP       PBG   {Ix}   WTN GWP(BCr) Trade(BCr) Passengers   RU   Build Cap    Army  Port  SPA pop  \n')
                f.write('---- -------------------- --------- ---  ------- --- -------- ---------- ---------- ------ ----------- ------ ----  -------- \n')
                for star in sector.worlds:
                    f.write('{:5}'.format(star.position))
                    f.write(u'{:21}'.format(star.name))
                    f.write('{:10}'.format(star.uwp))
                    f.write('{:d}{:d}{:d}  '.format(star.popM, star.belts, star.ggCount))
                    f.write('{{ {:d} }}'.format(star.importance))
                    f.write(onespace if star.importance < 0 else twospace)
                    f.write('{:3d}'.format(star.wtn))
                    f.write('{:10,d}'.format(star.gwp))
                    f.write('{:10,d}'.format(star.tradeIn/1000000))
                    f.write('{:10,d}'.format(star.passIn))
                    f.write('{:8,d}'.format(star.ru))
                    f.write('{:11,d}'.format(star.ship_capacity))
                    f.write('{:8,d}'.format(star.raw_be))
                    f.write('{:6d}'.format(star.starportSize))
                    f.write('{:10,d}'.format(star.starportPop))
                    f.write('\n')
                f.write('}}\n[[Category:Sectors with sector data]]\n')

    def write_population(self, population, f):
            if population >= 1000 :
                f.write(' {:,d} billion.'.format(population/1000))
            elif population >= 1:
                f.write(' {:,d} million.'.format(population))
            else:
                f.write(' less than 1 million.')

def baseN(num,b,numerals="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])
        