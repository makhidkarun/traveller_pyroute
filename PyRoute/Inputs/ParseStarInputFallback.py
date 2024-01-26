"""
Created on Oct 15, 2023

@author: CyberiaResurrection
"""
import re


class ParseStarInputFallback:
    # The first fallback regex when straight-up line parsing fails - fallback parsing assumes
    # tradeCodes will be empty
    first_three_regex = """
^(\d\d\d\d) +
(.{15,}) +
([\w\?]\w\w\w\w\w\w-[\w\?]|[X\?]\?\?\?\?\?\?-\?|[ABCDEX\?][\w\?]{3,3}\?\?\?-[\?0-9A-Z]) +
(.{1,})
"""
    first_three_line = re.compile(''.join([line.rstrip('\n') for line in first_three_regex]))

    # Second fallback regex
    ix_cx_ex_regex = """
    ((\{ *[+-]?[0-6] ?\}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]|-)|( ) ( ) ( )) +(\w{1,5}|-| ) +(.*)
        """

    # ix_cx_ex_line = re.compile(''.join([line.rstrip('\n') for line in ix_cx_ex_regex]))
    ix_cx_ex_line = r"((\{ *[+-]?[0-6] ?\}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]|-)|( ) ( ) ( )) +(\w{1,5}|-| ) +(.*)"

    ix_line = r"((\{ *[+-]?[0-6] ?\})"
    cx_line = r" \([0-9A-Z]{3}[+-]\d\)|- "

    # Alternate second fallback, with tradecodes
    ix_cx_ex_alternate_line = r"((.{15,}) +(\{ *[+-]?[0-6] ?\}) +(\([0-9A-Za-z]{3}[+-]\d\)|- ) +(\[[0-9A-Za-z]{4}[\}\]]|-)|( ) ( ) ( )) +(\w{1,5}|-| ) +(.*)"

    # Third fallback regex
    noble_base_zone_pbg_regex = """
(\w{1,3}|-|\*) +(\w|-| ) +(.*)
    """

    # noble_base_zone_line = re.compile(''.join([line.rstrip('\n') for line in noble_base_zone_pbg_regex]))
    noble_base_zone_line = r"(\w{1,3}|-|\*) +(\w|-| ) +(.*)"

    # Last fallback regex
    last_blocks_regex = """
([0-9X?][0-9A-FX?][0-9A-FX?]) +(\d{1,}| ) +([A-Z0-9?-][A-Za-z0-9?-]{1,3}) +(.*)
    """
    # last_blocks_line = re.compile(''.join([line.rstrip('\n') for line in last_blocks_regex]))
    last_blocks_line = r"([0-9X?][0-9A-FX?][0-9A-FX?]) +(\d{1,}| ) +([A-Z0-9?-][A-Za-z0-9?-]{1,3}) +(.*)"

    @staticmethod
    def parse_starline_fallback(star, line):
        bitz = []
        # We've tried classic line parsing, which has failed.  Try the fallback route before giving up.
        matches = ParseStarInputFallback.first_three_line.match(line)
        if not matches:  # fallback has blown up, throw our hands up
            return None
        ix_residual = ParseStarInputFallback._unpack_first_line(bitz, matches)

        ix_select = None
        ix_matches = re.match(ParseStarInputFallback.ix_cx_ex_line, ix_residual)
        if ix_matches:
            ix_select = "main"
        else:  # Straight up extension line didn't match, try fallback
            ix_matches = re.match(ParseStarInputFallback.ix_cx_ex_alternate_line, ix_residual)
            if ix_matches:
                ix_select = "alternate"

        if not ix_select:
            return None
        noble_residual = None
        if "main" == ix_select:
            bitz.append('')  # tradecodes, assumed empty
            noble_residual = ParseStarInputFallback._unpack_extension_chunks(bitz, ix_matches, ix_residual)
        elif "alternate" == ix_select:
            noble_residual = ParseStarInputFallback._unpack_extension_chunks_with_codes(bitz, ix_matches, ix_residual)
        else:
            assert False, "Failure in importance line parsing - this line should never be reached"

        noble_matches = re.match(ParseStarInputFallback.noble_base_zone_line, noble_residual)
        if not noble_matches:
            return None
        residual = ParseStarInputFallback._unpack_noble_data(bitz, noble_matches)

        residual_matches = re.match(ParseStarInputFallback.last_blocks_line, residual)
        if not residual_matches:
            return None

        residual_data = residual_matches.groups()
        for chunk in residual_data:
            bitz.append(chunk)

        return tuple(bitz)

    @staticmethod
    def _unpack_first_line(bitz, matches):
        rawdata = matches.groups()

        bitz.append(rawdata[0])  # star hex
        bitz.append(rawdata[1])  # star name
        bitz.append(rawdata[2])  # star UWP

        # To get here, we're assuming the trade codes entry is a long stream of spaces - ie, empty
        ix_residual = rawdata[3].strip()
        if 1 > len(ix_residual):
            start_bit = rawdata[0] + " " + rawdata[1] + " " + rawdata[2]
            start_len = len(start_bit)
            ix_residual = matches.string[start_len:].strip()
            # Handle weirdness that arises from processing starlines with known physicals but unknown everything else
            if ix_residual.startswith('???-?'):
                ix_residual = ix_residual[5:]

        return ix_residual + " "

    @staticmethod
    def _unpack_extension_chunks(bitz, ix_matches, ix_residual):
        ix_data = ix_matches.groups()
        # ix_data looks to be a little trickier, so the postprocessing is likewise
        split_pos = len(ix_data[0])
        bitz.append(ix_data[0])  # combined Ix, Ex, Cx - extracted to maintain compatibility with original regex
        bitz.append(ix_data[1])  # star Ix
        bitz.append(ix_data[2])  # star Ex
        bitz.append(ix_data[3])  # star Cx
        bitz.append(None)  # not sure why these are here, added to maintain compatibility with original
        bitz.append(None)
        bitz.append(None)
        bitz.append(ix_data[7])  # nobles
        noble_residual = ix_residual[split_pos:].strip()
        split_pos = len(ix_data[7])
        noble_residual = noble_residual[split_pos:].strip() + " "
        return noble_residual

    @staticmethod
    def _unpack_extension_chunks_with_codes(bitz, ix_matches, ix_residual):
        ix_data = ix_matches.groups()
        split_pos = len(ix_data[0])
        bitz.append(ix_data[1])  # trade codes
        bitz.append(ix_data[0])  # combined Ix, Ex, Cx - extracted to maintain compatibility with original regex
        bitz.append(ix_data[2])  # star Ix
        bitz.append(ix_data[3])  # star Ex
        bitz.append(ix_data[4])  # star Cx
        bitz.append(None)  # not sure why these are here, added to maintain compatibility with original
        bitz.append(None)
        bitz.append(None)
        bitz.append(ix_data[8])  # nobles

        noble_residual = ix_residual[split_pos:].strip()
        split_pos = len(ix_data[8])
        noble_residual = noble_residual[split_pos:].strip() + " "
        return noble_residual

    @staticmethod
    def _unpack_noble_data(bitz, noble_matches):
        noble_data = noble_matches.groups()
        bitz.append(noble_data[0])  # base codes
        bitz.append(noble_data[1])  # trade zone
        residual = noble_data[2].strip() + " "
        return residual

    @staticmethod
    def repack_starline_data(rawdata):
        data = list(rawdata)

        rawtrade = data[3]
        # see if splitting by spaces works
        bitz = rawtrade.split()
        imp_dex, bitz = ParseStarInputFallback._find_importance(bitz)

        if 3 < len(bitz) and imp_dex is not None:
            imp_bitz = bitz[imp_dex:]
            bitz = bitz[:imp_dex]

            countdown = [5, 6, 7]

            imp_len = min(len(imp_bitz), len(countdown))
            for i in range(0, imp_len):
                index = countdown[i]
                if data[index] is None:
                    data[index] = imp_bitz[0]
                    del imp_bitz[0]

            data[3] = ' '.join(bitz)
        elif 3 >= len(bitz) and imp_dex is not None:
            data[5] = bitz[imp_dex]

            if 3 == len(bitz) and 2 > imp_dex:
                data[6] = bitz[2]
                bitz[2] = ''

            bitz = [bit for bit in bitz if bit != data[5]]
            data[3] = ' '.join(bitz)

        if 3 == len(bitz) and 1 == imp_dex:
            data[3] = bitz[0]
            data[5] = bitz[1]
            data[6] = bitz[2]

        if data[6] is not None:
            if 1 == len(data[6]) and '-' != data[6]:
                data[6] = '-'

        if data[5] is not None:
            trimmed = data[5].strip('{}')
            trimmed = trimmed.strip()
            trimmed = '0' if '' == trimmed else trimmed
            data[5] = '{ ' + trimmed + ' }'

        return data

    @staticmethod
    def _find_importance(bitz):
        num_bitz = len(bitz)
        # first, try for {\d}
        for i in range(0, num_bitz):
            bit = bitz[i]
            if bit.startswith('{') and bit.endswith('}'):
                trim = bit.strip('{}').strip()
                if 0 == len(trim):
                    continue
                if trim.isdigit():
                    return i, bitz
                if ('-' == trim[0] or '+' == trim[0]) and trim[1:].isdigit():
                    return i, bitz
            if i < num_bitz - 1:
                next = bitz[i + 1].strip()
                if bit.startswith('{') and '}' == next.strip():
                    bitz[i] += '}'
                    del bitz[i + 1]
                    return i, bitz
                if '{' == bit.strip() and next.endswith('}'):
                    bitz[i] += next
                    del bitz[i + 1]
                    return i, bitz
                if i < num_bitz - 2:
                    far = bitz[i + 2]
                    if '{' == bit.strip() and '}' == far.strip():
                        if ('-' == next[0] or '+' == next[0]) and next[1:].isdigit():
                            bitz[i] += next
                            bitz[i] += far
                            del bitz[i + 2]
                            del bitz[i + 1]
                            return i, bitz
                        if next.isdigit():
                            bitz[i] += next
                            bitz[i] += far
                            del bitz[i + 2]
                            del bitz[i + 1]
                            return i, bitz

        return None, bitz

    @staticmethod
    def parse_starline_physicals_only(star, line):
        # This is to handle lines in sectors like Uuk, which have ... a speaking acquaintance ... with
        # well-formedness.  This specialist parser will probably break when the underlying data gets reviewed and fixed.
        # For instance:
        # Hex  Name                 UWP       Remarks              {Ix} (Ex) [Cx] N B Z PBG W A  Stellar
        # ---- -------------------- --------- -------------------- ---- ---- ---- - - - --- - -- -------
        # 0101                      ?321???-? Po                                  - - - ?22   Kk
        #
        bitz = []
        # We've tried classic line parsing and bulk fallback, which have failed.
        # Try the specialist route before giving up.
        matches = ParseStarInputFallback.first_three_line.match(line)
        if not matches:  # fallback has blown up, throw our hands up
            return None
        # For reasons unknown, these starlines don't bother with trivia like importance, economic or cultural extensions
        ix_residual = ParseStarInputFallback._unpack_first_line(bitz, matches)
        trade_matches = re.match(r'^([^-]{15,}) +(.*)', ix_residual)
        if not trade_matches:
            trade_matches = ['', ix_residual]
        else:
            trade_matches = trade_matches.groups()
        residual = trade_matches[1]

        bitz.append(trade_matches[0])
        # Add placeholders for unused spot 4, and missing Ix, Ex and Cs
        bitz.append(None)  # 4
        bitz.append(None)  # 5
        bitz.append(None)  # 6
        bitz.append(None)  # 7
        bitz.append(None)  # 8
        bitz.append(None)  # 9
        bitz.append(None)  # 10
        bitz.append('-')  # 11 - Nobles
        bitz.append(residual[2])  # 12 - Bases
        bitz.append(residual[4])  # 13 - Tradezone
        bitz.append(residual[6:9])  # 14 - PBG
        bitz.append('')  # 15 - Worlds
        bitz.append(residual[12:14])  # 16 - Allegiance
        if 13 < len(residual):
            stars = residual[14:].strip()  # 17 - Stars
            bitz.append(stars)
        else:
            bitz.append('')  # 17 - Stars

        return bitz
