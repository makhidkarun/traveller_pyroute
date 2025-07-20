
from PyRoute.AreaItems.Galaxy import Galaxy

from PyRoute.Outputs.PDFMap import PDFMap
from PyRoute.Outputs.SectorMap import SectorMap


class DarkModePDFSectorMap(PDFMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(DarkModePDFSectorMap, self).__init__(galaxy, routes, output_path, writer)
        self.colours['background'] = 'black'
        self.colours['sector'] = 'white'
        self.colours['system_port'] = (242, 242, 242)
        self.colours['system_uwp'] = (242, 242, 242)
        self.colours['system_name'] = (242, 242, 242)
        self.colours['base code'] = (242, 242, 242)
