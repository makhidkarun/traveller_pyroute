"""
Created on Aug 29, 2023

@author: CyberiaResurrection
"""
import functools


class Hex(object):

    position = None  # Hex location
    row = 0  # Location in the sector.
    col = 0
    dx = 0  # location in the whole space, row/column coordinate
    dy = 0
    q = 0   # location in the whole of space, axial coordinates
    r = 0

    def __init__(self, sector, position):
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

    def distance(self, other):
        return Hex.axial_distance((self.q, self.r), (other.q, other.r))

    def __str__(self):
        return f"{self.col:02d}{self.row:02d}"

    # Used to calculate distances for the AllyGen, which keeps only the q/r (axial) coordinates.
    @staticmethod
    def axial_distance(Hex1, Hex2):
        dq = Hex1[0] - Hex2[0]
        dr = Hex1[1] - Hex2[1]
        return Hex._axial_core(dq, dr)

    @staticmethod
    @functools.cache
    def _axial_core(dq, dr):
        return (abs(dq) + abs(dr) + abs(dq + dr)) // 2

    # Used to calculate distances for the TradeCalculation via the Network Graph, which requires a function
    @staticmethod
    def heuristicDistance(star1, star2):
        return star1.hex.distance(star2.hex)

    def hex_distance(self, star):
        return Hex._hex_core(self.x - star.x, self.y - star.y, self.z - star.z)

    @staticmethod
    @functools.cache
    def _hex_core(dx, dy, dz):
        return max(abs(dx), abs(dy), abs(dz))

    @functools.cache
    def hex_position(self):
        return (self.q, self.r)

    @staticmethod
    def get_neighbor(hex_pos, direction, distance=1):
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
            [+1, 0], [+1, -1], [0, -1],
            [-1, 0], [-1, +1], [0, +1]
        ]
        d = neighbors[direction]
        qn = hex_pos[0] + (d[0] * distance)
        rn = hex_pos[1] + (d[1] * distance)
        return (int(qn), int(rn))

    @staticmethod
    def hex_to_axial(row, col):
        q = row
        q_offset = (q + (q & 1)) // 2
        r = col - q_offset
        return q, r

    @staticmethod
    def axial_to_hex(q, r):
        row = q
        q_offset = (q + (q & 1)) // 2
        col = r + q_offset

        return row, col

    @staticmethod
    def axial_to_sector(q, r):
        (raw_row, raw_col) = Hex.axial_to_hex(q, r)

        row = Hex.dy_offset(raw_row, 0)

        return row, raw_col

    @staticmethod
    def dy_offset(row: int, sector_y: int) -> int:
        offset = 41 - row - 1
        return sector_y * 40 + offset

    @property
    def x(self):
        return self.q

    @property
    def y(self):
        return -self.q - self.r

    @property
    def z(self):
        return self.r
