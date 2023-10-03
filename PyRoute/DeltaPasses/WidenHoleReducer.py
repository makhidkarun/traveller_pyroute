"""
Created on Oct 04, 2023

@author: CyberiaResurrection
"""


class WidenHoleReducer(object):

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self, start_pos, reverse=False):
        found_reduction = True
        chunk_size = 1

        best_sectors = self.reducer.sectors

        msg = "# of lines: " + str(len(best_sectors.lines))
        self.reducer.logger.error(msg)

        while found_reduction:
            segment = best_sectors.lines
            if reverse:
                raw_start_pos = start_pos + 1 if 0 < start_pos else 0
                raw_fin_pos = raw_start_pos - chunk_size
                lines_to_drop = segment[min(raw_start_pos, raw_fin_pos):max(raw_start_pos, raw_fin_pos)]
            else:
                lines_to_drop = segment[start_pos:start_pos + chunk_size]

            if 1 < chunk_size and 0 == len(lines_to_drop):
                found_reduction = False
                continue

            temp_sectors = best_sectors.drop_lines(lines_to_drop)

            interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)

            if not interesting:
                found_reduction = False
                continue
            best_sectors = temp_sectors
            chunk_size *= 2

            msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines"
            self.reducer.logger.error(msg)

        self.reducer.sectors = best_sectors
