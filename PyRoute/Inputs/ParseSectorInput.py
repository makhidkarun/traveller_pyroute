"""
Created on 12 Jan, 2025

@author: CyberiaResurrection
"""


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
