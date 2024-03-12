"""
Created on Oct 03, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaPasses.WidenHoleReducer import WidenHoleReducer


class SubsectorReducer(object):

    def __init__(self, reducer):
        self.reducer = reducer
        self.breacher = WidenHoleReducer(reducer)

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self, singleton_only=False):
        segment = self.reducer.sectors.subsector_list()

        # An interesting single-element list is 1-minimal by definition
        if 2 > len(segment):
            return

        num_chunks = len(segment) if singleton_only else 2
        short_msg = None
        best_sectors = self.reducer.sectors

        while num_chunks <= len(segment):
            chunks = self.reducer.chunk_lines(segment, num_chunks)
            remove = []
            msg = "# of lines: " + str(len(best_sectors.lines)) + ", # of chunks: " + str(
                num_chunks) + ", # of subsectors: " + str(len(segment))
            self.reducer.logger.error(msg)
            start_counter = 0
            bounds = []
            for chunk in chunks:
                final_counter = start_counter + len(chunk) - 1
                bounds.append((start_counter, final_counter))
                start_counter = final_counter + 1

            for i in range(0, num_chunks):
                if i + len(remove) >= len(chunks):
                    continue
                msg = "Subsector reduction: Attempting chunk " + str(i + 1) + "/" + str(num_chunks)
                self.reducer.logger.error(msg)
                raw_lines = self.reducer._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                temp_sectors = best_sectors.subsector_subset(raw_lines)

                interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)
                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    short_msg = self.reducer.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines and " + str(
                        len(raw_lines)) + " subsectors"
                    self.reducer.logger.error(msg)

                    if 0 < i:  # if have cleared a later chunk, it's worth trying to expand the hole backwards
                        msg = "Widening breach backwards"
                        self.reducer.logger.error(msg)
                        startloc = bounds[i - 1][1]
                        best_sectors = self.breacher.run(
                            start_pos=startloc,
                            reverse=True,
                            best_sectors=best_sectors
                        )

                    if i < num_chunks - 1:  # now try expanding hole forwards
                        msg = "Widening breach forwards"
                        self.reducer.logger.error(msg)
                        startloc = bounds[i - 1][1]
                        best_sectors = self.breacher.run(
                            start_pos=startloc,
                            reverse=False,
                            best_sectors=best_sectors
                        )

                    msg = "Widening breach complete"
                    self.reducer.logger.error(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)

            num_chunks *= 2
            segment = best_sectors.subsector_list()

        # now that the pass is done, update self.sectors with best reduction found
        self.reducer.sectors = best_sectors
        if short_msg is not None:
            self.reducer.logger.error("Shortest error message: " + short_msg)
