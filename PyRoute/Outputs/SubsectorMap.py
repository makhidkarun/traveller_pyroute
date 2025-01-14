
from PyRoute.Outputs.Map import Map
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector


class SubsectorMap(Map):

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str):
        super(SubsectorMap).__init__(galaxy, routes, output_path)
        self.output_suffix = " Subsector"

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
        document = self.document(subsector.name + " Subsector", True)
        self.write_base_map(document, subsector)
