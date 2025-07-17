"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""
import logging
import os

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import toColor

from AreaItems.Galaxy import Galaxy
from Star import Star

from AreaItems.Sector import Sector
from Outputs.Cursor import Cursor
from Outputs.HexGrid import HexGrid
from Outputs.PDFMap import PDFMap
from Outputs.SectorMap import SectorMap
from StatCalculation import StatCalculation


class ClassicModePDFSectorMap(PDFMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(ClassicModePDFSectorMap, self).__init__(galaxy, routes, output_path, writer)
        self.fonts['title'] = ('Times-Roman', 30)
        self.fonts['system_name'] = ('Times-Roman', 4)
        self.fonts['system_port'] = ('Times-Roman', 4)
        self.fonts['system_uwp'] = ('Times-Roman', 4)
        self.colours['grid'] = toColor('rgb(211, 211, 211)')  # type: ignore
        self.colours['hexes'] = 'gray'
        self.colours['comm'] = toColor('rgb(102, 178, 102)')  # type: ignore

    def document(self, area_name: str, is_live=True) -> Canvas:
        document = super(ClassicModePDFSectorMap, self).document(area_name, is_live)
        document.setCreator("ReportLab")
        if isinstance(area_name, Sector):
            title = "Sector " + str(area_name)
            area_name = area_name.name + " Sector"
            document.setTitle(title)
            path = os.path.join(self.output_path, f"{area_name}.pdf")
            document._filename = path  # type:ignore[attr-defined]

        return document

    def write_base_map(self, area: Sector) -> None:  # type: ignore[override]
        self.fill_background()
        self.area_name_title(area.name)
        self.subsector_grid()
        grid = HexGrid(self, self.start, self.hex_size, 32, 40, legacy=True)
        grid.hex_grid(grid.draw_all, 0.5, colour=self.colours['hexes'])

    def area_name_title(self, area_name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, 0.9)
        self.add_text_centred(area_name, cursor, 'title')

    def draw_borders(self, sector: Sector) -> None:  # type: ignore[override]
        grid = HexGrid(self, self.start, self.hex_size, 32, 40, legacy=True)
        grid.set_borders(self.galaxy.borders, sector.dx, sector.dy)
        grid.hex_grid(grid.draw_borders, 1.5, colour=self.colours['hexes'])

    def statistics(self, sector: Sector) -> None:
        return

    def map_key(self, area: Sector) -> None:
        return

    def comm_line(self, start: Star, end: Star, sector: Sector) -> None:
        colour = self.colours['comm']
        assert self.system_writer is not None

        start_cursor = self.system_writer.location(start.hex)
        start_cursor.y_plus(self.hex_size.y)
        pos = end.hex
        if end.sector != sector:
            endRow = end.hex.row
            endCol = end.hex.col

            if end.sector.x < sector.x:
                endCol -= 32
            if end.sector.x > sector.x:
                endCol += 32
            if end.sector.y < sector.y:
                endRow += 40
            if end.sector.y > sector.y:
                endRow -= 40
            pos = f"{endCol}{endRow}"

        end_cursor = self.system_writer.location(pos)
        end_cursor.y_plus(self.hex_size.y)
        clip_start, clip_end = self.line_clipping(start_cursor, end_cursor)
        self.add_line(clip_start, clip_end, colour, stroke='solid', width=3)

    def trade_line(self, start: Star, end: Star, sector: Sector, data: dict) -> None:
        colour, scheme = self._trade_line_setup(data)
        if colour is None:
            return
        assert self.system_writer is not None

        start_cursor = self.system_writer.location(start.hex)
        start_cursor.y_plus(self.hex_size.y)
        pos = end.hex
        if end.sector != sector:
            endRow = end.hex.row
            endCol = end.hex.col

            if end.sector.x < sector.x:
                endCol -= 32
            if end.sector.x > sector.x:
                endCol += 32
            if end.sector.y < sector.y:
                endRow += 40
            if end.sector.y > sector.y:
                endRow -= 40
            pos = f"{endCol:02d}{endRow:02d}"

        end_cursor = self.system_writer.location(pos)
        end_cursor.y_plus(self.hex_size.y)
        clip_start, clip_end = self.line_clipping(start_cursor, end_cursor)
        self.add_circle(clip_start, 3, 1, True, scheme)
        if end.sector == start.sector:
            self.add_circle(clip_end, 3, 1, True, scheme)
        self.add_line(clip_start, clip_end, colour, stroke='solid', width=1)

    def _trade_line_setup(self, data):
        trade_colours = [(255, 0, 0),  # Red
                         (224, 224, 16),  # yellow - darker
                         (0, 255, 0),  # green
                         (0, 255, 255),  # Cyan
                         (96, 96, 255),  # blue - lighter
                         (128, 0, 128),  # purple
                         (148, 0, 211),  # violet
                         ]
        trade = StatCalculation.trade_to_btn(data['trade']) - self.galaxy.min_btn
        if trade < 0:
            return None
        if trade > 6:
            logging.getLogger('PyRoute.Outputs.ClassicModePDFSectorMap').warning("trade calculated over %d" % (self.galaxy.min_btn + 6))
            trade = 6
        trade_colour = trade_colours[trade]
        trade_string = "rgb" + str(trade_colour)
        trade_colour = toColor(trade_string)
        key = "trade" + str(trade)
        if key not in self.colours:
            self.colours[key] = trade_colour
        return trade_colour, key

    def coreward_name(self, name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, self.start.y - 13)
        self.add_text_centred(name, cursor, 'sector')

    def spinward_name(self, name: str) -> None:
        y = 390
        cursor = Cursor(self.start.x - 5, y)
        self.add_text_rotated(name, cursor, 'sector', 90)

    def trailing_name(self, name: str) -> None:
        y = 421
        x = 598

        cursor = Cursor(x, y)
        self.add_text_rotated(name, cursor, 'sector', -90)

    def rimward_name(self, name: str) -> None:
        cursor = Cursor(306, self.image_size.y - 13)
        self.add_text(name, cursor, 'sector')

    def line_clipping(self, start_cursor, end_cursor) -> tuple[Cursor, Cursor]:
        clip_start, clip_end = super(ClassicModePDFSectorMap, self).line_clipping(start_cursor, end_cursor)
        if 790 == clip_end.y:
            dy_offset = 10
            orig_dx = clip_end.x - clip_start.x
            orig_dy = clip_end.y - clip_start.y
            fraction = (orig_dy - dy_offset) / orig_dy
            new_dx = (orig_dx * fraction)
            clip_end.x_plus(new_dx - orig_dx)
            clip_end.y_plus(-dy_offset)
        if 603 == clip_end.x:
            dx_offset = 3
            orig_dx = clip_end.x - clip_start.x
            orig_dy = clip_end.y - clip_start.y
            fraction = (orig_dx - dx_offset) / orig_dx
            new_dy = (orig_dy * fraction)
            clip_end.x_plus(-dx_offset)
            clip_end.y_plus(new_dy - orig_dy)
        return clip_start, clip_end
