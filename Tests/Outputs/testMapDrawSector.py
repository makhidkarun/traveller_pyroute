import unittest
import logging
import tempfile

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Outputs.DarkModePDFSectorMap import DarkModePDFSectorMap
from PyRoute.Outputs.LightModeGraphicSectorMap import LightModeGraphicSectorMap
from PyRoute.Outputs.LightModePDFSectorMap import LightModePDFSectorMap

from Tests.baseTest import baseTest
from Tests.Outputs.TestMap import TestSectorMap

logger = logging.getLogger('PyRoute Test')


class TestMapDrawSector(baseTest):
    """
    This class is a test for the various map output classes. There is no verification of output contents here, this is
    only a test of if the generation process is correct (i.e. does not throw an error during the process). If you
    feel the need to verify this, open the output files in an appropriate viewer (graphic program or PDF viewer) to
    review the maps and see what they look like. This test was used extensively during the development of the updated
    map drawing classes to ensure they were correct and were not missing any bits or creating bad drawing.
    """
    def setUp(self):
        self.set_logging('INFO')
        self.galaxy = Galaxy(15, 6)
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag.sec')
        self.writer = 'light'

        self.galaxy.output_path = tempfile.gettempdir()
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code='fixed', ru_calc='scaled',
                                      route_reuse=10, trade_choice='none', route_btn=8,
                                      mp_threads=1, debug_flag=True, fix_pop=False,
                                      deep_space={}, map_type="classic")
        self.galaxy.read_sectors(readparms)
        self.galaxy.set_borders('erode', 'collapse')

        sector = self.galaxy.sectors['Dagudashaag']
        sector.stats.population = 851784
        sector.stats.economy = 9103578
        sector.stats.percapita = 10697
        sector.stats.sum_ru = 457568
        sector.stats.tradeVol = 132944 * (10**9)
        sector.stats.passengers = 7273 * (10**6)
        sector.stats.spa_people = 90496215

        sector.coreward = Sector('# Vland', "# -1, 1")
        sector.coreward.rimward = sector
        sector.spinward = Sector("# Gushemege", "# -2, 0")
        sector.spinward.trailing = sector
        sector.trailing = Sector("# Core", "# 0, 0")
        sector.trailing.spinward = sector
        sector.rimward = Sector("# Zarushagar", "# -1, -1")
        sector.rimward.coreward = sector

        self.galaxy._set_trade_object(10, 'None', 0, 0, True)
        self.galaxy.trade.generate_base_routes()

    def test_sector_graph(self) -> None:
        graphMap = LightModeGraphicSectorMap(self.galaxy, 'none',
                                             output_path=tempfile.gettempdir(),
                                             writer=self.writer)
        graphMap.write_maps()

    def test_sector_pdf(self) -> None:
        pdfmap = LightModePDFSectorMap(self.galaxy, 'none',
                                       output_path=tempfile.gettempdir(),
                                       writer=self.writer)
        self.galaxy.sectors['Dagudashaag'].name = 'Dagudashaag Light'
        pdfmap.write_maps()
        self.galaxy.sectors['Dagudashaag'].name = 'Dagudashaag'

    def test_sector_dark_pdf(self) -> None:
        pdfmap = DarkModePDFSectorMap(self.galaxy, 'none',
                                      output_path=tempfile.gettempdir(),
                                      writer=self.writer)
        self.galaxy.sectors['Dagudashaag'].name = 'Dagudashaag Dark'
        pdfmap.write_maps()
        self.galaxy.sectors['Dagudashaag'].name = 'Dagudashaag'

    def test_sector_test(self) -> None:
        self.writer = 'light'
        testmap = TestSectorMap(self.galaxy, 'none',
                                output_path=tempfile.gettempdir(),
                                writer=self.writer)
        testmap.write_maps()

        self.assertEqual(testmap.area_name, 'Dagudashaag')
        self.assertEqual(4429, len(testmap.lines))  # 4025 is the completed base map minus the map key
                                                        # 262 is the borders  # noqa
                                                        # 12 for the Map Key  # noqa
                                                        # 130 is the comm routes  # noqa
        self.assertEqual(560, len(testmap.rects))   # 559 blanking rectangles behind the world name
                                                        # 1 for the map key # noqa
        self.assertEqual(2177, len(testmap.texts))  # 12 is the completed base map minus the map key
                                                        # 4 is the connected sectors # noqa
                                                        #  9 is for the map key # noqa
                                                        # 2152 is worlds (559 * 3 lines each) # noqa
        # Assert all the fonts used are in the default font list of names.
        for text in testmap.texts:
            self.assertIn(text[3], testmap.fonts)

        self.assertEqual(559, self.galaxy.stars.number_of_nodes())
        self.assertEqual(13098, self.galaxy.stars.number_of_edges())
        self.assertEqual(559, self.galaxy.ranges.number_of_nodes())
        self.assertEqual(0, self.galaxy.ranges.number_of_edges())

        world_indexes = [star.index for star in self.galaxy.sectors['Dagudashaag'].worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(nbunch=world_indexes, data=True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]

        self.assertEqual(130, len(comm_routes))

    @staticmethod
    def set_logging(level):
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)


if __name__ == '__main__':
    unittest.main()
