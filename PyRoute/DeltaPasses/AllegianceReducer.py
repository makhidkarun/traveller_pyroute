"""
Created on Oct 07, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary


class AllegianceReducer(object):

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self, singleton_only=False):
        segment = list(self.reducer.sectors.allegiance_list())

        # An interesting single-element list is 1-minimal by definition
        if 2 > len(segment):
            return

        num_chunks = len(segment) if singleton_only else 2
        short_msg = None
        best_sectors = self.reducer.sectors
        singleton_run = singleton_only
        old_length = len(segment)

        while num_chunks <= len(segment):
            chunks = self.reducer.chunk_lines(segment, num_chunks)
            num_chunks = len(chunks)
            remove = []
            msg = "# of lines: " + str(len(best_sectors.lines)) + ", # of chunks: " + str(num_chunks) + ", # of allegiances: " + str(len(segment))
            self.reducer.logger.error(msg)
            for i in range(0, num_chunks):
                if i + len(remove) >= len(chunks):
                    continue
                msg = "Allegiance reduction: Attempting chunk " + str(i + 1) + "/" + str(num_chunks)
                self.reducer.logger.error(msg)
                raw_lines = self.reducer._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                temp_sectors = best_sectors.allegiance_subset(raw_lines)
                temp_lines = len(temp_sectors.lines)
                if 0 == temp_lines:
                    # nothing to do, move on
                    continue

                interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)
                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    short_msg = self.reducer.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines and " + str(
                        len(raw_lines)) + " allegiances"
                    self.reducer.logger.error(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)
                best_sectors.trim_empty_allegiances()
                self.write_files(best_sectors)

            num_chunks *= 2
            # if we're about to bust our loop condition, make sure we verify 1-minimality as our last hurrah
            if num_chunks > len(segment) and not singleton_run:
                singleton_run = True
                num_chunks = len(segment)
            segment = list(best_sectors.allegiance_list())

        # now that the pass is done, update self.sectors with best reduction found
        self.reducer.sectors = best_sectors
        if short_msg is not None:
            self.reducer.logger.error("Shortest error message: " + short_msg)

        # At least one allegiance was shown to be irrelevant, write out the intermediate result
        if old_length > len(segment):
            self.reducer.sectors.trim_empty_allegiances()
            self.write_files()

    def write_files(self, sectors=None):
        if isinstance(sectors, DeltaDictionary):
            sectors.write_files(self.reducer.args.mindir)
        else:
            self.reducer.sectors.write_files(self.reducer.args.mindir)
