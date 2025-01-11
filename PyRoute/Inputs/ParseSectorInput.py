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
        isheader = True
        for line in lines:
            if not isinstance(line, str):
                continue

            if isheader:
                headers.append(line)
                if line.startswith('----'):
                    isheader = False
            else:
                if line.startswith('#') or len(line) < 20:
                    continue
                starlines.append(line)
        return headers, starlines
