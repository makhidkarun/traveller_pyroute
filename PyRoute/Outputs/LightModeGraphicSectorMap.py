
from PyRoute.AreaItems.Galaxy import Galaxy

from PyRoute.Outputs.GraphicMap import GraphicMap
from PyRoute.Outputs.SectorMap import SectorMap


class LightModeGraphicSectorMap(GraphicMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        self.input_scale = 4
        self.output_scale = 1

        super(LightModeGraphicSectorMap, self).__init__(galaxy, routes, output_path, writer)

