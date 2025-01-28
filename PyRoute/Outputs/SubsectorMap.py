from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.GraphicMap import GraphicMap
from PyRoute.Outputs.HexGrid import HexGrid
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector


class SubsectorMap(GraphicMap):

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str):
        super(SubsectorMap, self).__init__(galaxy, routes, output_path, "")
        self.output_suffix = " Subsector"
        self.image_size = Cursor(826, 1272)
        self.xm = 28  # half the length of one side
        self.ym = 48  # half a hex height

        self.colours['background'] = 'black'

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

    def write_base_map(self, area: Subsector):
        self.fill_background()
        self.area_name_title(area.name)
        grid = HexGrid(self, self.start, self.hex_size, 8, 10)
        grid.hex_grid(grid.draw_all, 1, colour=self.colours['hexes'])

    def fill_background(self):
        background = self.colours['background']
        if background:
            start_cursor = Cursor(self.start.x - 14, self.start.y - 12)
            end_cursor = Cursor(611, self.start.y + self.hex_size.x + 21 + (180 * 4))
            self.add_rectangle(start_cursor, end_cursor, background, background, 1)

    def area_name_title(self, area_name: str) -> None:
        cursor = Cursor(self.image_size.x // 2, -5)
        self.add_text_centred(area_name, cursor, 'title')
