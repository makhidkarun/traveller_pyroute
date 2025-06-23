"""
Created on May 21, 2023

@author: CyberiaResurrection
"""
import copy

from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.AreaItems.Sector import Sector
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, SubsectorDictionary
from PyRoute.Star import Star


class DeltaGalaxy(Galaxy):

    def read_sectors(self, sectors, pop_code, ru_calc,  # type: ignore
                     route_reuse, trade_choice, route_btn, mp_threads, debug_flag) -> None:
        self._set_trade_object(route_reuse, trade_choice, route_btn, mp_threads, debug_flag)
        star_counter = 0
        sector: SectorDictionary

        sectors.skip_void_subsectors()
        for sector_name in sectors:
            sector = sectors[sector_name]
            sec = Sector("# " + sector.name, sector.position)
            sec.filename = sector.filename

            # load up subsectors
            for subsector_name in sector:
                subsector: SubsectorDictionary = sector[subsector_name]
                subsec = Subsector(subsector.name, subsector.position, sec)
                sec.subsectors[subsector.position] = subsec

            # load up allegiances
            for allegiance_name in sector.allegiances:
                allegiance: Allegiance = copy.deepcopy(sector.allegiances[allegiance_name])

                if allegiance_name not in self.alg:
                    self.alg[allegiance_name] = allegiance

            # once all that's done, load up the stars
            for line in sector.lines:
                if line.startswith('#') or len(line) < 20:
                    continue
                star = Star.parse_line_into_star(line, sec, pop_code, ru_calc)
                if star:
                    star_counter = self.add_star_to_galaxy(star, star_counter, sec)

            self.sectors[sec.name] = sec
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds)))

        self.set_bounding_sectors()
        self.set_bounding_subsectors()
        self.set_positions()
        self.logger.debug("Allegiances: {}".format(self.alg))
