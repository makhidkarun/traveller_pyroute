"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
from PIL import Image, ImageDraw, ImageColor, ImageFont

from PyRoute.Outputs.GraphicMap import GraphicMap


class GraphicSectorMap(GraphicMap):
    def __init__(self, galaxy, routes):
        super(GraphicSectorMap, self).__init__(galaxy, routes)
        self.image_size = (612, 792)

    def document(self, sector):
        self.sector = sector
        self.image = Image.new("RGB", self.image_size, "white")
        return ImageDraw.Draw(self.image)

    def sector_name(self, doc, name):
        """
        Write name at the top of the document
        """
        # get a font
        size = self.titleFont.getsize(name)
        pos = (306 - size[0] / 2, 0)
        doc.text(pos, name, font=self.titleFont, fill=self.fillBlack)
