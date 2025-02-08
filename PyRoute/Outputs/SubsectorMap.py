import os
import math

from PIL import Image, ImageDraw, ImageFont, ImageColor

from PyRoute.Position.Hex import Hex
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.GraphicMap import GraphicMap
from PyRoute.Outputs.HexGrid import HexGrid
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.Star import Star


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
        self.colours['hexes2'] = "white"
        self.colours['hexes3'] = "white"
        self.colours['hexes4'] = "white"
        self.colours['hexes4red'] = self.fillRed
        self.colours['hexes5'] = "white"
        self.colours['world'] = "white"
        self.colours['worldred'] = self.fillRed
        self.fonts['title'] = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 48)
        self.fonts['name'] = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 32)
        self.fonts['hexes'] = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 15)
        self.fonts['world'] = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 22)
        self.fonts['worldred'] = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 22)
        self.fonts['hexes2'] = ImageFont.truetype(self.font_layer.getpath('FreeMono.ttf'), 22)
        self.fonts['hexes3'] = ImageFont.truetype(self.font_layer.getpath('FreeMono.ttf'), 36)
        self.fonts['hexes4'] = ImageFont.truetype(self.font_layer.getpath('Symbola-hint.ttf'), 22)
        self.fonts['hexes4red'] = ImageFont.truetype(self.font_layer.getpath('Symbola-hint.ttf'), 22)
        self.fonts['hexes5'] = ImageFont.truetype(self.font_layer.getpath('Symbola-hint.ttf'), 36)

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

    def write_base_map(self, area: Subsector) -> None:
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
        if self.routes.lower() != 'none':
            self.trade_lines()
        for star in area.worlds:
            self.place_system(star)
        for star in area.worlds:
            self.write_name(star)

    def fill_background(self) -> None:
        background = self.colours['background']
        if background:
            start_cursor = Cursor(self.start.x - 14, self.start.y - 12)
            end_cursor = Cursor(611, self.start.y + self.hex_size.x + 21 + (180 * 4))
            self.add_rectangle(start_cursor, end_cursor, background, background, 1)

    def subsector_grid(self) -> None:
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

    def spinward_name(self, name: str) -> None:
        self.add_text_rotated(name, self.spin_pos, "name", 90)

    def trailing_name(self, name: str) -> None:
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
        # point.y_plus(ym)
        return pos, point, location

    def trade_lines(self) -> ImageDraw:
        world_dex = [item.index for item in self.subsector.worlds]
        trade = [pair for pair in self.galaxy.stars.edges(world_dex, True)
                 if pair[2]['distance'] < 3 and (pair[2]['SourceMarketPrice'] > 0 or pair[2]['TargetMarketPrice'] > 0)]

        self.logger.info("Generating routes in {} for {} worlds".format(self.subsector.name, len(trade)))
        for (star, neighbor, data) in trade:
            self.trade_line(self.galaxy.star_mapping[star], self.galaxy.star_mapping[neighbor], data,
                            self.subsector.position)

        self.logger.debug("Completed trade_lines for {}".format(self.subsector.name))
        return ImageDraw.Draw(self.image)

    def trade_line(self, star: Star, neighbor: Star, data: dict, position: str) -> None:
        xm = self.hex_size.x
        ym = self.hex_size.y
        if star.subsector() == neighbor.subsector():
            star_start = self.get_world_centrepoint(star)
            star_end = self.get_world_centrepoint(neighbor)
        elif star.subsector() == position:
            star_start = self.get_world_centrepoint(star)
            star_end = self.other_subsector_point(neighbor, position)
        elif neighbor.subsector() == position:
            star_start = self.other_subsector_point(star, position)
            star_end = self.get_world_centrepoint(neighbor)

        star_start.x_plus(xm)
        star_start.y_plus(ym)
        star_end.x_plus(xm)
        star_end.y_plus(ym)

        if data['SourceMarketPrice'] > 0:
            trade = data['SourceMarketPrice'] - 1000 - (star.trade_cost * 1000)
            if trade > 0:
                colour = self.trade_colour(int(round(trade / 1000)))
                self.draw_one_arc(star_start, star_end, colour)
        if data['TargetMarketPrice'] > 0:
            trade = data['TargetMarketPrice'] - 1000 - (neighbor.trade_cost * 1000)
            if trade > 0:
                colour = self.trade_colour(int(round(trade / 1000)))
                self.draw_one_arc(star_end, star_start, colour)

    def place_system(self, star: Star) -> None:
        point = self.get_world_centrepoint(star)
        self.zone(star, point.copy())

        # Put the point in the centre of the hex
        xm = self.hex_size.x
        ym = self.hex_size.y
        point.x_plus(xm)
        point.y_plus(ym)

        # Draw the centre dot coloured to reflect the world type.
        radius = (xm / 2) - 1

        if star.tradeCode.asteroid:
            worldCharacter = '\u2059'
            size = self._get_text_size(self.fonts['hexes3'], worldCharacter)

            pos = Cursor(point.x - size[0] / 2, point.y - size[1] * 0.45)
            self.add_text(worldCharacter, pos, "hexes3")

        else:
            colour = ImageColor.getrgb(star.tradeCode.pcode_color)
            self.doc.ellipse([(point.x - radius, point.y - radius), (point.x + radius, point.y + radius)], fill=colour,
                        outline=colour)

        # Write Port code
        size = self._get_text_size(self.fonts['world'], star.port)
        pos = Cursor(point.x - (size[0] / 2) + 1, point.y - (size[1]) - 9.6)
        self.add_text(star.port, pos, 'world')

        if star.ggCount:
            self.print_base_char('\u25CF', 'world', point, (1.75, -1.2))

        if 'N' in star.baseCode or 'K' in star.baseCode:
            self.print_base_char('\u066D', 'hexes3', point, (-0.7, -0.4))
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'S' in star.baseCode:
            self.print_base_char('\u25B2', 'hexes4', point, (-1.8, -1.0))
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'D' in star.baseCode:
            self.print_base_char('\u25A0', 'hexes4', point, (-1.55, -0.35))
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'W' in star.baseCode:
            self.print_base_char('\u25B2', 'hexes4red', point, (-1.85, -1.0))
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'I' in star.baseCode:
            self.print_base_char('\u2316', 'hexes5', point, (-2.5, -0.5))
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        station_code = star.tradeCode.research_station_char
        if station_code:
            self.print_base_char(station_code, 'hexes4red', point, (-2.6, -0.4))
            self.logger.debug("Research station for {} : {}".format(star.name, star.tradeCode))

    # Write the name of the world on the map (last).
    def write_name(self, star: Star) -> None:
        point = self.get_world_centrepoint(star)
        # Put the point in the centre of the hex
        xm = self.hex_size.x
        ym = self.hex_size.y
        point.x_plus(xm)
        point.y_plus(ym)

        name = star.name
        if star.tradeCode.high:
            name = name.upper()
        elif star.tradeCode.low:
            name = name.lower()
        size = self._get_text_size(self.fonts['world'], name)
        pos = Cursor(point.x - (size[0] / 2) + 1, point.y + size[1] - 6)
        if star.tradeCode.capital:
            self.add_text(name, pos, "worldred")
        else:
            self.add_text(name, pos, "world")

    def _world_point(self, hex_row: int, hex_col: int) -> Cursor:
        xm = self.hex_size.x
        ym = self.hex_size.y
        col = xm * 3 * hex_col
        if (hex_col & 1):
            row = (self.start.y - ym * 2) + (hex_row * ym * 2)
        else:
            row = (self.start.y - ym) + (hex_row * ym * 2)
        return Cursor(col, row)

    # Get the centre of the hex for writing a world
    def get_world_centrepoint(self, star: Star) -> Cursor:
        col = star.col + self.positions[star.subsector()][0]
        row = star.row + self.positions[star.subsector()][1]
        return self._world_point(row, col)

    def other_subsector_point(self, star: Star, position: str) -> Cursor:
        col_out = star.col + self.positions[position][0]
        row_out = star.row + self.positions[position][1]
        return self._world_point(row_out, col_out)

    def trade_colour(self, trade: int) -> str:
        tcolour = {0: "#0500ff", 1: "#0012ff", 2: "#0094ff", 3: "#00ffa8",
                  4: "#8aff00", 5: "#FFd200", 6: "#FF8200", 7: "#FF3200",
                  8: "#FF0030", 9: "#FF00B0", 10: "#FF04F0", 11: "#FF0CF0"}
        return tcolour.get(trade, "#000000")

    def zone(self, star: Star, point: Cursor) -> None:
        xm = self.hex_size.x
        ym = self.hex_size.y
        point.x_plus(xm)
        point.y_plus(ym)

        xm += 2

        if star.zone in ['R', 'F']:
            self.add_circle(point, xm, 6, False, 'red zone')
        elif star.zone in ['A', 'U']:
            self.add_circle(point, xm, 6, False, 'amber zone')
        else:  # no zone -> do nothing
            return

    def print_base_char(self, baseCharacter: str, scheme: str, point: Cursor, multiplier: tuple[float, float]) -> None:
        font = self.get_font(scheme)
        size = self._get_text_size(font, baseCharacter)
        pos = Cursor(point.x + (multiplier[0] * size[0]), point.y + (multiplier[1] * size[1]))
        self.add_text(baseCharacter, pos, scheme)

    def draw_one_arc(self, start: Cursor, end: Cursor, colour) -> None:
        centre = self.circle_centre(start, end)
        self.draw_arc(centre, start, end, colour)

    def circle_centre(self, start: Cursor, end: Cursor) -> Cursor:
        # Calculate the centre of an equilateral triangle from start and end
        # root3 = math.sqrt(3)
        root3 = 2
        xm = 0.5 * (start.x + end.x)
        ym = 0.5 * (start.y + end.y)

        xslope = (xm - start.x)
        yslope = (ym - start.y)

        slope = xslope / yslope if yslope != 0 else 0

        cx = xm + (root3 * slope)
        cy = ym + (root3 * slope)

        return Cursor(round(cx), round(cy))

    def draw_arc(self, centre, start, end, colour):
        r = math.sqrt((start.x - centre.x) ** 2 + (start.y - centre.y) ** 2)
        x1 = centre.x - r
        y1 = centre.y - r
        x2 = centre.x + r
        y2 = centre.y + r
        startAngle = (180 / math.pi) * math.atan2(start.y - centre.y, start.x - centre.x)
        endAngle = (180 / math.pi) * math.atan2(end.y - centre.y, end.x - centre.x)

        for i in range(-2, 2):
            self.doc.arc([x1 + i, y1, x2 + i, y2], startAngle, endAngle, colour)
            self.doc.arc([x1, y1 + i, x2, y2 + i], startAngle, endAngle, colour)
