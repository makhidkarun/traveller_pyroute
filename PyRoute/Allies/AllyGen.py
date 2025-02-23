"""
Created on Mar 26, 2014

@author: tjoneslo
"""
import functools
import typing

from typing_extensions import TypeAlias
from PyRoute.Outputs.Colour import Colour
from PyRoute.Position.Hex import HexPos

Alg: TypeAlias = typing.Optional[str]
AllyMap: TypeAlias = dict[HexPos, Alg]


class AllyGen(object):
    """
    classdocs
    """
    noOne = ['--', '----', '??', 'Xx']
    nonAligned = ['Na', 'Ns', 'Va', 'Cs', 'Hc', 'Kc',
                  'NaHu', 'NaHv', 'NaDr', 'NaVa', 'NaAs', 'NaXx', 'NaXX', "NaSo", "NaZh",
                  'VaEx',
                  'CsCa', 'CsHv', 'CsIm', 'CsMP', 'CsVa', 'CsZh', 'CsRe', 'CsMo', 'CsRr', "CsTw",
                  'Wild']
    sameAligned: list[tuple[Alg]] = [('Im', 'ImAp', 'ImDa', 'ImDc', 'ImDd', 'ImDg', 'ImDi', 'ImDs', 'ImDv',
                    'ImLa', 'ImLc', 'ImLu', 'ImSy', 'ImVd',
                    'I0', 'I1', 'I2', 'I3', 'I4', 'I5'),  # Testing values,
                   ('As', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8',
                    'A9', 'TE', 'Of', 'If',
                    'AsIf', 'AsMw', 'AsOf', 'AsSc', 'AsSF', 'AsT0', 'AsT1', 'AsT2',
                    'AsT3', 'AsT4', 'AsT5', 'AsT6', 'AsT7', 'AsT8', 'AsT9', 'AsTA',
                    'AsTv', 'AsTz', 'AsVc', 'AsWc', 'AsXX'),
                   ('Cr', 'CrRg'),
                   ('Kr', 'KrPr'),
                   ('Hv', 'HvFd', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H?', 'Hf'),
                   ('JP', 'J-', 'Jh', 'Hl', 'JuPr',
                    'JAOz', 'JAsi', 'JCoK', 'JHhk', 'JLum', 'JMen',
                    'JPSt', 'JRar', 'JUkh', 'JuHl', 'JuRu', 'JVug'),
                   ('Ke', 'KoEm'),
                   ("K1",),
                   ("K2",),
                   ("K3",),
                   ("K4",),
                   ("KC",),
                   ("Kk", "KkTw", "KO"),
                   ('So', 'SoCf', 'SoBF', 'SoCT', 'SoFr', 'SoHn', 'SoKv', 'SoNS',
                    'SoQu', 'SoRD', 'SoRz', 'SoWu'),
                   ('Lp', 'CoLp'),
                   ('Vd', 'VDeG'),
                   ('Vo', 'VOpA'),
                   ('Vx', 'VAsP'),
                   ('V9', 'VInL'),
                   ('Zh', 'ZhAx', 'ZhCa', 'ZhCh', 'ZhCo', 'ZhIa', 'ZhIN',
                    'ZhJp', 'ZhMe', 'ZhOb', 'ZhSh', 'ZhVQ')]

    default_population: dict[Alg, str] = {
        "As": "Asla",
        "Cr": "Huma",
        "Dr": "Droy",
        "Hv": "Hive",
        "JP": "Huma",
        "Kk": "KXkr",
        "Pd": "Piri",
        "Te": "Piri",
        "Tk": "Piri",
        "TY": "Drak",
        "Va": "Varg",
        "Vb": "Varg",
        "Vc": "Varg",
        "Wc": "Droy",
        "Yt": "Yask",
        "Zh": "Zhod",
        "AkUn": "Akee",
        "AlCo": "Muri",
        "CAEM": "Esly",
        "CAKT": "Varg",
        "CoLp": "Jend",
        "DaCf": "Dary",
        "FlLe": "Flor",
        "GeOr": "Ormi",
        "GlEm": "Asla",
        "GnCl": "Gnii",
        "IHPr": "Sred",
        "ImLu": "Luri",
        "ImVd": "Vega",
        "IsDo": "Ysla",
        "KaWo": "Karh",
        "KhLe": "Sydi",
        "KoEm": "Jaib",
        "KrPr": "Krot",
        "MaEm": "Mask",
        "MaPr": "MalX",
        "NaAs": "Asla",
        "NaDr": "Droy",
        "NaHv": "Hive",
        "NaVa": "Varg",
        "OcWs": "Stal",
        "SELK": "Lith",
        "SaCo": "Vlaz",
        "Sark": "Varg",
        "SwFW": "Swan",
        "VaEx": "Varg",
        "ZhAx": "Adda",
        "ZhCa": "Vlaz"
    }

    alleg_border_colors: dict[Alg, Colour] = {
        "Im": "red",
        "As": "yellow",
        "Cr": "gold",
        "Dr": None,
        "Hv": "violet",
        "JP": "blue",
        "Kr": "blue",
        "K1": "emerald",
        "K2": "emerald",
        "K3": "emerald",
        "K4": "darkolive",
        "KC": "emerald",
        "Kk": "green",
        "Rr": "blue",
        "So": "orange",
        "TY": "purple",
        "Va": "olive",
        "Vb": "olive",
        "Vc": "olive",
        "Wc": "lightblue",
        "Zh": "blue",
        "--": None,
        "Na": None,
        "----": None,
        "NaHu": None,
        "NaXX": None,
        "NaZh": None,
        "CsIm": None,
        "DaCf": "lightblue",
        "SwCf": "blue",
        "VAug": "olive",
        "VDzF": "olive",
        'I0': 'red', 'I1': 'red', 'I2': 'red', 'I3': 'red', 'I4': 'red',  # Testing Colors
        "NONE": "white",  # Default color
    }

    @staticmethod
    def is_unclaimed(alg: Alg) -> bool:
        return alg in AllyGen.noOne

    @staticmethod
    def is_nonaligned(alg: Alg, strict=False) -> bool:
        if strict:
            return alg in AllyGen.nonAligned
        return alg in AllyGen.nonAligned or alg in AllyGen.noOne

    @staticmethod
    def is_wilds(alg: Alg) -> bool:
        if alg is None:
            return False
        return alg[0:2] == 'Na' or alg in ['Wild', 'VaEx', 'Va']

    @staticmethod
    def is_client_state(alg: Alg) -> bool:
        if alg is None:
            return False
        return alg[0:2] == 'Cs'

    @staticmethod
    @functools.cache
    def same_align(alg: Alg) -> str:
        for sameAlg in AllyGen.sameAligned:
            if alg in sameAlg:
                return sameAlg[0]
        return alg

    @staticmethod
    def imperial_align(alg: Alg) -> bool:
        return AllyGen.same_align(alg) == 'Im'

    @staticmethod
    def same_align_name(alg: Alg, alg_name: typing.Optional[str]) -> str:
        if alg in AllyGen.nonAligned:
            return alg_name
        else:
            return alg_name.split(',')[0].strip()

    @staticmethod
    def population_align(alg: Alg, name: str) -> str:
        # Try getting the default cases
        code = AllyGen.default_population.get(alg, AllyGen.default_population.get(AllyGen.same_align(alg), None))

        # Handle the special cases.
        if code is None:
            if alg[0] == 'V':
                code = "Varg"
            elif alg == 'Na':
                if 'Hiver' in name:
                    code = 'Hive'
                elif 'Vargr' in name:
                    code = 'Varg'
                elif 'Zhodani' in name:
                    code = 'Zhod'
                elif 'Human' in name:
                    code = 'Huma'
                else:
                    code = 'Huma'
            elif alg == 'CsHv':
                code = "Hive"
            elif alg == "CsAs":
                code = "Asla"
            else:
                code = "Huma"
        return code

    @staticmethod
    def sort_allegiances(alg_list: dict, base_match_only: bool) -> list[Alg]:
        # The logic:
        # base_match_only == true -> --ally-match=collapse
        # only what matches the base allegiances
        # base_match_only == false -> --ally-match=separate
        # want the non-base code or the base codes for single code allegiances.

        if base_match_only:
            algs = [alg for alg in list(alg_list.values()) if alg.base]
        else:
            base_algs = [alg for alg in list(alg_list.values()) if alg.base]
            detail_algs = [alg for alg in list(alg_list.values()) if not alg.base]

            for alg in detail_algs:
                base_alg = alg_list[AllyGen.same_align(alg.code)]
                if base_algs and base_alg in base_algs:
                    base_algs = base_algs.remove(base_alg)

            algs = detail_algs
            algs += base_algs if base_algs else []
        algs.sort(key=lambda alg: alg.stats.number, reverse=True)
        return algs

    @staticmethod
    def are_owned_allies(alg1: Alg, alg2: Alg) -> bool:
        """
        Public function to determine if the Allegiances of two
        world are considered allied for the owned world checks.
        """
        if alg1 is None or alg2 is None:
            return False
        if alg1 in AllyGen.noOne or alg2 in AllyGen.noOne:
            return False
        if alg1 == alg2:
            return True
        for sameAlg in AllyGen.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        return False

    @staticmethod
    @functools.cache
    def are_allies(alg1: Alg, alg2: Alg) -> bool:
        """
        Public function to determine if the Allegiance of two
        worlds are considered allied for trade purposes or not.
        """
        if alg1 is None or alg2 is None:
            return False
        if alg1 in AllyGen.noOne or alg2 in AllyGen.noOne:
            return False
        if alg1 in AllyGen.nonAligned or alg2 in AllyGen.nonAligned:
            return False
        if alg1 == alg2:
            return True
        for sameAlg in AllyGen.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        return False
