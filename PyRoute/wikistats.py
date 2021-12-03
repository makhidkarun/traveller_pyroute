"""
Created on Mar 22, 2014

@author: tjoneslo
"""
import os

import logging
import codecs
import datetime
import urllib.parse
import math
import inflect
import jsonpickle
from networkx.readwrite import json_graph
from Star import Nobles
from AllyGen import AllyGen
from jinja2 import Environment, FileSystemLoader, select_autoescape

class WikiStats(object):
    """
    classdocs
    """
    stat_header = '{| class=\"wikitable sortable\"\n!Sector!! X,Y !! Worlds ' + \
                  '!! Population (millions) !! Economy (Bcr) !! Per Capita (Cr) ' + \
                  '!! Trade Volume (BCr / year) !! Int. Trade (BCr / year) !! Ext. Trade (BCr/year) ' + \
                  '!! RU !! Shipyard Capacity (MTons) !! Colonial Army (BEs) ' + \
                  '!! Travellers (M / year) !! SPA Pop !! ETI worlds !! ETI Cargo (tons / year) !! ETI passengers (per year)\n'

    def __init__(self, galaxy, uwp, min_alg_count=10, match_alg='collapse', json_data=False, routes_generated=False):
        """
        Constructor
        """
        self.galaxy = galaxy
        self.uwp = uwp
        self.min_alg_count = min_alg_count
        self.plural = inflect.engine()
        self.match_alg = match_alg == 'collapse'
        self.json_data = json_data
        self.logger = logging.getLogger('PyRoute.WikiStats')

        cwd = os.path.dirname(__file__)
        templatedir = cwd + "/templates"

        self.env = Environment(
            loader=FileSystemLoader(templatedir),
            #loader=PackageLoader('PyRoute', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
            )

    def write_statistics(self):
        self.summary_statistics_template()
        self.sector_statistics_template()
        self.subsector_statistics_template()
        self.sector_data_template()
        self.allegiance_statistics_template()

        #self.top_summary()
        #self.tcs_statistics()
        #self.subsector_statistics()
        #self.write_allegiances(self.galaxy.alg)
        #self.write_worlds_wiki_stats()
        #self.write_sector_wiki()
        #self.write_world_statistics()

        self.write_summary_lists()
        if self.json_data:
            self.write_json()


    def output_template (self, template, filename, parameters):
        template = self.env.get_template(template)
        path = os.path.join(self.galaxy.output_path, filename)
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(template.render(parameters))

    def summary_statistics_template(self):
        self.output_template('summary.wiki', 'summary.wiki',
                             {'global_stats': self.galaxy.stats,
                              'sectors': self.galaxy.sectors,
                              'uwp': self.uwp,
                              'plural': self.plural,
                              'global_alg': self.galaxy.alg_sorted})

    def sector_statistics_template(self):
        self.output_template('sectors.wiki', 'sectors.wiki',
                             {'sectors': self.galaxy.sectors,
                              'global_stats': self.galaxy.stats,
                              'im_stats': self.galaxy.alg.get('Im', None),
                              'plural': self.plural})

    def subsector_statistics_template(self):
        self.output_template('subsectors.wiki', 'subsectors.wiki',
                             {'sectors': self.galaxy.sectors,
                              'plural': self.plural})
        
    def sector_data_template(self):
        for sector in self.galaxy.sectors.values():
            self.output_template('sector_data.wiki', sector.sector_name() + " Sector.sector.wiki",
                                  {"sector": sector})
            self.output_template('sector_econ.wiki', sector.sector_name() + " Sector.economic.wiki",
                                 {'sector': sector})

    def allegiance_statistics_template(self):
        self.output_template('allegiances.wiki', 'allegiances.wiki',
                             {"global_alg": self.galaxy.alg_sorted,
                              "global_stats": self.galaxy.stats,
                              "plural": self.plural,
                              "area": self.galaxy,
                              "min_alg_count": self.min_alg_count})

    def write_json(self):
        path = os.path.join(self.galaxy.output_path, 'galaxy.json')
        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=2)
        galaxy_json = jsonpickle.encode(self.galaxy, unpicklable=False, max_depth=14)
        with open(path, 'w+', encoding='utf8') as f:
            f.write(galaxy_json)
        for sector in self.galaxy.sectors.values():
            path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.sector.json")
            sector_json = jsonpickle.encode(sector, unpicklable=False, max_depth=14)
            with open(path, 'w+', encoding='utf8') as f:
                f.write(sector_json)
        path = os.path.join(self.galaxy.output_path, 'ranges.json')
        with open(path, "w+", encoding='utf8') as f:
            f.write(jsonpickle.encode(json_graph.node_link_data(self.galaxy.ranges)))

        path = os.path.join(self.galaxy.output_path, 'stars.json')
        with open(path, "w+", encoding='utf8') as f:
            f.write(jsonpickle.encode(json_graph.node_link_data(self.galaxy.stars)))
        
    def write_summary_lists(self):
        path = os.path.join(self.galaxy.output_path, 'sectors_list.txt')
        with open(path, 'w+') as f:
            for sector in self.galaxy.sectors.values():
                f.write('[[{} Sector/summary]]\n'.format(sector.sector_name()))

        path = os.path.join(self.galaxy.output_path, 'subsector_list.txt')
        with codecs.open(path, 'w+', 'utf-8') as f:
            for sector in self.galaxy.sectors.values():
                for subsector in sector.subsectors.values():
                    f.write('[[{} Subsector/summary]]\n'.format(subsector.name))


#########################################################################################################
# Unused functions
#########################################################################################################
    def summary_statistics(self):
        path = os.path.join(self.galaxy.output_path, 'summary.wiki')
        with codecs.open(path, 'w+', 'utf-8') as f:
            f.write('==Economic Summary==\n')
            f.write('===Statistical Analysis===\n')
            f.write(self.stat_header)
            for sector in self.galaxy.sectors.values():
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
            for sector in self.galaxy.sectors.values():
                f.write('==== {} Sector ====\n'.format(sector.sector_name()))
                self.text_area_long(f, "sector", sector)
                f.write('\n\n===== Polity Listing =====')
                allegiances_sorted = AllyGen.sort_allegiances(sector.alg, self.match_alg)
                self.logger.debug(
                    "Processing allegiance statistics for {} - {}\n Sorted: {}".format(sector.name, sector.alg,
                                                                                       allegiances_sorted))
                for allegiance in allegiances_sorted:
                    f.write('\n')
                    self.text_alg_statistics(f, "Allegiance", allegiance, sector)

        path = os.path.join(self.galaxy.output_path, 'sectors_list.txt')
        with open(path, 'w+') as f:
            for sector in self.galaxy.sectors.values():
                f.write('[[{} Sector/summary]]\n'.format(sector.sector_name()))

        path = os.path.join(self.galaxy.output_path, 'subsector_list.txt')
        with codecs.open(path, 'w+', 'utf-8') as f:
            for sector in self.galaxy.sectors.values():
                for subsector in sector.subsectors.values():
                    f.write('[[{} Subsector/summary]]\n'.format(subsector.name))

    def write_stats(self, f, stats):
        f.write('|align="right"|{:d}\n'.format(stats.number))
        f.write('|align="right"|{:,d}\n'.format(stats.population))
        f.write('|align="right"|{:,d}\n'.format(stats.economy))
        f.write('|align="right"|{:,d}\n'.format(stats.percapita))
        f.write('|align="right"|{:,d}\n'.format(int(stats.tradeVol // 1e9)))
        f.write('|align="right"|{:,d}\n'.format(int(stats.trade // 1e9)))
        f.write('|align="right"|{:,d}\n'.format(int(stats.tradeExt // 1e9)))
        f.write('|align="right"|{:,d}\n'.format(stats.sum_ru))
        f.write('|align="right"|{:,d}\n'.format(stats.shipyards))
        f.write('|align="right"|{:,.2f}\n'.format(stats.col_be))
        f.write('|align="right"|{:,d}\n'.format(stats.passengers // 1000000))
        f.write('|align="right"|{:,d}\n'.format(stats.spa_people))
        f.write('|align="right"|{:,d}\n'.format(stats.eti_worlds))
        f.write('|align="right"|{:,d}\n'.format(int(stats.eti_cargo * 50)))
        f.write('|align="right"|{:,d}\n'.format(int(stats.eti_pass * 50)))

    def top_summary(self):
        path = os.path.join(self.galaxy.output_path, 'top_summary.wiki')
        with codecs.open(path, 'w+', 'utf-8') as f:
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
            f.write('|Trade || {:,d} billion\n'.format(int(self.galaxy.stats.trade / 1e9)))
            f.write('\n|}\n')
            
            f.write('===Summary Report===\n')
            self.write_uwp_counts(f)
            f.write('|-\n|colspan=20 align=center|Percent by Population\n')
            self.write_uwp_populations(f)

    def write_allegiances(self, alg):
        path = os.path.join(self.galaxy.output_path, 'alleg_summary.wiki')
        with codecs.open(path, "wb", 'utf_8') as f:
            f.write('===Allegiance Information===\n')
            allegiances_sorted = AllyGen.sort_allegiances(alg, self.match_alg)
            self.logger.debug("Allegiances:  {}".format(allegiances_sorted))
            f.write('{| class=\"wikitable sortable\"\n!Code !! Name !! Worlds !! Population (millions) ' +
                    '!! Economy (BCr) !! Per Capita (Cr) !!  RU !! Shipyard Capacity (MTons) !! Armed Forces (BEs) !! SPA Population\n')
            for allegiance in allegiances_sorted:
                if allegiance.stats.number < self.min_alg_count:
                    continue
                f.write('|-\n| {} || {} '.format(allegiance.code, allegiance.wiki_name()))
                stats = allegiance.stats
                f.write('|| {:,d} '.format(stats.number))
                f.write('|| {:,d} '.format(stats.population))
                f.write('|| {:,d} '.format(stats.economy))
                f.write('|| {:,d} '.format(stats.percapita))
                f.write('|| {:,d} '.format(stats.sum_ru))
                f.write('|| {:,d} '.format(stats.shipyards))
                if AllyGen.are_allies('Im', allegiance):
                    f.write('|| {:,.2f} (IA) + {:,.2F} (CA)'.format(stats.im_be, stats.col_be))
                else:
                    f.write('|| {:,.2f}'.format(stats.col_be))
                f.write('|| {:,d}'.format(stats.spa_people))
                f.write('\n')
            f.write('|}\n')

            area_type = "Allegiance"
            f.write('=== {} Statistics ===\n'.format(area_type))
            for allegiance in allegiances_sorted:
                f.write('==== {} ====\n'.format(allegiance.name))
                self.text_alg_statistics(f, area_type, allegiance)
                f.write('\n')

    def write_uwp_counts(self, f):
        from StatCalculation import ObjectStatistics
        default_stats = ObjectStatistics()
        f.write('{|\n!Component')
        for x in range(18):
            f.write('||{}'.format(baseN(x, 18)))
        f.write('||I-Z')
        for name, values in self.uwp.uwp.items():
            f.write('\n|- \n| {}'.format(name))
            for x in range(18):
                index = baseN(x, 18)
                stats = self.uwp.uwp.get(name, {}).get(index, default_stats)
                value = stats.number
                f.write('||{}'.format(value))
            found = False
            for index, stats in values.items():
                if index not in '0123456789ABCDEFGH':
                    f.write('||{:d}'.format(stats.number))
                    found = True
                    break
            if not found:
                f.write('||0')
        f.write('\n')

    def write_uwp_populations(self, f):
        from StatCalculation import ObjectStatistics
        population = self.galaxy.stats.population
        default_stats = ObjectStatistics()
        f.write('|-\n!Component')
        for x in range(18):
            f.write('||{}'.format(baseN(x, 18)))
        f.write('||I-Z')

        for name, values in self.uwp.uwp.items():
            f.write('\n|- \n| {}'.format(name))
            for x in range(18):
                index = baseN(x, 18)
                stats = self.uwp.uwp.get(name, {}).get(index, default_stats)
                value = stats.population // (population // 100) if population > 0 else 0
                f.write('||{:d}%'.format(value))

            found = False
            for index, stats in values.items():
                if index not in '0123456789ABCDEFGH':
                    value = stats.population // (population // 100) if population > 0 else 0
                    f.write('||{:d}%'.format(value))
                    found = True
                    break
            if not found:
                f.write('||0%')
        f.write('\n|}')

    def tcs_statistics(self):
        path = os.path.join(self.galaxy.output_path, 'tcs_summary.wiki')
        with codecs.open(path, 'w+', 'utf-8') as f:
            f.write('=== TCS Military budgets by sector ===\n')
            f.write('budgets in BCr, capacity in MegaTons\n')
            f.write(
                '{| class=\"wikitable sortable\"\n!Sector!!X,Y!!Worlds !! Budget (BCr) !! Shipyard Capacity (MTons)\n')
            for sector in self.galaxy.sectors.values():
                budget = [star.budget // 1000 for star in sector.worlds]
                capacity = [star.ship_capacity // 1000000 for star in sector.worlds]
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
        with codecs.open(path, 'w+', 'utf-8') as f:
            f.write('=== Economic Summary by Subsector ===\n')
            f.write(self.stat_header)
            for sector in self.galaxy.sectors.values():
                subsectors = [s for s in sector.subsectors.values()]
                subsectors.sort(key=lambda s: s.position)
                for subsector in subsectors:
                    f.write('|-\n')
                    f.write('|{}\n'.format(subsector.wiki_title()))
                    f.write('|| {:d},{:d}: {}\n'.format(sector.x, sector.y, subsector.position))
                    self.write_stats(f, subsector.stats)
            f.write('|}\n')

            area_type = "Subsector"
            f.write('=== {} Statistics ===\n'.format(area_type))
            for sector in self.galaxy.sectors.values():
                subsectors = [s for s in sector.subsectors.values()]
                subsectors.sort(key=lambda s: s.position)
                for subsector in subsectors:
                    f.write('\n==== {} Subsector ====\n'.format(subsector.sector_name()))
                    self.text_area_long(f, "subsector", subsector)
                    f.write('\n\n===== Polity Listing =====')
                    allegiances_sorted = AllyGen.sort_allegiances(subsector.alg, self.match_alg)
                    for allegiance in allegiances_sorted:
                        f.write('\n')
                        self.text_alg_statistics(f, "subsector", allegiance, subsector)

    # This sector has <N> worlds, of which <N> have native gas giants.
    # The estimated population for the sector is <N size> sapients (not necessarily humans).
    # There are <N> Agricultural (Ag) worlds versus <N> Non-Agricultural (Na) worlds.
    # There are <N> Non-Industrial (Ni) Worlds versus <N> Industrial (In) worlds.
    # There are <N> Rich (Ri) worlds versus <N> Poor (Po) worlds.
    # There are <N> Water Worlds (Wa), <N> Ice-Capped worlds (Ic), <N> Desert worlds (De), and <N> Vacuum (Va) worlds.
    # There are <N> High Population (Hi) worlds versus <N> Low Population (Lo) worlds.
    # There are <N> Asteroid Belts (As) in the sector.
    # There are <N> Barren (Ba) worlds.
    # There are <N> naval bases in the <area>, <N> scout bases, and <N> way stations.
    # In <area> there are <N> race homeworlds.
    # The highest population world in the sector is {{WorldS|Saazi (Antares 0533)}}; the lowest population world is {{WorldS|Lampigas}}
    # The average tech level in the sector is 6 (most lie between 3 and 9).

    def text_area_long(self, f, area_type, area):
        if area_type == 'subsector':
            f.write('{}, {} {} of {} '.format(area.wiki_name(), area_type,
                                                  area.position, area.sector.wiki_name()))
        else:
            f.write('The {} {} '.format(area.wiki_name(), area_type))

        if len(area.worlds) == 0:
            f.write('contains no charted worlds.\n')
            return

        f.write('has {:d} worlds, of which {:d} have native gas giants. The {} has an '.format(area.stats.number,
                                                                                                area.stats.gg_count,
                                                                                                area_type))

        self.text_area_populations(f, area)

        worlds = []
        worlds.append(self.get_count(area.stats.code_counts.get('Hi', 0), 'world', True, ' High population (Hi)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Ph', 0), 'world', False, ' Moderate population (Ph)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Ni', 0), 'world', False, ' Non-industrial (Ni)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Lo', 0), 'world', False, ' Low population (Lo)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Ba', 0), 'world', False, ' Barren (Ba)'))
        f.write('There {}. '.format(self.plural.join(worlds)))

        f.write('There ')
        self.write_count(f, area.stats.code_counts.get('Ag', 0), 'world', True, ' Agricultural (Ag)')
        f.write(' versus ')
        self.write_count(f, area.stats.code_counts.get('Pa', 0), 'world', False, ' Pre-Agricultural (Pa)')
        f.write(', and ')
        self.write_count(f, area.stats.code_counts.get('Na', 0), 'world', False, ' Non-Agricultural (Na)')
        f.write('. ')

        f.write('There ')
        self.write_count(f, area.stats.code_counts.get('Ri', 0), 'world', True, ' Rich (Ri)')
        f.write(' versus ')
        self.write_count(f, area.stats.code_counts.get('In', 0), 'world', False, ' Industrial (In)')
        f.write('. ')

        worlds = []
        worlds.append(self.get_count(area.stats.code_counts.get('As', 0), 'belt', True, ' Asteroid (As)'))
        worlds.append(self.get_count(area.stats.code_counts.get('De', 0), 'world', False, ' Desert (De)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Ga', 0), 'world', False, ' Garden (Ga)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Ic', 0), 'world', False, ' Ice-capped (Ic)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Po', 0), 'world', False, ' Poor (Po)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Va', 0), 'world', False, ' Vacuum (Va)'))
        worlds.append(self.get_count(area.stats.code_counts.get('Wa', 0) + area.stats.code_counts.get('Oc', 0),
                                     'world', False, ' Water (Wa) or Ocean (Oc)'))

        f.write('There {}. '.format(self.plural.join(worlds)))

        f.write('There ')
        self.write_count(f, area.stats.naval_bases, 'Naval base')
        f.write(' in the {}, '.format(area_type))
        self.write_count(f, area.stats.scout_bases, 'Scout base', False)
        f.write(', and ')
        self.write_count(f, area.stats.way_stations, 'Way station', False)
        f.write('. ')

        homeworlds = [world for world in area.worlds if world.tradeCode.homeworld]
        if len(homeworlds) > 0:
            f.write('In {} there '.format(area.wiki_name()))
            self.write_count(f, len(homeworlds), 'race homeworld', True)
            f.write('. ')

        nobles = Nobles()
        for world in area.worlds:
            nobles.accumulate(world.nobles)
        if nobles.nobles['Knights'] > 0:
            nlist = []
            nlist.append(self.get_count(nobles.nobles['Knights'], 'Knight', False))
            nlist.append(self.get_count(nobles.nobles['Baronets'], 'Baronet', False))
            nlist.append(self.get_count(nobles.nobles['Barons'], 'Baron', False))
            nlist.append(self.get_count(nobles.nobles['Marquis'], 'Marquis', False))
            nlist.append(self.get_count(nobles.nobles['Viscounts'], 'Viscount', False))
            nlist.append(self.get_count(nobles.nobles['Counts'], 'Count', False))
            nlist.append(self.get_count(nobles.nobles['Dukes'], 'Duke', False))
            if nobles.nobles['Sector Dukes'] > 0:
                nlist.append(self.get_count(nobles.nobles['Sector Dukes'], 'Subsector Duke', False))
            if nobles.nobles['Archdukes'] > 0:
                nlist.append(self.get_count(nobles.nobles['Archdukes'], 'Archduke', False))
            f.write('The Imperial nobility includes {}'.format(self.plural.join(nlist)))
            if nobles.nobles['Emperor'] > 0:
                f.write(' along with the Emperor. ')
            else:
                f.write('. ')

        self.text_area_pop_tl(f, area_type, area)

    def text_area_populations(self, f, area):
        f.write('estimated population of ')
        f.write(self.write_population(area.stats.population))
        sophonts = ["{}: {}".format(code, self.write_population(pop)) for (code, pop)
                    in area.stats.pop_groups.items()]
        f.write(' (')
        f.write(", ".join(sophonts))
        f.write('). ')

    def text_alg_statistics(self, f, area_type, area, contain=None):
        if AllyGen.is_unclaimed(area.code):
            outString = 'There '
            outString += self.get_count(area.stats.number, 'system', True, ' unclaimed or unexplored')
            if contain:
                outString += ' in {}.'.format(contain.wiki_name())
            else:
                outString += '.'
            f.write(outString)
        else:
            outString = 'The {}'.format(area.wiki_name())
            if area.code[0:2] == 'Na' or area.code in ['Wild', 'VaEx', 'Va']:
                outString += ' worlds{} encompasses '.format(' in ' + contain.wiki_name() if contain else "")
            elif area.code[0:2] == 'Cs':
                outString += '{} encompasses '.format(' in ' + contain.wiki_name() if contain else "")
            else:
                outString += '{} has jurisdiction over '.format(' in ' + contain.wiki_name() if contain else "")

            f.write(outString)
            if contain and contain.stats.number == len(area.worlds):
                f.write('all of the worlds. ')
                self.text_area_capitals(f, area_type, area)
            elif len(area.worlds) > 0:
                self.write_count(f, area.stats.number, 'world', False)
                f.write(' with an ')
                self.text_area_populations(f, area)

                f.write('The economy is BCr{:,d} and a per capita income of Cr{:,d}. '.format(area.stats.economy,
                                                                                              area.stats.percapita))

                if area.stats.population > 0:
                    self.text_area_pop_tl(f, area_type, area)
                    self.text_area_capitals(f, area_type, area)
            else:
                f.write(' no charted worlds.')
        f.write('\n')

    def text_area_pop_tl(self, f, area_type, area):
        PopWorlds = [world for world in area.worlds if world.popCode == area.stats.maxPop]
        if len(PopWorlds) == 1:
            f.write('The highest population world is {}. '.format(PopWorlds[0].wiki_name()))
        elif len(PopWorlds) > 1:
            PopWorlds.sort(key=lambda star: star.popM, reverse=True)
            maxPopM = PopWorlds[0].popM
            PopWorlds = [world.wiki_name() for world in PopWorlds if world.popM == maxPopM]
            PopWorlds = PopWorlds[0:6]

            self.plural.num(len(PopWorlds))
            f.write(self.plural.inflect("The highest population plural('world') plural_verb('is') {}. ".
                                        format(self.plural.join(PopWorlds))))
            self.plural.num()

        TLWorlds = [world for world in area.worlds if world.tl == area.stats.maxTL]
        TLWorlds = TLWorlds[0:6]
        TLWorlds = [t.wiki_name() for t in TLWorlds]
        f.write('The highest tech level is {} at {}. '.format(baseN(area.stats.maxTL, 18),
                                                               self.plural.join(TLWorlds)))

        TLList = [world.tl for world in area.worlds]
        if len(TLList) > 3:
            mean = sum(TLList) / len(TLList)
            TLVar = [math.pow(tl - mean, 2) for tl in TLList]
            stddev = math.sqrt(sum(TLVar) / len(TLVar))
            f.write('The average technology level is {:d}'.format(int(mean)))
            f.write(' (with most between {:d} and {:d}). '.format(max(int(mean - stddev), 0), int(mean + stddev)))

    def text_area_capitals(self, f, area_type, area):
        subsectorCp = [world for world in area.worlds if world.tradeCode.subsector_capital]
        sectorCp = [world for world in area.worlds if world.tradeCode.sector_capital]
        capital = [world for world in area.worlds if world.tradeCode.other_capital]

        lead = "\n* " if area_type == 'sector' or area_type == 'Allegiance' else ""

        if len(capital) > 0:
            for world in capital:
                alg = self.galaxy.alg[AllyGen.same_align(world.alg)]
                f.write('{}The capital of {} is {}.'.format(lead, alg.wiki_name(), world.wiki_name()))

        if len(sectorCp) > 0:
            for world in sectorCp:
                alg = self.galaxy.alg[AllyGen.same_align(world.alg)]
                f.write('{}The sector capital of {} is {}.'.format(lead, alg.wiki_name(), world.wiki_name()))

        if 0 < len(subsectorCp) < 17:
            for world in subsectorCp:
                alg = self.galaxy.alg[AllyGen.same_align(world.alg)]
                subsector = world.sector.subsectors[world.subsector()]
                if area_type == 'sector' or area_type == 'Allegiance':
                    f.write(
                        '{}The {} subsector capital of {} is {}.'.format(lead, alg.wiki_name(), subsector.wiki_name(),
                                                                          world.wiki_name()))
                # if area_type == 'subsector':
                else:
                    f.write('{}The subsector capital is {}.'.format(lead, world.wiki_name()))

    def write_sector_wiki(self):
        for sector in self.galaxy.sectors.values():
            path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.sector.wiki")
            with codecs.open(path, 'w+', 'utf-8') as f:
                f.write('<section begin="header"/>\n')
                f.write('{| class="wikitable sortable" width="90%"\n')
                f.write('|+ {} sector data\n'.format(sector.sector_name()))
                f.write('!Hex!!Name!!UWP!!Remarks!!{Ix}!!(Ex)!![Cx]!!Noble!!Base!!Zone!!PBG!!Worlds!!Alg!!Stellar')
                f.write('<section end="header"/>')
                for subsector in sector.subsectors.values():
                    f.write('<section begin="{}"/>\n'.format(subsector.name))
                    for star in subsector.worlds:
                        f.write('|-\n')
                        f.write('|{:5}'.format(star.position))
                        f.write('||[[{:21}|]]'.format(star.wiki_short_name()))
                        f.write('||{:10}'.format(star.uwp))
                        f.write('||{}'.format(star.tradeCode))
                        f.write('||{{{:d}}}'.format(star.importance))
                        f.write('||{}'.format(star.economics))
                        f.write('||{}'.format(star.social))
                        f.write('||{}'.format(star.nobles))
                        f.write('||{}'.format(star.baseCode))
                        f.write('||{}'.format(star.zone))
                        f.write('||{:d}{:d}{:d}'.format(star.popM, star.belts, star.ggCount))
                        f.write('||{:d}'.format(star.worlds))
                        f.write('||{}'.format(star.alg))
                        f.write('||{}'.format(star.stars))
                        f.write('\n')
                    f.write('<section end="{}"/>'.format(subsector.name))
                f.write('\n|}\n[[Category:Sectors with sector data]]\n')

    def write_worlds_wiki_stats(self):
        for sector in self.galaxy.sectors.values():
            path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.economic.wiki")
            with codecs.open(path, 'w+', 'utf-8') as f:
                f.write('<section begin="header"/>\n')
                f.write('{| class="wikitable sortable" width="90%"\n')
                f.write('|+ {} economic data\n'.format(sector.sector_name()))
                f.write('!Hex!!Name!!UWP!!PBG!!{Ix}!!WTN!!MSPR!!RU!!Per Capita (Cr)!!GWP (BCr)!!Trade (MCr/year)' +
                        '!!Passengers (per year)!!Build!!Army!!Port!!SPA Population' +
                        '!!ETI Index!!ETI Pass Index!!ETI worlds!!ETI Cargo (tons/year)!!ETI Passengers (per year)' +
                        '!!Trade Goods' +
                        '!!Subsector\n')
                f.write('<section end="header"/>')
                for subsector in sector.subsectors.values():
                    f.write('<section begin="{}"/>\n'.format(subsector.name))
                    for star in subsector.worlds:
                        f.write('|-\n')
                        f.write('|{:5}'.format(star.position))
                        f.write('||[[{:21}|]]'.format(star.wiki_short_name()))
                        f.write('||{:10}'.format(star.uwp))
                        f.write('||{:d}{:d}{:d}  '.format(star.popM, star.belts, star.ggCount))
                        f.write('||{{ {:d} }}'.format(star.importance))
                        f.write('||{:3d}'.format(star.wtn))
                        f.write('||{:d}'.format(star.mspr))
                        f.write('||{:8,d}'.format(star.ru))
                        f.write('||{:10,d}'.format(star.perCapita))
                        f.write('||{:10,d}'.format(star.gwp))
                        f.write('||{:10,d}'.format(star.tradeIn // 1000000))
                        f.write('||{:10,d}'.format(star.passIn))
                        f.write('||{:11,d}'.format(star.ship_capacity))
                        f.write('||{:8,d}'.format(star.raw_be))
                        f.write('||{:6d}'.format(star.starportSize))
                        f.write('||{:10,d}'.format(star.starportPop))
                        f.write('||{:d}'.format(star.eti_cargo))
                        f.write('||{:d}'.format(star.eti_passenger))
                        f.write('||{:10,d}'.format(star.eti_worlds))
                        f.write('||{:10,d}'.format(int(star.eti_cargo_volume * 50)))
                        f.write('||{:10,d}'.format(int(star.eti_pass_volume * 50)))
                        f.write('||{}'.format(star.trade_id))
                        f.write('||{}'.format(subsector.wiki_name()))
                        f.write('\n')
                    f.write('<section end="{}"/>'.format(subsector.name))
                f.write('\n|}\n[[Category:Sectors with sector economic data]]\n')

    def write_world_statistics(self):
        onespace = ' '
        twospace = '  '
        for sector in self.galaxy.sectors.values():

            path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.sec")
            with codecs.open(path, 'w+', 'utf-8') as f:
                f.write('{{pre|scroll|\n')
                f.write('2=# Generated by traveller-pyroute\n')
                f.write('# {}\n\n'.format(datetime.datetime.now()))
                f.write('# {}\n'.format(sector.name))
                f.write('# {},{}\n\n'.format(sector.x, sector.y))

                params = urllib.parse.urlencode({'sector': sector.sector_name(), 'type': 'SecondSurvey'})
                url = 'http://www.travellermap.com/api/sec?%s' % params
                url.replace('=', '&63;')
                f.write('# Source: {}\n'.format(url))
                f.write('# Key: [[Trade_map_key]]\n\n')

                subsector = [sub for sub in sector.subsectors.values()]
                subsector.sort(key=lambda sub: sub.position)
                for s in subsector:
                    f.write('# Subsector {}: {}\n'.format(s.position, s.name))
                f.write('\n')
                f.write(
                    'Hex  Name                 UWP       PBG   {Ix}   WTN GWP(BCr) Trade(BCr) Passengers   RU   Build Cap    Army  Port  SPA pop  \n')
                f.write(
                    '---  -------------------- --------- ---  ------- --- -------- ---------- ---------- ------ ----------- ------ ----  -------- \n')
                for star in sector.worlds:
                    f.write('{:5}'.format(star.position))
                    f.write('{:21}'.format(star.name))
                    f.write('{:10}'.format(star.uwp))
                    f.write('{:d}{:d}{:d}  '.format(star.popM, star.belts, star.ggCount))
                    f.write('{{ {:d} }}'.format(star.importance))
                    f.write(onespace if star.importance < 0 else twospace)
                    f.write('{:3d}'.format(star.wtn))
                    f.write('{:10,d}'.format(star.gwp))
                    f.write('{:10,d}'.format(star.tradeIn // 1000000))
                    f.write('{:10,d}'.format(star.passIn))
                    f.write('{:8,d}'.format(star.ru))
                    f.write('{:11,d}'.format(star.ship_capacity))
                    f.write('{:8,d}'.format(star.raw_be))
                    f.write('{:6d}'.format(star.starportSize))
                    f.write('{:10,d}'.format(star.starportPop))
                    f.write('\n')
                f.write('}}\n[[Category:Sectors with sector data]]\n')

    def get_count(self, count, text, is_are=True, lead_text=""):
        self.plural.num(count)
        c_text = self.plural.number_to_words(count, zero='no', threshold=10)
        if is_are:
            string = self.plural.inflect("plural_verb('is') {0}{1} plural('{2}')".format(c_text, lead_text, text))
        else:
            string = self.plural.inflect("{0}{1} plural('{2}')".format(c_text, lead_text, text))

        self.plural.num()
        return string

    def write_count(self, f, count, text, is_are=True, lead_text=""):
        f.write(self.get_count(count, text, is_are, lead_text))

    def write_population(self, population):
        if population >= 1000:
            return '{:,d} billion'.format(population // 1000)
        elif population >= 1:
            return '{:,d} million'.format(population)
        else:
            return 'less than 1 million'


def baseN(num, b, numerals="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])
