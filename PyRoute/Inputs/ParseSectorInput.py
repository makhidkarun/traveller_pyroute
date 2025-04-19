"""
Created on 12 Jan, 2025

@author: CyberiaResurrection
"""
import codecs
from logging import Logger

from PyRoute.Allies.AllyGen import AllyGen
from PyRoute.AreaItems.Allegiance import Allegiance


class ParseSectorInput:

    @staticmethod
    def partition_lines(lines: list[str]):
        """
            Break lines out into headers section, which is retained, and starlines, which gets either retained, or
            minimised later on - this assumes downloaded-from-TravellerMap sector file
        """
        assert isinstance(lines, list)

        headers = []
        starlines = []
        for line in lines:
            if not isinstance(line, str):
                continue

            if line[0].isdigit():
                starlines.append(line)
            else:
                headers.append(line)
            continue

        return headers, starlines

    @staticmethod
    def read_sector_file(filename: str, logger: Logger) -> list[str]:
        lines = []

        # read travellermap file in, line by line
        try:
            with codecs.open(filename, 'r', 'utf-8') as infile:
                try:
                    lines = [line for line in infile]
                except (OSError, IOError):
                    logger.error("sector file %s can not be read", filename, exc_info=True)
        except FileNotFoundError:
            logger.error("sector file %s not found" % filename)

        return lines

    @staticmethod
    def _parse_allegiance_core(line: str, alg_object: dict[str, Allegiance]) -> None:
        alg_code = line[8:].split(':', 1)[0].strip()
        alg_name = line[8:].split(':', 1)[1].strip().strip('"')

        # A work around for the base Na codes which may be empire dependent.
        alg_race = AllyGen.population_align(alg_code, alg_name)

        base = AllyGen.same_align(alg_code)
        if base not in alg_object:
            alg_object[base] = Allegiance(base, AllyGen.same_align_name(base, alg_name), base=True,
                                          population=alg_race)
        if alg_code not in alg_object:
            alg_object[alg_code] = Allegiance(alg_code, alg_name, base=False, population=alg_race)
