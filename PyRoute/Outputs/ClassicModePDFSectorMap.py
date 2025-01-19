"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""
import os

from PyRoute.AreaItems.Galaxy import Galaxy

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Outputs.PDFMap import PDFMap
from PyRoute.Outputs.SectorMap import SectorMap


class ClassicModePDFSectorMap(PDFMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(ClassicModePDFSectorMap, self).__init__(galaxy, routes, output_path, writer)

    def document(self, area_name: str, is_live=True):
        document = super(ClassicModePDFSectorMap, self).document(area_name, is_live)
        document.setCreator("ReportLab")
        if isinstance(area_name, Sector):
            title = "Sector " + str(area_name)
            area_name = area_name.name + " Sector"
            document.setTitle(title)
            path = os.path.join(self.output_path, f"{area_name}.pdf")
            document._filename = path

        return document
