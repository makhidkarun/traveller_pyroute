from PyRoute.Calculation.NoneCalculation import NoneCalculation
from PyRoute.Galaxy import Galaxy, Sector, Subsector
from PyRoute.Star import Star
from Tests.baseTest import baseTest


class TestAllyGenBase(baseTest):
    
    galaxy: Galaxy = None
    
    def setUp(self):
        self.galaxy = Galaxy(min_btn=14)
        self.galaxy.debug_flag = True
        self.galaxy.trade = NoneCalculation(self)
        core_sector = Sector('# Core', '# 0, 0')
        core_sector.subsectors['A'] = Subsector('CoreA', 'A', core_sector)
        core_sector.subsectors['E'] = Subsector('CoreE', 'E', core_sector)
        core_sector.subsectors['F'] = Subsector('CoreF', 'F', core_sector)
        lish_sector = Sector('# Lishun', '# 0, 1')
        lish_sector.subsectors['A'] = Subsector('Lish', 'A', lish_sector)
        dagu_sector = Sector('# Dagudashaag', '# -1, 0')
        dagu_sector.subsectors['A'] = Subsector('Dagu', 'A', dagu_sector)
        mass_sector = Sector('# Massilia', '# 0, -1')
        mass_sector.subsectors['A'] = Subsector('Mass', 'A', mass_sector)
        forn_sector = Sector('# Fornast', '# 1, 0')
        forn_sector.subsectors['A'] = Subsector('Forn', 'A', forn_sector)

        self.galaxy.sectors[0] = core_sector
        self.galaxy.sectors[1] = lish_sector
        self.galaxy.sectors[2] = dagu_sector
        self.galaxy.sectors[3] = mass_sector
        self.galaxy.sectors[4] = forn_sector
        self.borders = self.galaxy.borders

    def setupOneWorldAllSectors(self, loc:str = "0102"):
        for sector in range(5):
            sec = self.galaxy.sectors[sector]
            star = Star.parse_line_into_star(
                f"{loc} Shana Ma             E551112-7 Lo Po                {{ -3 }} (300-3) [1113] B     - A 913 9  I{sector} K2 IV M7 V ",
                sec, 'fixed', 'negative')
            self.galaxy.add_star_to_galaxy(star, sector, sec)

    def setupOneWorldCoreSector(self, loc:str, counter:int, allegiance:str = "Im"):
        star = Star.parse_line_into_star(
            f"{loc} Shana Ma             E551112-7 Lo Po                {{ -3 }} (300-3) [1113] B     - A 913 9  {allegiance} K2 IV M7 V     ",
            self.galaxy.sectors[0], 'fixed', 'negative')
        self.galaxy.add_star_to_galaxy(star, counter, self.galaxy.sectors[0])
