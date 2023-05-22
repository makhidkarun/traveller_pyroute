"""
Created on May 21, 2023

@author: CyberiaResurrection
"""
import logging
import re
import codecs
import os
import ast
import itertools
import math
import networkx as nx

from PyRoute.DeltaDictionary import SectorDictionary, SubsectorDictionary
from PyRoute.Galaxy import Galaxy, Sector, Subsector, Allegiance
from PyRoute.Star import Star
from PyRoute.TradeCalculation import TradeCalculation, NoneCalculation, CommCalculation, XRouteCalculation, \
    OwnedWorldCalculation
from PyRoute.StatCalculation import ObjectStatistics
from PyRoute.AllyGen import AllyGen


class DeltaGalaxy(Galaxy):

    def read_sectors(self, sectors, pop_code, ru_calc):
        sector: SectorDictionary
        for sector_name in sectors:
            sector = sectors[sector_name]
            sec = Sector(" " + sector.name, sector.position)
            sec.filename = sector.filename

            # load up subsectors
            for subsector_name in sector:
                subsector: SubsectorDictionary = sector[subsector_name]
                subsec = Subsector(subsector.name, subsector.position, sec)
                sec.subsectors[subsector.position] = subsec

            # load up allegiances
            for allegiance_name in sector.allegiances:
                allegiance: Allegiance = sector.allegiances[allegiance_name]

                if allegiance_name not in self.alg:
                    self.alg[allegiance_name] = allegiance

            # once all that's done, load up the stars
            for line in sector.lines:
                if line.startswith('#') or len(line) < 20:
                    continue
                star = Star.parse_line_into_star(line, sec, pop_code, ru_calc)
                if star:
                    sec.worlds.append(star)
                    sec.subsectors[star.subsector()].worlds.append(star)
                    star.alg_base_code = AllyGen.same_align(star.alg_code)

                    self.set_area_alg(star, self, self.alg)
                    self.set_area_alg(star, sec, self.alg)
                    self.set_area_alg(star, sec.subsectors[star.subsector()], self.alg)

                    star.tradeCode.sophont_list.append("{}A".format(self.alg[star.alg_code].population))

            self.sectors[sec.name] = sec
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds)))

        self.set_bounding_sectors()
        self.set_bounding_subsectors()
        self.set_positions()
        self.logger.debug("Allegiances: {}".format(self.alg))
