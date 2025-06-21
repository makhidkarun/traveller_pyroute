"""
Created on 21 Jul, 2024

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.AreaItem import AreaItem


class Subsector(AreaItem):
    def __init__(self, name, position, sector):
        super(Subsector, self).__init__(name)
        self.positions = ["ABCD", "EFGH", "IJKL", "MNOP"]
        self.sector = sector
        self.position = position
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        self.dx = sector.dx
        self.dy = sector.dy
        self._wiki_name = Subsector.set_wiki_name(name, sector.name, position)

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sector']
        del state['spinward']
        del state['trailing']
        del state['coreward']
        del state['rimward']
        del state['alg_sorted']
        del state['positions']
        return state

    @staticmethod
    def set_wiki_name(name, sector_name, position) -> str:
        if len(name) == 0:
            return "{0} location {1}".format(sector_name, position)
        else:
            if "(" in name:
                return '[[{0} Subsector|{1}]]'.format(name, name[:-7])
            else:
                return '[[{0} Subsector|{0}]]'.format(name)

    def wiki_title(self) -> str:
        return '{0} - {1}'.format(self.wiki_name(), self.sector.wiki_name())

    def subsector_name(self) -> str:
        if len(self.name) == 0:
            return "Location {}".format(self.position)
        else:
            return self.name[:-9] if self.name.endswith('Subsector') else self.name

    def set_bounding_subsectors(self) -> None:
        posrow = 0
        for row in self.positions:
            if self.position in row:
                pos = self.positions[posrow].index(self.position)
                break
            posrow += 1

        if posrow == 0:
            self.coreward = self.sector.coreward.subsectors[self.positions[3][pos]] if self.sector.coreward else None
        else:
            self.coreward = self.sector.subsectors[self.positions[posrow - 1][pos]]

        if pos == 0:
            self.spinward = self.sector.spinward.subsectors[self.positions[posrow][3]] if self.sector.spinward else None
        else:
            self.spinward = self.sector.subsectors[self.positions[posrow][pos - 1]]

        if posrow == 3:
            self.rimward = self.sector.rimward.subsectors[self.positions[0][pos]] if self.sector.rimward else None
        else:
            self.rimward = self.sector.subsectors[self.positions[posrow + 1][pos]]

        if pos == 3:
            self.trailing = self.sector.trailing.subsectors[self.positions[posrow][0]] if self.sector.trailing else None
        else:
            self.trailing = self.sector.subsectors[self.positions[posrow][pos + 1]]
