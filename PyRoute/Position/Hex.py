"""
Created on Aug 29, 2023

@author: CyberiaResurrection
"""
import functools
from typing import Tuple
from typing_extensions import TypeAlias

HexPos: TypeAlias = Tuple[int, int]


class Hex(object):

    position: str = None  # Hex location
    row: int = 0  # Location in the sector.
    col: int = 0
    dx: int = 0  # location in the whole space, row/column coordinate
    dy: int = 0
    q: int = 0   # location in the whole of space, axial coordinates
    r: int = 0

    # Hex-side alias constants
    BOTTOM = 1
    BOTTOMRIGHT = 2
    BOTTOMLEFT = 4

    def __init__(self, sector, position: str):
        """
        # The zero point of the co-ordinate system used is Reference (Core 0140).
        # As a result, hex position 01,40 becomes q=0, r=0, x=0, y=0, z=0.
        """

        self.position = position
        self.col = int(self.position[0:2])
        self.row = int(self.position[2:4])
        self.dx = sector.x * 32 + self.col - 1
        self.dy = sector.y * 40 + self.row - 1
        self.q, self.r = Hex.hex_to_axial(self.dx, Hex.dy_offset(self.row, sector.y))
        self._hash = hash((self.position, self.dx, self.dy))

    def __str__(self):
        return f"{self.col:02d}{self.row:02d}"

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if self.__hash__() != other.__hash__():
            return False
        if not isinstance(other, Hex):
            return False

        if self.position != other.position:
            return False
        if self.dx != other.dx:
            return False
        return not self.dy != other.dy

    def distance(self, other):
        return Hex.axial_distance((self.q, self.r), (other.q, other.r))

    # Used to calculate distances for the AllyGen, which keeps only the q/r (axial) coordinates.
    @staticmethod
    def axial_distance(Hex1: HexPos, Hex2: HexPos):
        return Hex._axial_core(Hex1[0] - Hex2[0], Hex1[1] - Hex2[1])

    @staticmethod
    @functools.cache
    def _axial_core(dq: int, dr: int):
        return (abs(dq) + abs(dr) + abs(dq + dr)) // 2

    # Used to calculate distances for the TradeCalculation via the Network Graph, which requires a function
    @staticmethod
    def heuristicDistance(star1, star2):
        return star1.hex.distance(star2.hex)

    def hex_distance(self, star):
        return Hex._hex_core(self.x - star.x, self.y - star.y, self.z - star.z)

    @staticmethod
    @functools.cache
    def _hex_core(dx: int, dy: int, dz: int):
        return max(abs(dx), abs(dy), abs(dz))

    @functools.cache
    def hex_position(self) -> HexPos:
        return self.q, self.r

    def get_neighbour(self, direction: int, distance: int = 1):
        return Hex.get_neighbor(self.hex_position(), direction, distance)

    @staticmethod
    def get_neighbor(hex_pos: HexPos, direction: int, distance: int = 1) -> HexPos:
        """
        determine neighboring hex from the q,r position and direction.
        Direction index is:
        0 => Down / right
        1 => Up / right
        2 => Up
        3 => Up / left
        4 => Down / left
        5 => Down
        """
        neighbors = [
            [+1, -1], [+1, 0], [0, +1],
            [-1, +1], [-1, 0], [0, -1]
        ]
        d = neighbors[direction]
        qn = hex_pos[0] + (d[0] * distance)
        rn = hex_pos[1] + (d[1] * distance)
        return int(qn), int(rn)

    @staticmethod
    def hex_to_axial(row: int, col: int) -> HexPos:
        q = row
        q_offset = (q + (q & 1)) // 2
        r = col - q_offset
        return q, r

    @staticmethod
    def axial_to_hex(q: int, r: int):
        row = q
        q_offset = (q + (q & 1)) // 2
        col = r + q_offset

        return row, col

    @staticmethod
    def axial_to_sector(q: int, r: int, flip: bool = False):
        (raw_row, raw_col) = Hex.axial_to_hex(q, r)

        col, _ = Hex.dy_reverse(raw_col)
        row = (raw_row % 32) + 1

        if flip:
            col = 41 - col

        return row, col

    @staticmethod
    def dy_offset(row: int, sector_y: int) -> int:
        offset = 41 - row - 1
        return sector_y * 40 + offset

    @staticmethod
    def dy_reverse(dy_offset: int):
        sector_y = dy_offset // 40
        offset = dy_offset % 40

        row = 40 - offset
        return row, sector_y

    @property
    def x(self):
        return self.q

    @property
    def y(self):
        return -self.q - self.r

    @property
    def z(self):
        return self.r

    def is_well_formed(self):
        msg = ""
        if not (1 <= self.col <= 32):
            msg = "Column must be in range 1-32 - is " + str(self.col)
            return False, msg
        if not (1 <= self.row <= 40):
            msg = "Row must be in range 1-40 - is " + str(self.row)
            return False, msg

        return True, msg
