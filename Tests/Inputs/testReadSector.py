"""
Created on May 18, 2025

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from Tests.baseTest import baseTest


class testReadSector(baseTest):

    def testReadKilongSector(self):
        sourcefile = self.unpack_filename('DeltaFiles/read_kilong_sector/Kilong.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual(518, len(sector.lines), "Unexpected # of lines")
