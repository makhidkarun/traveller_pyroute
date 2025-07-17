"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""
from AreaItems.Galaxy import Galaxy
from AreaItems.Sector import Sector
from Star import Star

from Outputs.Cursor import Cursor
from Outputs.HexGrid import HexGrid
from Outputs.HexSystem import HexSystem
from Outputs.Map import Map
from StatCalculation import StatCalculation


class SectorMap(Map):
    subsector_grid_width: int = 592
    subsector_width: int = 144
    subsector_grid_height: int = 780
    subsector_height: int = 180

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(SectorMap, self).__init__(galaxy, routes, output_path, writer)
        self.output_suffix = " Sector"

        self.start: Cursor = Cursor(15, 43)
        self.hex_size: Cursor = Cursor(6, 9)
        self.image_size: Cursor = Cursor(612, 792)  # Default letter sized page. May be adjusted later
        self.logger.debug("Completed SectorMap init")

    def write_maps(self) -> None:
        self.logger.info(f"writing {len(self.galaxy.sectors)} sector maps...")
        for sector in self.galaxy.sectors.values():
            self.write_sector_map(sector)

    def write_sector_map(self, sector: Sector) -> None:
        self.doc = self.document(sector.name + " Sector", False)
        self.system_writer = HexSystem.set_system_writer(self.system_writer_type, self, self.start, self.hex_size,
                                                         self.routes)
        self.write_base_map(sector)
        self.draw_borders(sector)

        if sector.coreward:
            self.coreward_name(sector.coreward.name)
        if sector.rimward:
            self.rimward_name(sector.rimward.name)
        if sector.trailing:
            self.trailing_name(sector.trailing.name)
        if sector.spinward:
            self.spinward_name(sector.spinward.name)

        self.draw_comm_routes(sector)
        self.draw_trade_routes(sector)

        for star in sector.worlds:
            self.system_writer.place_system(star)

        self.close()

    def draw_borders(self, sector: Sector) -> None:  # type:ignore[override]
        grid = HexGrid(self, self.start, self.hex_size, 32, 40)
        grid.set_borders(self.galaxy.borders, sector.dx, sector.dy)
        grid.hex_grid(grid.draw_borders, 1, colour=self.colours['hexes'])

    def write_base_map(self, area: Sector) -> None:  # type:ignore[override]
        self.fill_background()
        self.area_name_title(area.name)
        self.subsector_grid()
        grid = HexGrid(self, self.start, self.hex_size, 32, 40)
        grid.hex_grid(grid.draw_all, 1, colour=self.colours['hexes'])
        self.statistics(area)
        self.map_key(area)

    def fill_background(self) -> None:
        background = self.colours['background']
        if background:
            start_cursor = Cursor(self.start.x - 14, self.start.y - 12)
            end_cursor = Cursor(611, self.start.y + self.hex_size.x + 21 + (180 * 4))
            self.add_rectangle(start_cursor, end_cursor, background, background, 1)

    def subsector_grid(self) -> None:
        vlineStart = Cursor(0, self.start.y + self.hex_size.x)
        vlineEnd = Cursor(0, self.start.y + self.hex_size.x + (self.subsector_height * 4))
        for x in range(self.start.x, self.subsector_grid_width, self.subsector_width):
            vlineStart.x = x
            vlineEnd.x = x
            self.add_line(start=vlineStart, end=vlineEnd, colour=self.colours['grid'])

        hlineStart = Cursor(self.start.x, 0)
        hlineEnd = Cursor(self.subsector_grid_width, 0)
        for y in range(self.start.y + self.hex_size.x, self.subsector_grid_height, self.subsector_height):
            hlineStart.y = y
            hlineEnd.y = y
            self.add_line(start=hlineStart, end=hlineEnd, colour=self.colours['grid'])

    def statistics(self, sector: Sector) -> None:
        cursor = Cursor(self.start.x, 0)

        # Column 1
        strings = {
            9: "Information:",
            16: "Position: {:d}, {:d} ".format(sector.x, sector.y),
            23: "Worlds: {:d}".format(sector.world_count()),
            30: "Population: {:,d}".format(sector.stats.population)
        }

        for y, text in strings.items():
            cursor.y = y
            cursor.x = self.start.x
            self.add_text(text, cursor, 'info')

        # Column 2
        strings = {
            9: "Economy:",
            16: "GSP: BCr{:,d} ".format(sector.stats.economy),
            23: "Per Capita: Cr{:,d}".format(sector.stats.percapita),
            30: "Total RU: {:,d}".format(sector.stats.sum_ru)
        }
        cursor.x = 75  # 15 + 2.25 * 25 (characters for above)
        for y, text in strings.items():
            cursor.y = y
            cursor.x = 75
            self.add_text(text, cursor, 'info')

        strings = {
            9: "Trade:",
            16: "Volume: BCr{:,d}/y".format(sector.stats.tradeVol // (10**9)),
            23: "Passengers: {:,d}M/y".format(sector.stats.passengers // (10**6)),
            30: "SPA: {:,d}".format(sector.stats.spa_people)
        }
        cursor.x = 145  # 15 + 75 + 2.25 * 25 (characters)
        for y, text in strings.items():
            cursor.y = y
            cursor.x = 145
            self.add_text(text, cursor, 'info')

    def area_name_title(self, area_name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, -5)
        self.add_text_centred(area_name, cursor, 'title')

    def coreward_name(self, name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, self.start.y - 15)
        self.add_text_centred(name, cursor, 'sector')

    def rimward_name(self, name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, self.image_size.y - 18)
        self.add_text_centred(name, cursor, 'sector')

    def spinward_name(self, name: str) -> None:
        y = self.start.y + self.hex_size.x + self.subsector_height + self.subsector_height
        cursor = Cursor(self.start.x - 7, y)
        self.add_text_rotated(name, cursor, 'sector', 90)

    def trailing_name(self, name: str) -> None:
        y = self.start.y + self.hex_size.x + self.subsector_height + self.subsector_height
        cursor = Cursor(self.image_size.x - 10, y)
        self.add_text_rotated(name, cursor, 'sector', -90)

    def map_key(self, area: Sector) -> None:
        start_cursor = Cursor(self.start.x + (self.subsector_width * 3), 2)
        end_cursor = Cursor(self.start.x + (self.subsector_width * 4), self.start.y - 13)
        assert self.system_writer is not None
        self.system_writer.map_key(start_cursor, end_cursor)

    def draw_comm_routes(self, area: Sector) -> None:
        sector_indexes = [star.index for star in area.worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(sector_indexes, True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]
        for (star, neighbor, _) in comm_routes:
            star_actual = self.galaxy.star_mapping[star]
            neighbor_actual = self.galaxy.star_mapping[neighbor]
            self.comm_line(star_actual, neighbor_actual, area)

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
        self.add_line(clip_start, clip_end, colour, stroke='dashed', width=2)

    def draw_trade_routes(self, area: Sector) -> None:
        sector_indexes = [star.index for star in area.worlds]
        trade_routes = [star for star in self.galaxy.stars.edges(sector_indexes, True)
                        if star[2]['trade'] > 0 and StatCalculation.trade_to_btn(star[2]['trade']) >= self.galaxy.min_btn]
        trade_routes.sort(key=lambda x: x[2]['trade'])
        for (star, neighbor, data) in trade_routes:
            star_actual = self.galaxy.star_mapping[star]
            neighbor_actual = self.galaxy.star_mapping[neighbor]
            self.trade_line(star_actual, neighbor_actual, area, data)

    def trade_line(self, start: Star, end: Star, sector: Sector, data: dict) -> None:
        colour = self.colours['trade']
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
        self.add_line(clip_start, clip_end, colour, stroke='solid', width=2)

    def line_clipping(self, start_cursor, end_cursor) -> tuple[Cursor, Cursor]:
        clip_start, clip_end = Map.clipping(self.start, self.image_size, start_cursor, end_cursor)
        assert isinstance(clip_start, Cursor) and isinstance(clip_end, Cursor)
        return clip_start, clip_end
