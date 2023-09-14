"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
from PIL import ImageColor


class GraphicLine(object):
    def __init__(self, image, lineStart, lineEnd, colorname, width):
        self.image = image
        self.lineStart = lineStart
        self.lineEnd = lineEnd
        self.color = ImageColor.getrgb(colorname)
        self.width = max(1, int(width))

    def _draw(self):
        self.image.line([(self.lineStart.x, self.lineStart.y), (self.lineEnd.x, self.lineEnd.y)], self.color,
                        self.width)
