"""
Created on Apr 23, 2025

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from Tests.baseTest import baseTest


class testAllegianceSubset(baseTest):

    def test_blowup_1(self):
        source = self.unpack_filename('DeltaFiles/allegiance_subset_blowup_1/Reaver\'s Deep.sec')

        delta = DeltaDictionary()
        for src in [source]:
            sector = SectorDictionary.load_traveller_map_file(src)
            delta[sector.name] = sector
        result, msg = delta.is_well_formed()
        self.assertTrue(result, msg)

        allegiances = delta.allegiance_list()
        nu_allegiances = allegiances.copy()
        nu_allegiances.remove("CaTe")

        nu_delta = delta.allegiance_subset(nu_allegiances)
        result, msg = nu_delta.is_well_formed()
        self.assertTrue(result, msg)
