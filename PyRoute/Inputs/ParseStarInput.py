"""
Created on Nov 27, 2023

@author: CyberiaResurrection
"""
import re

from lark import UnexpectedCharacters, UnexpectedEOF

from PyRoute.Inputs.StarlineTransformer import StarlineTransformer
from PyRoute.Inputs.StarlineParser import StarlineParser
from PyRoute.Nobles import Nobles
from PyRoute.SystemData.UWP import UWP
from PyRoute.SystemData.Utilities import Utilities
from PyRoute.TradeCodes import TradeCodes


class ParseStarInput:
    regex = """
^([0-3]\d[0-4]\d) +
(.{15,}) +
(\w\w\w\w\w\w\w-\w|\?\?\?\?\?\?\?-\?|[\w\?]{7,7}-[\w\?]) +
(.{15,}) +
((\{ *[+-]?[0-6] ?\}) +(\([0-9A-Za-z]{3}[+-]\d\)|- ) +(\[[0-9A-Za-z]{4}\]|- )|( ) ( ) ( )) +
([BcCDeEfFGH]{1,5}|-| ) +
([A-Z]{1,3}|-|\*) +
([ARUFGBarufgb]|-| ) +
([0-9X?][0-9A-FX?][0-9A-FX?]) +
(\d{1,}| ) +
([A-Z0-9?-][A-Za-z0-9?-]{1,3})
(.*)
"""
    starline = re.compile(''.join([line.rstrip('\n') for line in regex]))
    parser = None
    transformer = None

    @staticmethod
    def parse_line_into_star_core(star, line, sector, pop_code, ru_calc, fix_pop=False):
        star.sector = sector
        star.logger.debug(line)
        data = ParseStarInput._unpack_starline(star, line)
        if data is None:
            return None

        star.logger.debug(data)

        star.position = data[0].strip()
        star.set_location()
        result, _ = star.hex.is_well_formed()
        if not result:
            return None  # If hex position is bad, bail out - error is fatal
        star.name = data[1].strip()

        try:
            star.uwp = UWP(data[2].strip())
        except ValueError as e:
            if 'Input UWP malformed' == str(e):
                return None
            raise e
        star.tradeCode = TradeCodes(data[3].strip())
        star.ownedBy = star.tradeCode.owned_by(star)

        star.economics = data[6].strip().upper() if data[6] and data[6].strip() != '-' else None
        star.social = data[7].strip().upper() if data[7] and data[7].strip() != '-' else None

        star.nobles = Nobles()
        star.nobles.count(data[11])

        star.baseCode = data[12].strip()
        if ('' == star.baseCode) or ('-' != star.baseCode and 1 == len(star.baseCode) and not star.baseCode.isalpha()):
            star.baseCode = '-'
        star.zone = data[13].strip()
        if not star.zone or star.zone not in 'arufARUF-':
            star.zone = '-'
        star.zone = star.zone.upper()
        star.ggCount = int(data[14][2], 16) if data[14][2] not in 'X?' else 0
        star.popM = int(data[14][0]) if data[14][0] not in 'X?' else 0
        star.belts = int(data[14][1], 16) if data[14][1] not in 'X?' else 0

        star.worlds = int(data[15]) if data[15].strip().isdigit() else 0

        star.alg_code = data[16].strip()
        star.alg_base_code = star.alg_code

        star.stars = data[17].strip()
        star.extract_routes()
        try:
            star.split_stellar_data()
        except ValueError as e:
            if 'No stars found' == str(e):
                return None
            raise e

        star.tradeIn = 0
        star.tradeOver = 0
        star.tradeCount = 0
        star.passIn = 0
        star.passOver = 0
        star.starportSize = 0
        star.starportBudget = 0
        star.starportPop = 0

        star.tradeCode.check_world_codes(star, fix_pop=fix_pop)

        if data[5]:
            imp = int(data[5][1:-1].strip())
            star.calculate_importance()
            if imp != star.importance:
                star.logger.warning(
                    '{}-{} Calculated importance {} does not match generated importance {}'.
                    format(star, star.baseCode, star.importance, imp))
        else:
            star.calculate_importance()

        star.uwpCodes = {'Starport': star.port,
                         'Size': star.size,
                         'Atmosphere': star.atmo,
                         'Hydrographics': star.hydro,
                         'Population': star.pop,
                         'Government': star.gov,
                         'Law Level': star.law,
                         'Tech Level': star.tl,
                         'Pop Code': str(star.popM),
                         'Starport Size': star.starportSize,
                         'Primary Type': star.primary_type if star.primary_type else 'X',
                         'Importance': star.importance,
                         'Resources': Utilities.ehex_to_int(star.economics[1]) if star.economics else 0
                         }

        if fix_pop is True:
            star.fix_ex()
        else:
            star.check_ex()
        star.check_cx()

        star.calculate_wtn()
        star.calculate_mspr()
        star.calculate_gwp(pop_code)

        star.calculate_TCS()
        star.calculate_army()
        star.calculate_ru(ru_calc)

        star.eti_cargo_volume = 0
        star.eti_pass_volume = 0
        star.eti_cargo = 0
        star.eti_passenger = 0
        star.eti_worlds = 0
        star.calculate_eti()

        star.trade_id = None  # Used by the Speculative Trade
        star.calc_hash()
        star.calc_passenger_btn_mod()
        return star

    @staticmethod
    def _unpack_starline(star, line):
        if '{Anomaly}' in line:
            star.logger.info("Found anomaly, skipping processing: {}".format(line))
            return None

        if ParseStarInput.parser is None:
            ParseStarInput.parser = StarlineParser()
        try:
            result, line = ParseStarInput.parser.parse(line)
        except UnexpectedCharacters:
            star.logger.error("Unmatched line: {}".format(line))
            return None
        except UnexpectedEOF:
            star.logger.error("Unmatched line: {}".format(line))
            return None
        if ParseStarInput.transformer is None:
            ParseStarInput.transformer = StarlineTransformer(raw=line)
        else:
            ParseStarInput.transformer.raw = line
            ParseStarInput.transformer.crankshaft = False
        transformed = ParseStarInput.transformer.transform(result)

        return transformed
