from typing_extensions import Self

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.Colour import Colour
from PyRoute.Outputs.Map import Map, Scheme
from PyRoute.Outputs.SectorMap import SectorMap


class TestMap(Map):
    """
    The TestMap class is an implementation of the Map class. Rather than drawing anything, this just accumulates the
    results of the calls to the different draw methods to validate the drawing is being done correctly. This is not
    designed to output anything (like PDFMap or GraphicMap are).
    """
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(TestMap, self).__init__(galaxy, routes, output_path, writer)
        self.image_size = Cursor(612, 792)  # Default letter sized page. May be adjusted later
        self.area_name = None
        self.lines = []
        self.rects = []
        self.texts = []
        self.circles = []

    def document(self, sector: str, is_live: bool = True) -> Self:
        """
        Generated by the type of document
        """
        return self

    def close(self) -> None:
        return None

    def area_name_title(self, area_name: str) -> None:
        """
        Set the title of the area at the top of the document as a title
        :param area_name: Name to write
        :return: None
        """
        self.area_name = area_name

    def add_line(self, start: Cursor, end: Cursor, colour: Colour, stroke: str = 'solid', width: float = 1) -> None:
        """
        Add a line to the document, from start to end, in colour
        """
        line = (start.x, start.y, end.x, end.y, colour, stroke, width)
        self.lines.append(line)

    def add_rectangle(self, start: Cursor, end: Cursor, border_colour: Colour, fill_colour: Colour, width: int) -> None:
        """
        Add a filled rectangle to the document, upper right -> lower left, border + fill colour.
        :param start:
        :param end:
        :param border_colour:
        :param fill_colour:
        :param width:
        :return:
        """
        rect = (start.x, start.y, end.x, end.y, border_colour, fill_colour, width)
        self.rects.append(rect)

    def add_circle(self, center: Cursor, radius: int, line_width: int, fill: bool, scheme: Scheme) -> None:
        circle = (center.x, center.y, radius, line_width, fill, scheme)
        self.circles.append(circle)

    def add_text(self, text: str, start: Cursor, scheme: Scheme) -> None:
        text_addition = (start.x, start.y, text, scheme)
        self.texts.append(text_addition)

    def add_text_centred(self, text: str, start: Cursor, scheme: Scheme, max_width: int = -1) -> None:
        text_addition = (start.x, start.y, text, scheme)
        self.texts.append(text_addition)

    def add_text_rotated(self, text: str, start: Cursor, scheme: Scheme, rotation: int) -> None:
        text_addition = (start.x, start.y, text, scheme)
        self.texts.append(text_addition)

    def add_text_right_aligned(self, text: str, start: Cursor, scheme: Scheme) -> None:
        text_addition = (start.x, start.y, text, scheme)
        self.texts.append(text_addition)

    @staticmethod
    def _get_colour(colour: Colour):
        return colour

    @staticmethod
    def _get_text_size(font, string: str) -> tuple[int, int]:
        return 0, 0


class TestSectorMap(TestMap, SectorMap):
    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(TestSectorMap, self).__init__(galaxy, routes, output_path, writer)
