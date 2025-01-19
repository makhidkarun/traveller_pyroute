"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
import os

from PIL import Image, ImageDraw, ImageColor, ImageFont

from PyRoute.Outputs.GraphicLine import GraphicLine
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.OldMap import OldMap


class GraphicMap(OldMap):
    image_size = (612, 792)
    corePos = (image_size[0] / 2, 40)
    rimPos = (image_size[0] / 2, image_size[1] - 10)
    spinPos = (0, image_size[1] / 2)
    trailPos = (image_size[0] - 14, image_size[1] / 2)
    fillBlack = (0, 0, 0, 255)
    fillWhite = (255, 255, 255, 255)
    fillBlue = (50, 215, 255, 255)
    fillRed = (255, 48, 48, 255)

    def __init__(self, galaxy, routes):
        super(GraphicMap, self).__init__(galaxy, routes)
        self.titleFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 30)
        self.namesFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 10)
        self.textFill = GraphicMap.fillBlack

    def close(self):
        path = os.path.join(self.galaxy.output_path, self.sector.sector_name() + " Sector.png")
        self.image.save(path)

    def cursor(self, x=0, y=0):
        return Cursor(x, y)

    def add_line(self, doc, start, end, colorname):
        color = ImageColor.getrgb(colorname)
        doc.line([(start.x, start.y), (end.x, end.y)], color)

    def add_circle(self, doc, center, radius, colorname):
        color = ImageColor.getrgb(colorname)
        doc.ellipse([(center.x - radius, center.y - radius), (center.x + radius, center.y + radius)], outline=color)

    def get_line(self, doc, start, end, colorname, width):
        return GraphicLine(doc, start, end, colorname, width)

    def coreward_sector(self, doc, name):
        size = self.get_text_size(self.namesFont, name)
        pos = (self.corePos[0] - size[0] / 2, self.corePos[1] - size[1])
        doc.text(pos, name, font=self.namesFont, fill=self.textFill)

    def rimward_sector(self, doc, name):
        size = self.get_text_size(self.namesFont, name)
        pos = (self.rimPos[0] - size[0] / 2, self.rimPos[1] - size[1])
        doc.text(pos, name, font=self.namesFont, fill=self.textFill)

    def spinward_sector(self, doc, name):
        size = self.get_text_size(self.namesFont, name)
        size = (size[0], size[1] + 3)
        txt = Image.new('L', size, 0)
        d = ImageDraw.Draw(txt)
        d.text((0, 0), name, font=self.namesFont, fill=255)
        w = txt.rotate(90, expand=1)
        doc.bitmap((self.spinPos[0], self.spinPos[1] - w.size[1] / 2), w, fill=self.textFill)

    def trailing_sector(self, doc, name):
        size = self.get_text_size(self.namesFont, name)
        size = (size[0], size[1] + 3)
        txt = Image.new('L', size, 0)
        d = ImageDraw.Draw(txt)
        d.text((0, 0), name, font=self.namesFont, fill=255)
        w = txt.rotate(-90, expand=1)
        doc.bitmap((self.trailPos[0], self.trailPos[1] - w.size[1] / 2), w, fill=self.textFill)

    def get_text_size(self, font, string):
        foo = font.getbbox(string)
        size = (foo[2] - foo[0], foo[3] - foo[1])

        return size
