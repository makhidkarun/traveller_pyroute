"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""
import logging

from typing import Union
from typing_extensions import TypeAlias

from PyRoute.AreaItems.Galaxy import Galaxy, AreaItem
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.HexSystem import HexSystem
from PyRoute.Outputs.MapOutput import MapOutput

Scheme: TypeAlias = str


class Map(MapOutput):

    def __init__(self, galaxy: Galaxy, routes: str, output_path: str, writer: str):
        super(Map, self).__init__(galaxy, routes, output_path, writer)
        self.logger = logging.getLogger('PyRoute.Outputs.Map')
        self.galaxy: Galaxy = galaxy
        self.routes: str = routes
        self.start: Cursor = Cursor(0, 0)
        self.hex_size: Cursor = Cursor(6, 9)
        self.system_writer_type: str = writer
        self.system_writer: HexSystem

    def write_maps(self) -> None:
        raise NotImplementedError("Base Class")

    def write_base_map(self, sector: AreaItem) -> None:
        raise NotImplementedError("Base Class")

    def area_name_title(self, area_name: str) -> None:
        """
        Set the title of the area at the top of the document as a title
        :param area_name: Name to write
        :return: None
        """
        raise NotImplementedError("Base Class")

    def draw_borders(self, sector: AreaItem) -> None:
        raise NotImplementedError("Base Class")

    def coreward_name(self, name: str) -> None:
        raise NotImplementedError("Base Class")

    def rimward_name(self, name: str) -> None:
        raise NotImplementedError("Base Class")

    def spinward_name(self, name: str) -> None:
        raise NotImplementedError("Base Class")

    def trailing_name(self, name: str) -> None:
        raise NotImplementedError("Base Class")

    # An implementation of the Liang–Barsky algorithm for clipping lines.
    # https://en.wikipedia.org/wiki/Liang%E2%80%93Barsky_algorithm
    # This is used by the route drawing process when trade and comm lines cross over borders.
    @staticmethod
    def clipping(minpos: Cursor, maxpos: Cursor, start: Cursor, end: Cursor) -> Union[tuple[Cursor, Cursor], tuple[None, None]]:
        p1 = -(end.x - start.x)
        p2 = -p1
        p3 = -(end.y - start.y)
        p4 = -p3

        q1 = start.x - minpos.x
        q2 = maxpos.x - start.x
        q3 = start.y - minpos.y
        q4 = maxpos.y - start.y

        posarr = [1.0]
        negarr = [0.0]

        # reject as parallel to the borders of the clipping window.
        if (p1 == 0 and q1 < 0) or (p2 == 0 and q2 < 0) or (p3 == 0 and q3 < 0) or (p4 == 0 and q4 < 0):
            return None, None

        if p1 != 0:
            r1 = q1 / p1
            r2 = q2 / p2
            if p1 < 0:
                negarr.append(r1)  # for negative p1, add it to negative array
                posarr.append(r2)  # and add p2 to positive array
            else:
                negarr.append(r2)
                posarr.append(r1)
        if p3 != 0:
            r3 = q3 / p3
            r4 = q4 / p4
            if p3 < 0:
                negarr.append(r3)
                posarr.append(r4)
            else:
                negarr.append(r4)
                posarr.append(r3)
        rn1 = max(negarr)
        rn2 = min(posarr)
        if rn1 > rn2:  # Reject as outside the clipping window
            return None, None

        # Computing new points
        xn1 = start.x + p2 * rn1
        yn1 = start.y + p4 * rn1

        xn2 = start.x + p2 * rn2
        yn2 = start.y + p4 * rn2

        return Cursor(xn1, yn1), Cursor(xn2, yn2)
