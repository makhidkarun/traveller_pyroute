"""
Created on Oct 03, 2023

@author: CyberiaResurrection
"""


class TwoLineReducer(object):

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self, singleton_only=False):
        segment = self.reducer.sectors.lines

        # An interesting less-than-4-element list is 2-minimal by definition
        if 4 > len(segment):
            return

        best_sectors = self.reducer.sectors
        gap = 1
        while gap < len(segment):
            msg = "# of lines: " + str(len(best_sectors.lines))
            self.reducer.logger.error(msg)

            i = 0
            j = i + gap
            while j < len(segment):
                lines_to_remove = [segment[i], segment[j]]
                temp_sectors = best_sectors.drop_lines(lines_to_remove)

                interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)

                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    best_sectors = temp_sectors
                    segment = best_sectors.lines
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines"
                    self.reducer.logger.error(msg)
                else:
                    i += 1
                j = i + gap

            gap += 1

        # now that the pass is done, update self.sectors with best reduction found
        self.reducer.sectors = best_sectors
