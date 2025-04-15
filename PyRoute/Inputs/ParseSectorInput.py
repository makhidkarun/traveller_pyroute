"""
Created on 12 Jan, 2025

@author: CyberiaResurrection
"""
import codecs
from logging import Logger


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
