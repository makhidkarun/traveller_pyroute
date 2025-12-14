"""
Created on 21 Jul, 2024

@author: CyberiaResurrection
"""
import re
from typing import Optional

from PyRoute.Star import Star
from PyRoute.AreaItems.AreaItem import AreaItem


class Sector(AreaItem):
    position_match = re.compile(r"([-+ ]?\d{1,4})\s*[,]\s*([-+ ]?\d{1,4})")

    def __init__(self, name, position):
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        if not isinstance(position, str):
            raise ValueError("Position must be a string")
        name = name.strip()
        if 3 > len(name):
            raise ValueError("Name string too short")
        if 5 > len(position):
            raise ValueError("Position string too short")
        if '#' != name[0]:
            raise ValueError("Name string should start with #")
        if '#' != position[0]:
            raise ValueError("Position string should start with #")

        # Pre-trim input values

        # The name as passed from the Galaxy read include the comment marker at the start of the line
        # So strip the comment marker, then strip spaces.
        super(Sector, self).__init__(name[1:].strip())

        # Same here, the position has a leading comment marker.  Strip that, and then any flanking whitespace.
        position = position[1:].strip()
        positions = Sector.position_match.match(position)
        if not positions:
            raise ValueError("Position string malformed")

        pos_bits = positions.groups()

        self.x = int(pos_bits[0])
        self.y = int(pos_bits[1])

        self._wiki_name = '[[{0} Sector|{0}]]'.format(self.sector_name())

        self.dx = self.x * 32
        self.dy = self.y * 40
        self.subsectors = {}
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        self.filename = None

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['spinward']
        del state['trailing']
        del state['coreward']
        del state['rimward']
        del state['alg_sorted']
        return state

    def __str__(self):
        return '{} ({},{})'.format(self.name, str(self.x), str(self.y))

    def __eq__(self, other):
        if not isinstance(other, Sector):
            return False
        return str(self) == str(other)

    def sector_name(self) -> str:
        return self.name.removesuffix(' Sector').removesuffix('Sector').strip()

    def find_world_by_pos(self, pos) -> Optional[Star]:
        for world in self.worlds:
            if world.position == pos:
                return world
        return None

    def is_well_formed(self) -> tuple[bool, str]:
        # check name
        if self.name is None or '' == self.name.strip():
            msg = "Name cannot be empty"
            return False, msg

        # Check reciprocity of adjacent sectors
        if self.coreward is not None:
            neighbour = self.coreward
            other = neighbour.rimward
            if other is None or other != self:
                msg = "Coreward sector mismatch for " + self.name
                return False, msg
            if self.x != neighbour.x:
                msg = "Coreward sector x co-ord mismatch for " + self.name
                return False, msg
            if self.y + 1 != neighbour.y:
                msg = "Coreward sector y co-ord mismatch for " + self.name
                return False, msg
        if self.rimward is not None:
            neighbour = self.rimward
            other = neighbour.coreward
            if other is None or other != self:
                msg = "Rimward sector mismatch for " + self.name
                return False, msg
            if self.x != neighbour.x:
                msg = "Rimward sector x co-ord mismatch for " + self.name
                return False, msg
            if self.y - 1 != neighbour.y:
                msg = "Rimward sector y co-ord mismatch for " + self.name
                return False, msg
        if self.spinward is not None:
            neighbour = self.spinward
            other = neighbour.trailing
            if other is None or other != self:
                msg = "Spinward sector mismatch for " + self.name
                return False, msg
            if self.x - 1 != neighbour.x:
                msg = "Spinward sector x co-ord mismatch for " + self.name
                return False, msg
            if self.y != neighbour.y:
                msg = "Spinward sector y co-ord mismatch for " + self.name
                return False, msg
        if self.trailing is not None:
            neighbour = self.trailing
            other = neighbour.spinward
            if other is None or other != self:
                msg = "Trailing sector mismatch for " + self.name
                return False, msg
            if self.x + 1 != neighbour.x:
                msg = "Trailing sector x co-ord mismatch for " + self.name
                return False, msg
            if self.y != neighbour.y:
                msg = "Trailing sector y co-ord mismatch for " + self.name
                return False, msg

        result, msg = self._check_allegiance_counts_well_formed()
        if not result:
            return False, msg

        return True, msg

    def _check_allegiance_counts_well_formed(self):
        sector_count = dict()
        subsector_count = dict()

        for alg in self.alg:
            sector_count[alg] = len(self.alg[alg].worlds)
            subsector_count[alg] = 0

        for position in self.subsectors:
            for alg in self.subsectors[position].alg:
                if alg not in sector_count:
                    return False, "Allegiance " + alg + " found in subsector " + position + " but not sector"
                subsector_count[alg] += len(self.subsectors[position].alg[alg].worlds)

        for alg in sector_count:
            if sector_count[alg] != subsector_count[alg]:
                return False, "Allegiance " + alg + " has " + str(sector_count[alg]) + " worlds at sector, and "\
                       + str(subsector_count[alg]) + " totalled across subsectors"

        return True, ""
