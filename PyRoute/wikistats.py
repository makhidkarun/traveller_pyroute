"""
Created on Mar 22, 2014

@author: tjoneslo
"""
import os

import logging
import codecs
import inflect
import jsonpickle  # type:ignore[import-untyped]
from networkx.readwrite import json_graph
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
            # loader=PackageLoader('PyRoute', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
            )

    def write_statistics(self) -> None:
        self.summary_statistics_template()
        self.sector_statistics_template()
        self.subsector_statistics_template()
        self.sector_data_template()
        self.allegiance_statistics_template()

        # self.top_summary()
        # self.tcs_statistics()
        # self.subsector_statistics()
        # self.write_allegiances(self.galaxy.alg)
        # self.write_worlds_wiki_stats()
        # self.write_sector_wiki()
        # self.write_world_statistics()

        self.write_summary_lists()
        if self.json_data:
            self.write_json()

    def output_template(self, template, filename, parameters) -> None:
        template = self.env.get_template(template)
        path = os.path.join(self.galaxy.output_path, filename)
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(template.render(parameters))

    def summary_statistics_template(self) -> None:
        self.output_template('summary.wiki', 'summary.wiki',
                             {'global_stats': self.galaxy.stats,
                              'sectors': self.galaxy.sectors,
                              'uwp': self.uwp,
                              'plural': self.plural,
                              'global_alg': self.galaxy.alg_sorted})

    def sector_statistics_template(self) -> None:
        self.output_template('sectors.wiki', 'sectors.wiki',
                             {'sectors': self.galaxy.sectors,
                              'global_stats': self.galaxy.stats,
                              'im_stats': self.galaxy.alg.get('Im', None),
                              'plural': self.plural})

    def subsector_statistics_template(self) -> None:
        self.output_template('subsectors.wiki', 'subsectors.wiki',
                             {'sectors': self.galaxy.sectors,
                              'plural': self.plural})

    def sector_data_template(self) -> None:
        for sector in self.galaxy.sectors.values():
            self.output_template('sector_data.wiki', sector.sector_name() + " Sector.sector.wiki",
                                  {"sector": sector})
            self.output_template('sector_econ.wiki', sector.sector_name() + " Sector.economic.wiki",
                                 {'sector': sector})

    def allegiance_statistics_template(self) -> None:
        self.output_template('allegiances.wiki', 'allegiances.wiki',
                             {"global_alg": self.galaxy.alg_sorted,
                              "global_stats": self.galaxy.stats,
                              "plural": self.plural,
                              "area": self.galaxy,
                              "min_alg_count": self.min_alg_count})

    def write_json(self) -> None:
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

    def write_summary_lists(self) -> None:
        path = os.path.join(self.galaxy.output_path, 'sectors_list.txt')
        with open(path, 'w+', encoding="utf-8") as f:
            for sector in self.galaxy.sectors.values():
                f.write('[[{} Sector/summary]]\n'.format(sector.sector_name()))

        path = os.path.join(self.galaxy.output_path, 'subsector_list.txt')
        with codecs.open(path, 'w+', encoding="utf-8") as f:
            for sector in self.galaxy.sectors.values():
                for subsector in sector.subsectors.values():
                    f.write('[[{} Subsector/summary]]\n'.format(subsector.name))


def baseN(num, b, numerals="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])
