"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
from PIL import ImageColor  # type: ignore

from Outputs.Cursor import Cursor


class GraphicLine(object):
    def __init__(self, image, lineStart: Cursor, lineEnd: Cursor, colorname: str, width: int):
        self.image = image
        self.lineStart: Cursor = lineStart
        self.lineEnd: Cursor = lineEnd
        self.color = ImageColor.getrgb(colorname)
        self.width = max(1, int(width))

    def _draw(self):
        self.image.line([self.lineStart.as_tuple(), self.lineEnd.as_tuple()], self.color,
                        self.width)
