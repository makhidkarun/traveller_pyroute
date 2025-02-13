import json

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.NoneCalculation import NoneCalculation
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

    def setupOneWorldAllSectors(self, loc: str = "0102"):
        for sector in range(5):
            sec = self.galaxy.sectors[sector]
            star = Star.parse_line_into_star(
                f"{loc} Shana Ma             E551112-7 Lo Po                {{ -3 }} (300-3) [1113] B     - A 913 9  I{sector} K2 IV M7 V ",
                sec, 'fixed', 'negative')
            self.galaxy.add_star_to_galaxy(star, sector, sec)

    def setupOneWorldCoreSector(self, loc: str, counter: int, allegiance: str = "Im"):
        star = Star.parse_line_into_star(
            f"{loc} Shana Ma             E551112-7 Lo Po                {{ -3 }} (300-3) [1113] B     - A 913 9  {allegiance} K2 IV M7 V     ",
            self.galaxy.sectors[0], 'fixed', 'negative')
        self.galaxy.add_star_to_galaxy(star, counter, self.galaxy.sectors[0])

    @staticmethod
    def dump_dict_to_json(targ_dict, rawfile):
        raw = {str(k): v for (k, v) in targ_dict.items()}
        raw = json.dumps(raw)
        with open(rawfile, 'w+', encoding="utf-8") as outfile:
            outfile.write(raw)

    @staticmethod
    def load_dict_from_json(rawfile):
        raw = None
        with open(rawfile, 'r', encoding="utf-8") as infile:
            raw = json.load(infile)
        assert isinstance(raw, dict), "Loaded file could not be restored to python dict"
        mid = dict()
        rawkey: str
        for rawkey in raw:
            value = raw[rawkey]
            rawstrip = rawkey.strip('()')
            bitz = rawstrip.split(',')
            nu_key = (int(bitz[0]), int(bitz[1]))
            assert nu_key not in mid, "Key " + str(nu_key) + " duplicated in dict file " + rawfile
            mid[nu_key] = value
        return mid
