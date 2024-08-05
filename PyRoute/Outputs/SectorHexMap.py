"""
Created on Aug 05, 2024

@author: CyberiaResurrection
"""
from PyRoute.Outputs.Map import Map


class SectorHexMap(Map):

    def _setup_sector_pdf_map(self, gal_sector, is_live):
        pdf_doc = self.document(gal_sector, is_live)
        self.write_base_map(pdf_doc, gal_sector)
        self.draw_borders(pdf_doc, gal_sector)
        worlds = [item.index for item in gal_sector.worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(worlds, True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]
        return comm_routes, pdf_doc, worlds
