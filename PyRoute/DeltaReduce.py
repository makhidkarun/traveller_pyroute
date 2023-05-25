"""
Created on May 23, 2023

The core reduction engine used by delta debugging.
Modify this class to add different reduction passes.

@author: CyberiaResurrection
"""
import functools
import logging
import math

from PyRoute.DeltaDictionary import DeltaDictionary
from PyRoute.DeltaGalaxy import DeltaGalaxy
from PyRoute.HexMap import HexMap
from PyRoute.SpeculativeTrade import SpeculativeTrade
from PyRoute.StatCalculation import StatCalculation
from PyRoute.SubsectorMap2 import GraphicSubsectorMap


class DeltaReduce:

    def __init__(self, sectors, args, interesting_line=None, interesting_type=None):
        assert isinstance(sectors, DeltaDictionary), "Sectors object must be an instance of DeltaDictionary"
        self.sectors = sectors
        self.args = args
        # Interesting_line allows the caller to tighten the definition of interesting by requiring a specific
        # string to appear in the exception message
        # Interesting_type requires an exception type to contain a specific string
        # If both are defined, they both have to match for the result to be interesting
        self.interesting_line = interesting_line
        self.interesting_type = interesting_type
        self.logger = logging.getLogger('PyRoute.DeltaReduce')

    def is_initial_state_interesting(self):
        sectors = self.sectors
        args = self.args

        interesting, _ = self._check_interesting(args, sectors)

        if not interesting:
            raise AssertionError("Original input not interesting - aborting")

    def reduce_sector_pass(self, singleton_only=False):
        segment = self.sectors.sector_list()

        # An interesting single-element list is 1-minimal by definition
        if 2 > len(segment):
            return

        num_chunks = len(segment) if singleton_only else 2
        short_msg = None
        best_sectors = self.sectors
        singleton_run = singleton_only

        while num_chunks <= len(segment):
            chunks = self.chunk_lines(segment, num_chunks)
            remove = []
            msg = "# of lines: " + str(len(best_sectors.lines)) + ", # of chunks: " + str(num_chunks)
            self.logger.info(msg)

            for i in range(0, num_chunks):
                threshold = i + (len(remove) if 2 == num_chunks else 0)
                if threshold >= len(chunks):
                    continue
                raw_lines = self._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                temp_sectors = best_sectors.sector_subset(raw_lines)

                interesting, msg = self._check_interesting(self.args, temp_sectors)
                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    short_msg = self.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines"
                    self.logger.info(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)

            num_chunks *= 2
            # if we're about to bust our loop condition, make sure we verify 1-minimality as our last hurrah
            if num_chunks > len(segment) and not singleton_run:
                singleton_run = True
                num_chunks = len(segment)

            segment = best_sectors.sector_list()

        # now that the pass is done, update self.sectors with best reduction found
        self.sectors = best_sectors

    def reduce_subsector_pass(self):
        segment = self.sectors.subsector_list()

        # An interesting single-element list is 1-minimal by definition
        if 2 > len(segment):
            return

        num_chunks = 2
        short_msg = None
        best_sectors = self.sectors

        while num_chunks <= len(segment):
            chunks = self.chunk_lines(segment, num_chunks)
            remove = []
            msg = "# of lines: " + str(len(best_sectors.lines)) + ", # of chunks: " + str(num_chunks)
            self.logger.info(msg)
            for i in range(0, num_chunks):
                if i + len(remove) >= len(chunks):
                    continue
                raw_lines = self._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                temp_sectors = best_sectors.subsector_subset(raw_lines)

                interesting, msg = self._check_interesting(self.args, temp_sectors)
                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    short_msg = self.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines"
                    self.logger.info(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)

            num_chunks *= 2
            segment = best_sectors.subsector_list()

        # now that the pass is done, update self.sectors with best reduction found
        self.sectors = best_sectors

    def reduce_line_pass(self, singleton_only=False):
        segment = self.sectors.lines

        # An interesting single-element list is 1-minimal by definition
        if 2 > len(segment):
            return

        num_chunks = len(segment) if singleton_only else 2
        short_msg = None
        best_sectors = self.sectors
        singleton_run = singleton_only

        while num_chunks <= len(segment):
            chunks = self.chunk_lines(segment, num_chunks)
            remove = []
            msg = "# of lines: " + str(len(best_sectors.lines)) + ", # of chunks: " + str(num_chunks)
            self.logger.info(msg)

            for i in range(0, num_chunks):
                threshold = i + (len(remove) if 2 == num_chunks else 0)
                if threshold >= len(chunks):
                    continue
                raw_lines = self._assemble_all_but_ith_chunk(chunks, i)
                if 0 == len(raw_lines):
                    # nothing to do, move on
                    continue

                temp_sectors = best_sectors.drop_lines(chunks[i])

                interesting, msg = self._check_interesting(self.args, temp_sectors)
                # We've found a chunk of input and have _demonstrated_ its irrelevance,
                # empty that chunk, update best so far, and continue
                if interesting:
                    short_msg = self.update_short_msg(msg, short_msg)
                    chunks[i] = []
                    remove.append(i)
                    best_sectors = temp_sectors
                    msg = "Reduction found: new input has " + str(len(best_sectors.lines)) + " lines"
                    self.logger.info(msg)

            if 0 < len(remove):
                num_chunks -= len(remove)

            num_chunks *= 2
            # if we're about to bust our loop condition, make sure we verify 1-minimality as our last hurrah
            if num_chunks > len(segment) and not singleton_run:
                singleton_run = True
                num_chunks = len(segment)

            segment = best_sectors.lines

        # now that the pass is done, update self.sectors with best reduction found
        self.sectors = best_sectors

    def _assemble_all_but_ith_chunk(self, chunks, i):
        # Assemble all _but_ the ith chunk
        nulines = [item for ind, item in enumerate(chunks) if ind != i and ind < len(chunks)]
        # pythonically flatten nulines (list of lists) into single list
        raw_lines = [item for sublist in nulines for item in sublist]
        return raw_lines

    @staticmethod
    def update_short_msg(msg, short_msg):
        if msg is not None:
            if short_msg is None:
                short_msg = msg
            elif len(msg) < len(short_msg):
                short_msg = msg
        return short_msg

    @staticmethod
    def _check_interesting(args, sectors):
        interesting = False
        msg = None

        try:
            galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
            galaxy.read_sectors(sectors, args.pop_code, args.ru_calc)
            galaxy.output_path = args.output

            galaxy.generate_routes(args.routes, args.route_reuse)

            galaxy.set_borders(args.borders, args.ally_match)

            if args.owned:
                galaxy.process_owned_worlds()

            if args.trade:
                galaxy.trade.calculate_routes()
                galaxy.process_eti()
                spectrade = SpeculativeTrade(args.speculative_version, galaxy.stars)
                spectrade.process_tradegoods()

            if args.routes:
                galaxy.write_routes(args.routes)

            stats = StatCalculation(galaxy)
            stats.calculate_statistics(args.ally_match)
            stats.write_statistics(args.ally_count, args.ally_match, args.json_data)

            if args.maps:
                pdfmap = HexMap(galaxy, args.routes, args.route_btn)
                pdfmap.write_maps()

                if args.subsectors:
                    graphMap = GraphicSubsectorMap(galaxy, args.routes, args.speculative_version)
                    graphMap.write_maps()
        except Exception as e:
            # check e's message and/or stack trace for interestingness line
            msg = str(e)
            interesting = True
            if args.interestingline:
                if msg.__contains__(args.interestingline):
                    interesting = True
                else:
                    interesting = False
            if args.interestingtype and interesting:
                strtype = str(type(e))
                if strtype.__contains__(args.interestingtype):
                    interesting = True
                else:
                    interesting = False

        return interesting, msg

    @staticmethod
    def chunk_lines(lines, num_chunks):
        n = math.ceil(len(lines) / num_chunks)
        return [lines[i:i + n] for i in range(0, len(lines), n)]
