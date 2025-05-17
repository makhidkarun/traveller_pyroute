"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaLogicError import DeltaLogicError
from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary
from PyRoute.DeltaStar import DeltaStar


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
        if 0 == len(subs_list):
            # nothing to do, bail out early
            return

        self.reducer.logger.error(self.start_msg)
        self.reducer.is_initial_state_interesting()

        msg = "start - # of unreduced lines: " + str(len(segment))
        self.reducer.logger.error(msg)

        best_sectors = self.reducer.sectors.switch_lines(subs_list)

        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, best_sectors)

        if interesting:
            self.reducer.sectors = best_sectors
            self.reducer.logger.error(self.full_msg)
            self.reducer.sectors.trim_empty_allegiances()
            self.write_files()
            return
        # By the time we've gotten here, if segment is 1 element long, switching it in _can't_ be interesting,
        # otherwise it would have tripped the original if statement, so bail out early
        elif 1 == len(segment):
            return
        else:
            best_sectors = self.reducer.sectors

        # trying everything didn't work, now we need to minimise the number of un-reduced lines
        num_chunks = 2
        short_msg = None
        singleton_run = False

        while num_chunks <= len(segment):
            chunks = self.reducer.chunk_lines(segment, num_chunks)
            num_chunks = len(chunks)
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
                    step = '(' + str(i + 1) + "/" + str(num_chunks) + ')'
                    msg = "Reduction found " + step + ": new input has " + str(len(raw_lines)) + " unreduced lines"
                    self.reducer.logger.error(msg)
                del temp_sectors

            if 0 < len(remove):
                num_chunks -= len(remove)
                new_hex = 'Hex  Name                 UWP       Remarks                               {Ix}   (Ex)    [Cx]   N    B  Z PBG W  A    Stellar         Routes                                   \n'
                new_dash = '---- -------------------- --------- ------------------------------------- ------ ------- ------ ---- -- - --- -- ---- --------------- -----------------------------------------\n'
                for sec_name in best_sectors:
                    num_headers = len(best_sectors[sec_name].headers)
                    for i in range(0, num_headers):
                        raw_line = best_sectors[sec_name].headers[i]
                        if raw_line.startswith('Hex  '):
                            best_sectors[sec_name].headers[i] = new_hex
                        elif raw_line.startswith('---- --'):
                            best_sectors[sec_name].headers[i] = new_dash
                best_sectors.trim_empty_allegiances()
                self.write_files(best_sectors)

            num_chunks *= 2

            # rebuild segment from chunks
            segment = []
            for chunk in chunks:
                segment.extend(chunk)

            # if we've got here, reducing all lines hasn't worked.  If we're down to 1 element, we're done.
            if 1 == len(segment):
                break

            # if we're about to bust our loop condition, make sure we verify 1-minimality as our last hurrah
            if num_chunks >= len(segment) and not singleton_run:
                singleton_run = True
                num_chunks = len(segment)

        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, best_sectors)
        if not interesting:
            raise DeltaLogicError("Intermediate output not interesting")

        self.reducer.sectors = best_sectors

        self.reducer.sectors.trim_empty_allegiances()
        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, self.reducer.sectors)
        if not interesting:
            raise DeltaLogicError("Final output not interesting")

        self.reducer.sectors.trim_empty_allegiances()
        self.write_files()
        if short_msg is not None:
            self.reducer.logger.error("Shortest error message: " + short_msg)

    def _build_subs_list(self):
        raise NotImplementedError

    def _build_fill_list(self):
        subs_list = []
        segment = []
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce(line)
            if line.startswith(canon):
                continue

            subs_list.append((line, canon))
            segment.append(line)

        return segment, subs_list

    def _assemble_segment(self, unreduced_lines, subs_list):
        nu_list = []

        for line in subs_list:
            if line[0] in unreduced_lines:
                continue
            nu_list.append((line[0], line[1]))

        return nu_list

    def write_files(self, sectors=None):
        if isinstance(sectors, DeltaDictionary):
            sectors.write_files(self.reducer.args.mindir)
        else:
            self.reducer.sectors.write_files(self.reducer.args.mindir)
