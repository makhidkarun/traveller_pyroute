
from PyRoute.Outputs.Map import MapOutput
from PyRoute.Outputs.HexGrid import HexGrid
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Position.Hex import Hex
from PyRoute.Star import Star
from PyRoute.StatCalculation import StatCalculation
from PyRoute.SystemData.UWP import UWP


class HexSystem(object):
    def __init__(self, doc: MapOutput, start: Cursor, hex_size: Cursor):
        self.doc: MapOutput = doc
        self.start: Cursor = start
        self.hex_size: Cursor = hex_size

    def place_system(self, star: Star) -> None:
        self._place_system_information(self.location(star.hex), star)

    def _place_system_information(self, point: Cursor, star: Star) -> None:
        raise NotImplementedError("Base Class")

    def map_key(self, start: Cursor, end: Cursor) -> None:
        raise NotImplementedError("Base Class")

    def location(self, star_hex: Hex) -> Cursor:
        col = (self.hex_size.x * 3 * star_hex.col) + int(self.hex_size.x * 1.5)
        if star_hex.col & 1:
            row = (self.start.y - self.hex_size.y * 2) + (star_hex.row * self.hex_size.y * 2)
        else:
            row = (self.start.y - self.hex_size.y) + (star_hex.row * self.hex_size.y * 2)
        return Cursor(col, row)

    def clear_hex(self, center: Cursor):
        center.x_plus(0)
        center.y_plus(self.hex_size.y)
        radius = int(self.hex_size.x * 1.25)
        self.doc.add_circle(center, radius, 1, True, "background")

    def zone(self, star: Star, center: Cursor) -> None:
        center.y_plus(self.hex_size.y)
        radius = int(self.hex_size.x * 1.25)
        if star.zone in ['R', 'F']:
            self.doc.add_circle(center, radius, 2, False, 'red zone')
        elif star.zone in ['A', 'U']:
            self.doc.add_circle(center, radius, 2, False, 'amber zone')
        else:
            return

    @staticmethod
    def set_system_writer(writer: str, doc: MapOutput, start: Cursor, hex_size: Cursor):
        writers = {
            'light': HexSystemClassicLayout,
            'medium': HexSystem3Lines,
            'dense': HexSystem4Lines,
        }
        return writers[writer](doc, start, hex_size)

    def map_key_base(self, start: Cursor, end: Cursor):
        background = self.doc.colours['background']
        if background:
            self.doc.add_rectangle(start, end, background, background, 1)

        point = Cursor(start.x + self.hex_size.x * 6, start.y + 3)

        hex_grid = point.copy()
        grid = HexGrid(self.doc, hex_grid, self.hex_size, 1, 1)
        grid.hex_grid(grid.draw_all, 1, colour=self.doc.colours['hexes'])

        hex_grid.x_plus(self.hex_size.x * 9)
        grid = HexGrid(self.doc, hex_grid, self.hex_size, 1, 1)
        grid.hex_grid(grid.draw_all, 1, colour=self.doc.colours['hexes'])

        point.x_plus(int(self.hex_size.x * 2))
        self._place_system_information(point.copy(), self.map_key_star())
        point.y_plus(self.hex_size.y + 3)
        return point

    def map_key_star(self) -> Star:
        star = Star()
        star.uwp = UWP('A847427-B')
        star.name = 'Azimuth'
        star.zone = '-'
        star.baseCode = 'N'
        star.ggCount = 1
        star.uwpCodes = {'Starport': star.port,
                         'Size': star.size,
                         'Atmosphere': star.atmo,
                         'Hydrographics': star.hydro}

        return star


class HexSystem3Lines(HexSystem):

    def __init__(self, doc: MapOutput, start: Cursor, hex_size: Cursor):
        super(HexSystem3Lines, self).__init__(doc, start, hex_size)

    def _place_system_information(self, point: Cursor, star: Star):
        self.clear_hex(point.copy())
        self.zone(star, point.copy())

        self.fuel_markers(star, point.copy())
        # Port size value
        added = "{}".format(star.starportSize)
        self.doc.add_text_centred(added, point, 'system_port')

        # UWP
        point.y_plus(5)
        self.doc.add_text_centred(star.uwp, point, 'system_uwp')

        # System Name
        point.y_plus(5)
        self.doc.add_text_centred(star.name, point, 'system_name', self.hex_size.x * 3)

    def fuel_markers(self, star: Star, center: Cursor) -> None:
        center.x_plus(-1 * self.hex_size.x * 0.75)
        center.y_plus(self.hex_size.x * 0.3)

        if star.ggCount > 0:
            self.doc.add_circle(center, radius=1, line_width=2, fill=True, scheme='gg refuel')

        if star.wilderness_refuel():
            center.y_plus(1.5)
            center.x_plus(1.5)
            self.doc.add_circle(center, radius=1, line_width=2, fill=True, scheme='wild refuel')

    def map_key(self, start: Cursor, end: Cursor):
        _ = self.map_key_base(start, end)


class HexSystem4Lines(HexSystem):

    def __init__(self, doc: MapOutput, start: Cursor, hex_size: Cursor):
        super(HexSystem4Lines, self).__init__(doc, start, hex_size)

    def _place_system_information(self, point: Cursor, star: Star) -> None:
        self.zone(star, point.copy())

        point.y_plus(3.5)
        self.doc.add_text_centred(star.uwp, point, 'system_uwp')

        if len(star.name) > 0:
            point.y_plus(3.5)
            self.doc.add_text_centred(star.name, point, 'system_uwp', self.hex_size.x * 3)

        added = star.alg_code
        if star.tradeCode.subsector_capital:
            added += '+'
        elif star.tradeCode.capital:
            added += "*"
        else:
            added += ' '
        added += '{:d}'.format(star.ggCount)
        point.y_plus(3.5)
        self.doc.add_text_centred(added, point, 'system_uwp')

        point.y_plus(3.5)
        tradeIn = StatCalculation.trade_to_btn(star.tradeIn)
        tradeThrough = StatCalculation.trade_to_btn(star.tradeIn + star.tradeOver)
        added = "{:X}{:X}{:X}{:d}".format(star.wtn, tradeIn, tradeThrough, star.starportSize)
        self.doc.add_text_centred(added, point, 'system_uwp')

    def map_key(self, start: Cursor, end: Cursor):
        _ = self.map_key_base(start, end)


class HexSystemClassicLayout(HexSystem):

    def __init__(self, doc: MapOutput, start: Cursor, hex_size: Cursor):
        super(HexSystemClassicLayout, self).__init__(doc, start, hex_size)

    def _place_system_information(self, point: Cursor, star: Star) -> None:
        self.zone(star, point.copy())
        self.base_marker(star, point.copy())
        self.fuel_markers(star, point.copy())

        port_center = point.copy()
        port_center.y_plus(self.hex_size.x * 0.2)
        self.doc.add_text_centred(star.port, point, 'system_port')

        point.x_plus(0)
        point.y_plus(self.hex_size.y)
        radius = int(self.hex_size.x * 0.6)

        if star.wilderness_refuel():
            self.doc.add_circle(point, radius, 1, True, "wild refuel")
        elif star.tradeCode.asteroid:
            world = '_'
            point.y_plus(-0.3 * self.hex_size.y)
            self.doc.add_text_centred(world, point, 'base code')
            point.y_plus(0.3 * self.hex_size.y)
        else:
            self.doc.add_circle(point, radius, 1, True, "grid")

        # allegiance
        # point.x_plus(self.hex_size.x * 1.25)
        # point.y_plus(-0.25 * self.hex_size.y)
        # self.doc.add_text_centred(star.alg_code, point, 'system_uwp')
        # point.x_plus (-1.25 * self.hex_size.x)
        # point.y_plus(0.25 * self.hex_size.y)

        # System Name
        point.y_plus(3)
        self.doc.add_rectangle(Cursor(point.x - 1.25 * self.hex_size.x, point.y + 1),
                               Cursor(point.x + 1.25 * self.hex_size.x, point.y + 5),
                               self.doc.get_colour('background'), self.doc.get_colour('background'), 1)
        self.doc.add_text_centred(star.name, point, 'system_uwp', self.hex_size.x * 3)

    def base_marker(self, star: Star, centre: Cursor) -> None:
        centre.x_plus(-1 * self.hex_size.x)
        centre.y_plus(self.hex_size.x * 0.3)

        if 'N' in star.baseCode:
            base = 'H'  # ZapfDingbats Star
        elif 'W' in star.baseCode or 'S' in star.baseCode:
            base = 's'  # ZapfDingbats Triangle
        elif 'D' in star.baseCode:
            base = 'l'  # ZapfDingbats circle
        elif 'M' in star.baseCode:
            base = 'n'  # ZapfDingbats square
        else:
            base = ''
        self.doc.add_text_centred(base, centre, 'base code')

    def fuel_markers(self, star: Star, centre: Cursor) -> None:
        centre.x_plus(1 * self.hex_size.x)
        centre.y_plus(self.hex_size.x * 0.3)
        if star.ggCount > 0:
            self.doc.add_text_centred('l', centre, 'base code')

        # if star.ggCount > 0:
        #     self.doc.add_circle(center, radius=1, line_width=1, fill=True, scheme='gg refuel')

    def map_key(self, start: Cursor, end: Cursor):
        point = self.map_key_base(start, end)
        # point = Cursor(start.x + self.hex_size.x * 6, start.y + 3)

        port_cursor = point.copy()
        port_cursor.x_plus(-1 * self.hex_size.x * 2)
        port_cursor.y_plus(-1 * self.hex_size.y)
        self.doc.add_text_right_aligned("Port", port_cursor, 'system_port')

        base_cursor = port_cursor.copy()
        base_cursor.y_plus(5)
        self.doc.add_text_right_aligned("Base", base_cursor, 'system_port')

        world_cursor = port_cursor.copy()
        world_cursor.y_plus(10)
        self.doc.add_text_right_aligned("World Type", world_cursor, "system_port")

        name_cursor = port_cursor.copy()
        name_cursor.y_plus(15)
        self.doc.add_text_right_aligned("Name", name_cursor, "system_port")

        gg_cursor = port_cursor.copy()
        gg_cursor.x_plus(self.hex_size.x * 4)
        self.doc.add_text("Gas Giant", gg_cursor, "system_port")
