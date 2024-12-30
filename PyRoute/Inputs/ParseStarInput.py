"""
Created on Nov 27, 2023

@author: CyberiaResurrection
"""
import re

from lark import UnexpectedCharacters, UnexpectedEOF

from PyRoute.Inputs.StarlineStationParser import StarlineStationParser
from PyRoute.Inputs.StarlineStationTransformer import StarlineStationTransformer
from PyRoute.Inputs.StarlineTransformer import StarlineTransformer
from PyRoute.Inputs.StarlineParser import StarlineParser
from PyRoute.Nobles import Nobles
from PyRoute.SystemData.UWP import UWP
from PyRoute.SystemData.Utilities import Utilities
from PyRoute.TradeCodes import TradeCodes


class ParseStarInput:
    regex = """
^((?:0[1-9]|[1-2]\d|3[0-2])(?:0[1-9]|40|[1-3]\d)) +
(.{15,}) +
([A-HXYa-hxy][0-9A-Fa-f]\w\w[0-9A-Fa-f][0-9A-Xa-x][0-9A-Ja-j]-\w|\?\?\?\?\?\?\?-\?|[A-HXYa-hxy\?][0-9A-Fa-f\?][\w\?]{2,2}[0-9A-Fa-f\?][0-9A-Xa-x\?][0-9A-Ja-j\?]-[\w\?]) +
(.{15,}) +
((\{ *[ +-]?[0-6] ?\}|-) +(\([0-9A-Za-z]{3}[+-]\d\)|- ) +(\[[0-9A-Za-z]{4}\]|- )|( ) ( ) ( )) +
([BcCDeEfFGH]{1,5}|-| ) +
([A-Z]{1,3}|-|\*) +
([ARUFGBarufgb]|-| ) +
([0-9X?][0-9A-FX?][0-9A-FX?]) +
(\d{1,}| ) +
([A-Z0-9?-][A-Za-z0-9?-]{1,3})
(.*)
"""
    # Hex position in the sector
    # Name of the system
    # UWP
    # Trade Codes
    # Ix, Ex, Cx The T5 Extensions
    # Nobility codes
    # Base codes
    # Travel Zone Code
    # PBG code (Population, Belts, Gas Giants
    # World Count
    # Allegiance
    # Stars and star data (parsed separately)
    starline = re.compile(''.join([line.rstrip('\n') for line in regex]))
    parser = None
    transformer = None
    station_parser = None
    station_transformer = None
    deep_space = {}
    valid_zone = 'arufgbARUFGB-'
    valid_nobles = 'BCcDEeFfGH-'

    @staticmethod
    def parse_line_into_star_core(star, line, sector, pop_code, ru_calc, fix_pop=False):
        star.sector = sector
        star.logger.debug(line)
        data, is_station = ParseStarInput._unpack_starline(star, line, sector)
        if data is None:
            return None

        star.logger.debug(data)

        star.position = data[0].strip()
        star.set_location()
        star.name = data[1].strip()

        try:
            star.uwp = UWP(data[2].strip())
        except ValueError as e:
            if 'Input UWP malformed' == str(e):
                return None
            raise e
        star.tradeCode = TradeCodes(data[3].strip())
        star.ownedBy = star.tradeCode.owned_by(star)

        raw_economics = data[6].strip().upper() if data[6] else None
        if raw_economics is not None:
            star.economics = raw_economics if 7 == len(raw_economics) else None
        raw_social = data[7].strip().upper() if data[7] else None
        if raw_social is not None:
            star.social = raw_social if 6 == len(raw_social) else None

        star.nobles = Nobles()
        star.nobles.count(data[11])

        star.baseCode = data[12].strip()
        if ('' == star.baseCode) or ('-' != star.baseCode and 1 == len(star.baseCode) and not star.baseCode.isalpha()):
            star.baseCode = '-'
        star.zone = data[13].strip()
        if not star.zone or star.zone not in ParseStarInput.valid_zone:
            star.zone = '-'
        star.zone = star.zone.upper()
        star.ggCount = 0 if (len(data[14]) < 3 or not data[14][2] or data[14][2] in 'X?') else int(data[14][2], 16)
        star.popM = 0 if data[14][0] in 'X?' else int(data[14][0])
        star.belts = 0 if (len(data[14]) < 2 or data[14][1] in 'X?') else int(data[14][1], 16)

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

        if data[5] and data[5].startswith('{'):
            raw_imp = data[5][1:-1].strip()
            imp = 0
            if '' != raw_imp:
                imp = int(raw_imp)
            star.calculate_importance()
            if imp != star.importance:
                star.logger.warning(
                    '{}-{} IX Calculated importance {} does not match generated importance {}'.
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
        if is_station:
            star.deep_space_station = True
            if star.allegiance_base is None or '?' == star.alg_code:
                star.allegiance_base = 'Na'
                star.alg_code = 'Na'
                star.alg_base_code = 'Na'
        return star

    @staticmethod
    def _unpack_starline(star, line, sector):
        is_station = False
        if '{Anomaly}' in line and sector.name not in ParseStarInput.deep_space:
            star.logger.info("Found anomaly, skipping processing: {}".format(line))
            return None, None
        elif sector.name in ParseStarInput.deep_space:
            if line[0:4] not in ParseStarInput.deep_space[sector.name]:
                if '{Anomaly}' in line:
                    star.logger.info("Found anomaly, skipping processing: {}".format(line))
                    return None, None
            else:
                is_station = True

        if ParseStarInput.parser is None:
            ParseStarInput.parser = StarlineParser()
        if ParseStarInput.station_parser is None:
            ParseStarInput.station_parser = StarlineStationParser()
        try:
            if is_station:
                result, line = ParseStarInput.station_parser.parse(line)
            else:
                result, line = ParseStarInput.parser.parse(line)
        except UnexpectedCharacters:
            result = ParseStarInput._unpack_starline_fallback(line)
            if result is None:
                star.logger.error("Unmatched line: {}".format(line))
                return None, None
        except UnexpectedEOF:
            result = ParseStarInput._unpack_starline_fallback(line)
            if result is None:
                star.logger.error("Unmatched line: {}".format(line))
                return None, None
        if ParseStarInput.transformer is None:
            ParseStarInput.transformer = StarlineTransformer(raw=line)
        else:
            ParseStarInput.transformer.raw = line
            ParseStarInput.transformer.crankshaft = False
        if ParseStarInput.station_transformer is None:
            ParseStarInput.station_transformer = StarlineStationTransformer(raw=line)
        else:
            ParseStarInput.station_transformer.raw = line
            ParseStarInput.station_transformer.crankshaft = False

        if not isinstance(result, list):
            if is_station:
                transformed = ParseStarInput.station_transformer.transform(result)
            else:
                transformed = ParseStarInput.transformer.transform(result)
        else:
            transformed = result

        return transformed, is_station

    @staticmethod
    def _unpack_starline_fallback(line):
        matches = ParseStarInput.starline.match(line)
        if matches is None:
            return
        data = list(matches.groups())
        parsed = {'position': data[0], 'name': data[1], 'uwp': data[2], 'trade': data[3]}
        raw_extensions = data[4].replace('  ', ' ').replace('{ ', '{').replace(' }', '}')
        oldlen = 0
        while oldlen != len(raw_extensions):
            oldlen = len(raw_extensions)
            raw_extensions = raw_extensions.replace('  ', ' ').replace('{ ', '{').replace(' }', '}')
        if 2 <= raw_extensions.count(' '):
            bitz = raw_extensions.split(' ')
            bitz = [item for item in bitz if '' != item]
            parsed['ix'] = bitz[0]
            parsed['ex'] = bitz[1]
            parsed['cx'] = bitz[2]
        else:
            parsed['ix'] = ' ' if data[8] is None else data[8]
            parsed['ex'] = ' ' if data[9] is None else data[9]
            parsed['cx'] = ' ' if data[10] is None else data[10]
        parsed['nobles'] = data[11]
        parsed['base'] = data[12]
        parsed['zone'] = data[13]
        parsed['pbg'] = data[14]
        parsed['worlds'] = data[15]
        parsed['allegiance'] = data[16]
        parsed['residual'] = data[17]

        extensions = parsed['ix'] + ' ' + parsed['ex'] + ' ' + parsed['cx']

        spacer = ' '
        data = [parsed['position'], parsed['name'], parsed['uwp'], parsed['trade'], extensions, parsed['ix'], parsed['ex'], parsed['cx'], spacer, spacer, spacer, parsed['nobles'], parsed['base'], parsed['zone'].upper(), parsed['pbg'], parsed['worlds'], parsed['allegiance'], parsed['residual']]

        data = ParseStarInput._unpack_starline_tweak(data)
        return data

    @staticmethod
    def _unpack_starline_tweak(data):
        data[1] = data[1].replace('  ', ' ')
        if data[16].startswith('--') and '----' != data[16]:
            if 2 < len(data[16]):
                data[17] = data[16][2:] + " " + data[17]
                data[16] = '--'

        return data

    @staticmethod
    def check_tl(star, fullmsg=None):
        if '???-' in str(star.uwp) or star.tl_unknown:
            return

        max_tl, min_tl = ParseStarInput.check_tl_core(star)

        if min_tl <= star.tl <= max_tl:
            return

        msg = '{}-{} Calculated TL "{}" not in range {}-{}'.format(star, star.uwp, star.tl, min_tl, max_tl)

        if not isinstance(fullmsg, list):
            star.logger.error(msg)
        else:
            fullmsg.append(msg)

    @staticmethod
    def check_tl_core(star):
        mod = 0
        if star.size in '01':
            mod += 2
        elif star.size in '234':
            mod += 1
        if star.atmo in '0123ABCDEF':
            mod += 1
        if star.hydro in '9A':
            mod += 1
        if 'A' == star.hydro:
            mod += 1
        if star.pop in '123459ABCDEF':
            mod += 1
        if star.pop in '9ABCDEF':
            mod += 1
        if star.pop in 'ABCDEF':
            mod += 2
        if star.gov in '05':
            mod += 1
        elif 'D' == star.gov:
            mod -= 2
        if 'X' == star.port:
            mod -= 4
        if star.port in 'ABC':
            mod += 2
        if star.port in 'AB':
            mod += 2
        if 'A' == star.port:
            mod += 2
        min_tl = max(0, mod + 1)
        max_tl = mod + 6
        return max_tl, min_tl

    @staticmethod
    def can_be_nobles(segment) -> bool:
        if not isinstance(segment, str):
            return False

        if '-' == segment.strip():
            return True

        non_noble = [item for item in segment if item not in ParseStarInput.valid_nobles]
        return 0 == len(non_noble)

    @staticmethod
    def can_be_base(segment) -> bool:
        if not isinstance(segment, str):
            return False

        if '-' == segment or '*' == segment or ' ' == segment:
            return True

        if 3 < len(segment):
            return False

        return segment.isupper()
