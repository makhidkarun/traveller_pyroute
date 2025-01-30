import os

from PIL import Image, ImageFont

from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.GraphicMap import GraphicMap
from PyRoute.Outputs.HexGrid import HexGrid
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector


class SubsectorMap(GraphicMap):
    positions = {'A': (0, 0), 'B': (-8, 0), 'C': (-16, 0), 'D': (-24, 0),
                 'E': (0, -10), 'F': (-8, -10), 'G': (-16, -10), 'H': (-24, -10),
                 'I': (0, -20), 'J': (-8, -20), 'K': (-16, -20), 'L': (-24, -20),
                 'M': (0, -30), 'N': (-8, -30), 'O': (-16, -30), 'P': (-24, -30)}

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str):
        super(SubsectorMap, self).__init__(galaxy, routes, output_path, "")
        self.output_suffix = " Subsector"
        self.image_size = Cursor(826, 1272)
        self.start = Cursor(56, 56)
        self.hex_size = Cursor(28, 48)

        self.colours['background'] = 'black'
        self.fonts['title'] = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 48)

    def write_maps(self) -> None:
        maps = len(self.galaxy.sectors) * 16
        self.logger.info(f"writing {maps} subsector maps...")

        for sector in self.galaxy.sectors.values():
            for subsector in sector.subsectors.values():
                self.subsector = subsector
                if subsector.name is None or '' == subsector.name:
                    # Assign a default name to stop file writes blowing up
                    subsector.name = sector.name + "-" + subsector.position
                self.write_subsector_map(subsector)

    def write_subsector_map(self, subsector: Subsector) -> None:
        self.doc = self.document(subsector.name + " Subsector", True)
        self.write_base_map(subsector)
        self.close()

    def close(self) -> None:
        path = os.path.join(self.galaxy.output_path, self.area_name + ".png")
        self.image = self.image.resize((413, 636), Image.BICUBIC)
        self.image.save(path)

    def write_base_map(self, area: Subsector):
        self.fill_background()
        self.subsector_grid()
        grid = HexGrid(self, self.start, self.hex_size, 8, 10)
        grid.hex_grid(grid.draw_all, 1, colour=self.colours['hexes'])


    def fill_background(self):
        background = self.colours['background']
        if background:
            start_cursor = Cursor(self.start.x - 14, self.start.y - 12)
            end_cursor = Cursor(611, self.start.y + self.hex_size.x + 21 + (180 * 4))
            self.add_rectangle(start_cursor, end_cursor, background, background, 1)

    def subsector_grid(self):
        sector = self.subsector.sector
        pos = Cursor(20, 1140)
        name = self.subsector.name + " / " + sector.name
        font = self.get_font('title')

        width, height = self._get_text_size(font, name)
        size = (width, height)
        if size[0] > 680:
            name = self.subsector.name + " /"
            self.add_text(name, pos, 'title')
            pos.y_plus(size[1] - 4)
            self.add_text(sector.name, pos, 'title')
        else:
            self.add_text(name, pos, 'title')

        colour = "white"
        fillcolour = "black"
        self._draw_inner_rectangle(colour, fillcolour)
        self._draw_outer_rectangle(colour, fillcolour)

        # Draw small grid
        startline = Cursor(792, 1120)
        startline.dx = -22
        startline.dy = 34
        endline = Cursor(792, 1256)
        endline.dx = -22
        endline.dy = 34

        # vertical lines
        for _ in range(5):
            self.add_line(startline, endline, colour, fillcolour, 2)
            startline.x_plus()
            endline.x_plus()

        # horizontal lines
        startline = Cursor(792, 1120)
        startline.dx = 22
        startline.dy = 34
        endline = Cursor(704, 1120)
        endline.dx = 22
        endline.dy = 34

        for _ in range(5):
            self.add_line(startline, endline, colour, fillcolour, 2)
            startline.y_plus()
            endline.y_plus()

        pos = self.positions[self.subsector.position]
        x = 704 + ((-pos[0] / 8) * 22)
        y = 1120 + ((-pos[1] / 10) * 34)
        startrec = Cursor(x, y)
        endrec = Cursor(x + 22, y + 34)
        self.add_rectangle(startrec, endrec, colour, colour, 1)

    def _draw_inner_rectangle(self, colour: str, fillcolour: str) -> None:
        # Draw inner line around hex grid
        offset = 4
        start = Cursor(53, 53)
        start.x_plus(-offset)
        start.y_plus(-offset)
        end = Cursor(760, 1067)
        end.x_plus(offset)
        end.y_plus(offset)
        self.add_rectangle(start, end, colour, fillcolour, 7)

    def _draw_outer_rectangle(self, colour: str, fillcolour: str) -> None:
        offset = 4
        start1 = Cursor(30, 30)
        start1.x_plus(-offset)
        start1.y_plus(-offset)
        end1 = Cursor(786, 1096)
        end1.x_plus(offset)
        end1.y_plus(offset)
        self.add_rectangle(start1, end1, colour, fillcolour, 7)
