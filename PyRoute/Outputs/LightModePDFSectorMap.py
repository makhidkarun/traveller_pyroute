
from PyRoute.AreaItems.Galaxy import Galaxy

from PyRoute.Outputs.PDFMap import PDFMap
from PyRoute.Outputs.SectorMap import SectorMap


class LightModePDFSectorMap(PDFMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(LightModePDFSectorMap, self).__init__(galaxy, routes, output_path, writer)
