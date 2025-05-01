"""
Created on Oct 03, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaPasses.BeyondLineReducer import BeyondLineReducer


class TwoLineReducer(BeyondLineReducer):

    def run(self, singleton_only=False, first_segment=True):
        segment = self.reducer.sectors.lines

        # An interesting less-than-4-element list is 2-minimal by definition
        if 4 > len(segment):
            return

        best_sectors = self.reducer.sectors
        old_length = len(segment)
        sqrt = max(2, round(old_length ** 0.5))
        gap = 1 if first_segment else sqrt
        maxgap = sqrt + 1 if first_segment else len(segment)

        while gap < min(maxgap, len(segment)):
            msg = "# of lines: " + str(len(best_sectors.lines)) + f", gap {gap}"
            self.reducer.logger.error(msg)
            interim_write = max(10, int((len(segment) - gap) ** 0.5))
            interim_counter = 0

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
                    interim_counter += 1
                    if interim_write == interim_counter:
                        interim_counter = 0
                        best_sectors.trim_empty_allegiances()
                        self.write_files(best_sectors)
                else:
                    i += 1
                j = i + gap

            if old_length > len(segment):
                best_sectors.trim_empty_allegiances()
                self.write_files(best_sectors)
                old_length = len(segment)

            gap += 1

        # now that the pass is done, update self.sectors with best reduction found
        self.reducer.sectors = best_sectors

        # At least one sector was shown to be irrelevant, write out the intermediate result
        if old_length > len(segment):
            self.reducer.sectors.trim_empty_allegiances()
            self.write_files()
