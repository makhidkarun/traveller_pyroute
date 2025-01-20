"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""
import os

from reportlab.lib.colors import toColor

from PyRoute.AreaItems.Galaxy import Galaxy

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.HexGrid import HexGrid
from PyRoute.Outputs.PDFMap import PDFMap
from PyRoute.Outputs.SectorMap import SectorMap


class ClassicModePDFSectorMap(PDFMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(ClassicModePDFSectorMap, self).__init__(galaxy, routes, output_path, writer)
        self.fonts['title'] = ('Times-Roman', 30)
        self.colours['grid'] = toColor('rgb(211, 211, 211)')
        self.colours['hexes'] = 'gray'

    def document(self, area_name: str, is_live=True):
        document = super(ClassicModePDFSectorMap, self).document(area_name, is_live)
        document.setCreator("ReportLab")
        if isinstance(area_name, Sector):
            title = "Sector " + str(area_name)
            area_name = area_name.name + " Sector"
            document.setTitle(title)
            path = os.path.join(self.output_path, f"{area_name}.pdf")
            document._filename = path

        return document

    def write_base_map(self, area: Sector):
        self.fill_background()
        self.area_name_title(area.name)
        self.subsector_grid()
        grid = HexGrid(self, self.start, self.hex_size, 32, 40)
        grid.hex_grid(grid.draw_all, 0.5, colour=self.colours['hexes'])

    def area_name_title(self, area_name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, 0.5)
        self.add_text_centred(area_name, cursor, 'title')

    def statistics(self, sector: Sector):
        return

    def map_key(self, area: Sector):
        return
