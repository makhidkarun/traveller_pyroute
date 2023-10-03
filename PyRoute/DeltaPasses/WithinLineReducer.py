"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""


class WithinLineReducer(object):

    full_msg = None
    start_msg = None

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self):
        segment, subs_list = self._build_subs_list()
        self.reducer.logger.error(self.start_msg)

        msg = "start - # of unreduced lines: " + str(len(segment))
        self.reducer.logger.error(msg)

        best_sectors = self.reducer.sectors.switch_lines(subs_list)

        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, best_sectors)

        if interesting:
            self.reducer.sectors = best_sectors
            self.reducer.logger.error(self.full_msg)
            return
        else:
            best_sectors = self.reducer.sectors

        # trying everything didn't work, now we need to minimise the number of un-reduced lines
        num_chunks = 2
        short_msg = None
        singleton_run = True

        while num_chunks <= len(segment):
            chunks = self.reducer.chunk_lines(segment, num_chunks)
            remove = []
            msg = "# of unreduced lines: " + str(len(segment)) + ", # of chunks: " + str(num_chunks)
            self.reducer.logger.error(msg)
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
                    msg = "Reduction found: new input has " + str(len(raw_lines)) + " unreduced lines"
                    self.reducer.logger.error(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)

            num_chunks *= 2

            # rebuild segment from chunks
            segment = []
            for chunk in chunks:
                segment.extend(chunk)

            # if we've got here, reducing all lines hasn't worked.  If we're down to 1 element, we're done.
            if 1 == len(segment):
                break

            # if we're about to bust our loop condition, make sure we verify 1-minimality as our last hurrah
            if num_chunks > len(segment) and not singleton_run:
                singleton_run = True
                num_chunks = len(segment)

        self.reducer.sectors = best_sectors
        if short_msg is not None:
            self.reducer.logger.error("Shortest error message: " + short_msg)

    def _build_subs_list(self):
        raise NotImplementedError

    def _assemble_segment(self, unreduced_lines, subs_list):
        nu_list = []

        for line in subs_list:
            if line[0] in unreduced_lines:
                continue
            nu_list.append((line[0], line[1]))

        return nu_list
