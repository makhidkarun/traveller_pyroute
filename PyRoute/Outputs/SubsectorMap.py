import os

from PIL import Image, ImageFont, ImageDraw

from PyRoute.Position.Hex import Hex
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

    x_count = 8
    y_count = 10

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str):
        super(SubsectorMap, self).__init__(galaxy, routes, output_path, "")
        self.output_suffix = " Subsector"
        self.image_size = Cursor(826, 1272)
        self.core_pos = Cursor(self.image_size.x / 2, 45)
        self.rim_pos = Cursor(self.image_size.x / 2, 1121)
        self.spin_pos = Cursor(0, 1108 / 2)
        self.trail_pos = Cursor(780, 1108 / 2)
        self.start = Cursor(56, 56)
        self.hex_size = Cursor(28, 48)

        self.colours['background'] = 'black'
        self.colours['name'] = "white"
        self.colours['hexes'] = "white"
        self.fonts['title'] = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 48)
        self.fonts['name'] = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 32)
        self.fonts['hexes'] = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 15)

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
        grid = HexGrid(self, self.start, self.hex_size, self.x_count, self.y_count)
        grid.hex_grid(grid.draw_all, 1, colour=self.colours['hexes'])
        if area.coreward:
            core_sub = area.coreward.name
            self.coreward_name(core_sub)
        if area.rimward:
            core_sub = area.rimward.name
            self.rimward_name(core_sub)
        if area.spinward:
            core_sub = area.spinward.name
            self.spinward_name(core_sub)
        if area.trailing:
            core_sub = area.trailing.name
            self.trailing_name(core_sub)
        self.hex_locations()

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
        offset = 1
        upleft = Cursor(30, 30)
        upleft.x_plus(-offset)
        upleft.y_plus(-offset)
        dnleft = Cursor(30, 1096)
        dnleft.x_plus(-offset)
        dnleft.y_plus(offset)
        upright = Cursor(786, 30)
        upright.x_plus(offset)
        upright.y_plus(-offset)
        dnright = Cursor(786, 1096)
        dnright.x_plus(offset)
        dnright.y_plus(offset)

        upleftmid = Cursor(254, 30)
        upleftmid.y_plus(-offset)
        uprightmid = Cursor(568, 30)
        uprightmid.y_plus(-offset)

        dnleftmid = Cursor(254, 1096)
        dnleftmid.y_plus(offset)
        dnrightmid = Cursor(568, 1096)
        dnrightmid.y_plus(offset)

        upleftvert = Cursor(30, 400)
        upleftvert.x_plus(-offset)
        dnleftvert = Cursor(30, 722)
        dnleftvert.x_plus(-offset)

        uprightvert = Cursor(786, 400)
        uprightvert.x_plus(offset)
        dnrightvert = Cursor(786, 722)
        dnrightvert.x_plus(offset)

        linewidth = 6

        self.add_line(upleft, upleftmid, colour, fillcolour, linewidth)
        self.add_line(upright, uprightmid, colour, fillcolour, linewidth)
        self.add_line(upleft, upleftvert, colour, fillcolour, linewidth)
        self.add_line(dnleft, dnleftvert, colour, fillcolour, linewidth)
        self.add_line(upright, uprightvert, colour, fillcolour, linewidth)
        self.add_line(dnright, dnrightvert, colour, fillcolour, linewidth)
        self.add_line(dnleft, dnleftmid, colour, fillcolour, linewidth)
        self.add_line(dnright, dnrightmid, colour, fillcolour, linewidth)

    def coreward_name(self, name: str) -> None:
        size = self._get_text_size(self.fonts['name'], name)
        pos = Cursor(self.core_pos.x - size[0] / 2, self.core_pos.y - size[1])
        self.add_text(name, pos, "name")

    def rimward_name(self, name: str) -> None:
        size = self._get_text_size(self.fonts['name'], name)
        pos = Cursor(self.rim_pos.x - size[0] / 2, self.rim_pos.y - size[1])
        self.add_text(name, pos, "name")

    def spinward_name(self, name):
        self.add_text_rotated(name, self.spin_pos, "name", 90)

    def trailing_name(self, name):
        self.add_text_rotated(name, self.trail_pos, "name", -90)

    def hex_locations(self) -> None:
        # Draw the borders and add the hex numbers
        for x in range(1, self.x_count + 1, 1):
            for y in range(1, self.y_count + 1, 1):
                _, point, location = self._set_pos(x, y)

                name = "{0:02d}{1:02d}".format(location[0], location[1])

                self.add_text_centred(name, point, "hexes")

    def _set_pos(self, x: int, y: int) -> (tuple, Cursor, tuple):
        location = (-self.positions[self.subsector.position][0] + x, -self.positions[self.subsector.position][1] + y)

        q, r = Hex.hex_to_axial(location[0] + self.subsector.sector.dx - 1, location[1] + self.subsector.sector.dy - 1)

        pos = (q, r)
        xm = self.hex_size.x
        ym = self.hex_size.y
        col = xm * 3 * x
        if (x & 1):
            row = (self.start.y - ym * 2) + (y * ym * 2)
        else:
            row = (self.start.y - ym) + (y * ym * 2)
        point = Cursor(col, row)
        point.x_plus(xm)
        #point.y_plus(ym)
        return pos, point, location
