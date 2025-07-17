
from AreaItems.Galaxy import Galaxy

from Outputs.GraphicMap import GraphicMap
from Outputs.SectorMap import SectorMap


class LightModeGraphicSectorMap(GraphicMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        self.input_scale = 4
        self.output_scale = 1

        super(LightModeGraphicSectorMap, self).__init__(galaxy, routes, output_path, writer)
