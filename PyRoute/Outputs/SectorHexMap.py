"""
Created on Aug 05, 2024

@author: CyberiaResurrection
"""
import logging

from PyRoute.Outputs.Map import Map
from StatCalculation import StatCalculation


class SectorHexMap(Map):

    def comm_line(self, pdf, edge):
        raise NotImplementedError("Base Class")

    def _setup_sector_pdf_map(self, gal_sector, is_live):
        pdf_doc = self.document(gal_sector, is_live)
        self.write_base_map(pdf_doc, gal_sector)
        self.draw_borders(pdf_doc, gal_sector)
        worlds = [item.index for item in gal_sector.worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(worlds, True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]
        return comm_routes, pdf_doc, worlds

    def _sector_map_comm_and_trade_routes(self, comm_routes, pdf_doc, worlds):
        for (star, neighbor, data) in comm_routes:
            srcstar = self.galaxy.star_mapping[star]
            trgstar = self.galaxy.star_mapping[neighbor]
            self.comm_line(pdf_doc, [srcstar, trgstar])
        sector_trade = [star for star in self.galaxy.stars.edges(worlds, True)
                        if star[2]['trade'] > 0 and StatCalculation.trade_to_btn(star[2]['trade']) >= self.min_btn]
        logging.getLogger('PyRoute.HexMap').debug("Worlds with trade: {}".format(len(sector_trade)))
        sector_trade.sort(key=lambda line: line[2]['trade'])
        for (star, neighbor, data) in sector_trade:
            self.galaxy.stars[star][neighbor]['trade btn'] = StatCalculation.trade_to_btn(data['trade'])
            srcstar = self.galaxy.star_mapping[star]
            trgstar = self.galaxy.star_mapping[neighbor]
            self.trade_line(pdf_doc, [srcstar, trgstar], data)

    def _sector_map_systems_and_sectors(self, gal_sector, pdf_doc):
        for star in gal_sector.worlds:
            self.system(pdf_doc, star)
        if gal_sector.coreward:
            self.coreward_sector(pdf_doc, gal_sector.coreward.name)
        if gal_sector.rimward:
            self.rimward_sector(pdf_doc, gal_sector.rimward.name)
        if gal_sector.spinward:
            self.spinward_sector(pdf_doc, gal_sector.spinward.name)
        if gal_sector.trailing:
            self.trailing_sector(pdf_doc, gal_sector.trailing.name)
