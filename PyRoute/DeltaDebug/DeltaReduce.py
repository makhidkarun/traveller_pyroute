"""
Created on May 23, 2023

The core reduction engine used by delta debugging.
Modify this class to add different reduction passes.

@author: CyberiaResurrection
"""
import logging
import math

from DeltaPasses.SingleLineReducer import SingleLineReducer
from DeltaPasses.TwoLineReducer import TwoLineReducer
from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Outputs.HexMap import HexMap
from PyRoute.DeltaPasses.AuxiliaryLineReduce import AuxiliaryLineReduce
from PyRoute.DeltaPasses.Canonicalisation import Canonicalisation
from PyRoute.DeltaPasses.CapitalLineReduce import CapitalLineReduce
from PyRoute.DeltaPasses.FullLineReduce import FullLineReduce
from PyRoute.DeltaPasses.ImportanceLineReduce import ImportanceLineReduce
from PyRoute.DeltaPasses.SectorReducer import SectorReducer
from PyRoute.DeltaPasses.SubsectorReducer import SubsectorReducer
from PyRoute.SpeculativeTrade import SpeculativeTrade
from PyRoute.StatCalculation import StatCalculation
from PyRoute.Outputs.SubsectorMap2 import GraphicSubsectorMap


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
        self.logger = logging.getLogger('PyRoute.Star')
        logging.disable(logging.WARNING)
        self.withinline = [Canonicalisation(self), FullLineReduce(self), ImportanceLineReduce(self), CapitalLineReduce(self), AuxiliaryLineReduce(self)]
        self.sector_reducer = SectorReducer(self)
        self.subsector_reducer = SubsectorReducer(self)
        self.single_line_reducer = SingleLineReducer(self)
        self.two_line_reducer = TwoLineReducer(self)

    def is_initial_state_interesting(self):
        sectors = self.sectors
        args = self.args

        interesting, msg, _ = self._check_interesting(args, sectors)

        if not interesting:
            raise AssertionError("Original input not interesting - aborting")

    def is_initial_state_uninteresting(self, reraise=False):
        sectors = self.sectors
        args = self.args

        interesting, msg, e = self._check_interesting(args, sectors)

        if interesting:
            if reraise:
                raise e
            raise AssertionError(msg)

    def reduce_sector_pass(self, singleton_only=False):
        self.sector_reducer.run(singleton_only)

    def reduce_subsector_pass(self):
        self.subsector_reducer.run(False)

    def reduce_line_pass(self, singleton_only=False):
        self.single_line_reducer.run(singleton_only)

    def reduce_line_two_minimal(self):
        self.two_line_reducer.run(False)

    def reduce_within_line(self):
        # we're going to be deliberately mangling lines in the process of reducing them, so shut up loggers,
        # such as the TradeCodes logger, that will complain, to stop flooding stdout.
        logger = logging.getLogger('PyRoute.TradeCodes')
        logger.setLevel(logging.CRITICAL)

        for reducer in self.withinline:
            if reducer.preflight():
                reducer.run()

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
        q = None

        try:
            galaxy = DeltaGalaxy(args.btn, args.max_jump)
            galaxy.read_sectors(sectors, args.pop_code, args.ru_calc,
                                args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
            galaxy.output_path = args.output

            galaxy.generate_routes()

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
            q = e
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

        return interesting, msg, q

    @staticmethod
    def chunk_lines(lines, num_chunks):
        n = math.ceil(len(lines) / num_chunks)
        return [lines[i:i + n] for i in range(0, len(lines), n)]
