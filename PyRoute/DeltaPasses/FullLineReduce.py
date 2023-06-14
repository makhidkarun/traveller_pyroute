"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaReduce import DeltaReduce
from PyRoute.DeltaPasses.WithinLineReducer import WithinLineReducer
from PyRoute.DeltaStar import DeltaStar


class FullLineReduce(WithinLineReducer):

    reducer: DeltaReduce

    def run(self):
        segment, subs_list = self._build_subs_list()

        best_sectors = self.reducer.sectors.switch_lines(subs_list)

        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, best_sectors)

        if interesting:
            self.reducer.sectors = best_sectors
            msg = "Reduction found with full star line reduction"
            self.reducer.logger.error(msg)
            return

        # trying everything didn't work, now we need to minimise the number of un-reduced lines
        num_chunks = 2

        while num_chunks <= len(segment):
            chunks = self.reducer.chunk_lines(segment, num_chunks)
            remove = []
            short_msg = None

            for i in range(0, num_chunks):
                threshold = i + (len(remove) if 2 == num_chunks else 0)
                if threshold >= len(chunks):
                    continue

                raw_lines = self.reducer._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                nu_list = self._assemble_segment(raw_lines, subs_list)

                temp_sectors = self.reducer.sectors.switch_lines(nu_list)

                interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)

                if interesting:
                    short_msg = self.reducer.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors

                if 0 < len(remove):
                    num_chunks -= len(remove)

                num_chunks *= 2

            # rebuild segment from chunks
            segment = []
            for chunk in chunks:
                segment.extend(chunk)

        self.reducer.sectors = best_sectors

    def _build_subs_list(self):
        # build substitution list - reduce _everything_
        subs_list = []
        segment = []
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce_all(line.strip())
            assert isinstance(canon,
                              str), "Candidate line " + line + " was not reduced to a string.  Got " + canon + " instead."
            subs_list.append((line, canon))
            segment.append(line)
        return segment, subs_list
