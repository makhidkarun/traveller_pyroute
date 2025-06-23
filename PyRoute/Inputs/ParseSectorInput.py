"""
Created on 12 Jan, 2025

@author: CyberiaResurrection
"""
import codecs
import logging
import os
from logging import Logger
from typing import Union

from PyRoute.Allies.AllyGen import AllyGen
from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Sector import Sector
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, SubsectorDictionary
from PyRoute.Star import Star


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
    def read_sector_file(filename: str, logger: Logger) -> tuple[list[str], list[str]]:
        headers = []
        lines = []

        # read travellermap file in, line by line
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as infile:
                try:
                    lines = [line for line in infile]
                    headers, lines = ParseSectorInput.partition_lines(lines)
                except (OSError, IOError):
                    logger.error("sector file %s can not be read", filename, exc_info=True)
        except FileNotFoundError:
            logger.error("sector file %s not found" % filename)

        return headers, lines

    @staticmethod
    def parse_allegiance(headers: list[str], alg_object) -> None:
        allegiances = [line for line in headers if line.startswith('# Alleg:')]

        for line in allegiances:
            ParseSectorInput._parse_allegiance_core(line, alg_object)

    @staticmethod
    def _parse_allegiance_core(line: str, alg_object: dict[str, Allegiance]) -> None:
        alg_code = line[8:].split(':', 1)[0].strip()
        alg_name = line[8:].split(':', 1)[1].strip().strip('"')

        # A work around for the base Na codes which may be empire dependent.
        alg_race = AllyGen.population_align(alg_code, alg_name)

        base = AllyGen.same_align(alg_code)
        if base is not None and base not in alg_object:
            alg_object[base] = Allegiance(base, AllyGen.same_align_name(base, alg_name), base=True,
                                          population=alg_race)
        if alg_code not in alg_object:
            alg_object[alg_code] = Allegiance(alg_code, alg_name, base=False, population=alg_race)

    @staticmethod
    def parse_subsectors(headers: list[str], name: str, sector: Union[Sector, SectorDictionary]) -> dict[str, str]:
        if not (isinstance(sector, (Sector, SectorDictionary))):
            raise ValueError("Supplied sector must be instance of Sector or SectorDictionary")
        is_dict = isinstance(sector, SectorDictionary)

        sublines = [line for line in headers if line.startswith('# Subsector ')]
        subsector_names = dict()
        for line in sublines:
            data = line[11:].split(':', 1)
            pos = data[0].strip()
            subname = data[1].strip()
            if '' == subname:
                subname = name.strip() + ' ' + pos
            subsector_names[pos] = subname
            if is_dict:
                sector[subname] = SubsectorDictionary(subname, pos)
            else:
                sector.subsectors[pos] = Subsector(subname, pos, sector)  # type: ignore
        return subsector_names

    @staticmethod
    def read_parsed_sector_to_sector_dict(basename, headers, starlines):
        nameline = headers[3]  # assuming the definitive name line is the 4th line in what got read in
        name = nameline.strip('#')
        position = headers[4]

        sector = SectorDictionary(name.strip(), basename)
        sector.headers = headers
        sector.position = position.strip()

        # dig out allegiances
        ParseSectorInput.parse_allegiance(headers, sector.allegiances)

        # dig out subsector names, and use them to seed the dict entries
        subsector_names = ParseSectorInput.parse_subsectors(headers, name, sector)

        # now subsectors are seeded, run thru the elements of starlines and deal them out to their respective subsector
        # dicts
        dummy = Sector('# dummy', '# 0,0')
        logging.disable(logging.WARNING)

        for line in starlines:
            # Re-use the existing, battle-tested, validation logic rather than scraping something new and buggy together
            star = Star.parse_line_into_star(line, dummy, 'scaled', 'scaled')
            if not star:
                continue
            subsec = star.subsector()
            subname = subsector_names[subsec]
            sector[subname].items.append(line.strip('\n'))

        return sector

    @staticmethod
    def read_parsed_sector_to_sector_object(fix_pop, headers, loaded_sectors, logger, pop_code, ru_calc, sector,
                                            star_counter, starlines, galaxy):
        logger.debug('reading %s ' % sector)

        sec = Sector(headers[3], headers[4])
        sec.filename = os.path.basename(sector)
        if str(sec) not in loaded_sectors:
            loaded_sectors.add(str(sec))
        else:
            logger.error("sector file %s loads duplicate sector %s" % (sector, str(sec)))
            return None, None

        # dig out allegiances
        ParseSectorInput.parse_allegiance(headers, galaxy.alg)

        # dig out subsector names, and use them to seed the dict entries
        ParseSectorInput.parse_subsectors(headers, sec.name, sec)

        for line in starlines:
            star = Star.parse_line_into_star(line, sec, pop_code, ru_calc, fix_pop=fix_pop)
            if star:
                star_counter = galaxy.add_star_to_galaxy(star, star_counter, sec)

        return sec, star_counter
