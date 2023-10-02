"""
Created on May 27, 2023

@author: CyberiaResurrection

A dirt-simple wrapper to enable error-causing inputs to be minimised
by the delta-debugging approach.

In brief, delta debugging notes that a given input triggering some
sort of program misbehaviour contains a (usually relatively) small
amount of input relevant to the failure, and a much larger amount
of irrelevant input.  Delta-debugging aims to produce a reasonable
approximation of _just_ the relevant input, while removing the bulk
of the irrelevant input, chunk by chunk.

For the moment, it requires the user to specify a line that must
appear in the run output for that run to count as "interesting".
"""

import argparse
import logging
import codecs
import os

from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary
from PyRoute.DeltaDebug.DeltaReduce import DeltaReduce
from PyRoute.Galaxy import Galaxy



logger = logging.getLogger('PyRoute')


def process():
    parser = argparse.ArgumentParser(description='PyRoute input minimiser.')
    logger.setLevel(logging.ERROR)

    alleg = parser.add_argument_group('Allegiance', 'Alter processing of allegiances')
    alleg.add_argument('--borders', choices=['none', 'range', 'allygen', 'erode'], default='range',
                       help='Allegiance border generation, default [range]')
    alleg.add_argument('--ally-match', choices=['collapse', 'separate'], default='collapse',
                       help='Allegiance matching for borders, default [collapse]')

    route = parser.add_argument_group('Routes', 'Route generation options')
    route.add_argument('--routes', dest='routes', choices=['trade', 'comm', 'xroute', 'owned', 'none'], default='trade',
                       help='Route type to be generated, default [trade]')
    route.add_argument('--min-btn', dest='btn', default=13, type=int,
                       help='Minimum BTN used for route calculation, default [13]')
    route.add_argument('--min-route-btn', dest='route_btn', default=8, type=int,
                       help='Minimum btn for drawing on the map, default [8]')
    route.add_argument('--max-jump', dest='max_jump', default=4, type=int,
                       help='Maximum jump distance for trade routes, default [4]')
    route.add_argument('--pop-code', choices=['fixed', 'scaled', 'benford'], default='scaled',
                       help='Interpretation of the population modifier code, default [scaled]')
    route.add_argument('--route-reuse', default=10, type=int,
                       help='Scale for reusing routes during route generation')
    route.add_argument('--ru-calc', default='scaled', choices=['scaled', 'negative'],
                       help='RU calculation, default [scaled]')
    route.add_argument('--speculative-version', choices=['CT', 'T5', 'None'], default='CT',
                       help='version of the speculative trade calculations, default [CT]')
    route.add_argument('--mp-threads', default=os.cpu_count()-1, type=int,
                       help=f"Number of processes to use for trade-mp processing, default {os.cpu_count()-1}")

    output = parser.add_argument_group('Output', 'Output options')

    output.add_argument('--output', default='maps', help='output directory for maps, statistics')
    output.add_argument('--owned-worlds', dest='owned', default=False, action='store_true',
                        help='Generate the owned worlds report, used for review purposes')
    output.add_argument('--no-trade', dest='trade', default=True, action='store_false',
                        help='Do not generate any trade data, only the default statistical data')
    output.add_argument('--no-maps', dest='maps', default=True, action='store_false',
                        help='Do not generate sector level trade maps')
    output.add_argument('--no-subsector-maps', dest='subsectors', default=True, action='store_false',
                        help='Do not generate subsector level maps')
    output.add_argument('--min-ally-count', dest='ally_count', default=10, type=int,
                        help='Minimum number of worlds in an allegiance for output, default [10]')
    output.add_argument('--json-data', dest='json_data', default=False, action='store_true',
                        help='Dump internal data structures as json for later further processing ')

    debugging = parser.add_argument_group('Debug', "Debugging flags")
    debugging.add_argument('--debug', dest="debug_flag", default=False, action='store_true',
                           help="Turn on trade-route debugging")

    delta = parser.add_argument_group('Debugging', 'Parameters for the delta-debugging procedure itself')
    delta.add_argument('--input', default='sectors', help='input directory for sectors')
    delta.add_argument('--sectors', default=None, help='file with list of sector names to process')
    delta.add_argument('sector', nargs='*', help='T5SS sector file(s) to process')
    delta.add_argument('--output-dir', dest="outputdir",
                       help='Output folder to place any maps generated during minimisation.')
    delta.add_argument('--min-dir', dest="mindir",
                       help='Output folder to place minimised sector files generated during minimisation.')
    delta.add_argument('--interesting-line', dest="interestingline", default=None,
                       help="Line required to classify run output as interesting")
    delta.add_argument('--interesting-type', dest="interestingtype", default=None,
                       help="Exception type required to classify run output as interesting")
    delta.add_argument('--two-minimise', dest="two_min", default=False, action='store_true',
                       help="Try all pairs of star lines to see if any can be removed")
    delta.add_argument('--no-sector', dest="run_sector", default=True, action='store_false',
                       help="Skip sector-level reduction")
    delta.add_argument('--no-subsector', dest="run_subsector", default=True, action='store_false',
                       help="Skip subsector-level reduction")
    delta.add_argument('--no-line', dest="run_line", default=True, action='store_false',
                       help="Skip line-level reduction.  At least one of sector, subsector, line and two-minimisation must be selected")
    delta.add_argument('--within-line', dest="run_within", default=False, action='store_true',
                       help="Try to remove irrelevant components (eg base codes) from _within_ individual lines")
    delta.add_argument('--assume-interesting', dest="run_init", default=True, action='store_false',
                       help="Assume initial input is interesting.")

    args = parser.parse_args()

    # sanity check run arguments
    if not (args.two_min or args.run_sector or args.run_subsector or args.run_line):
        raise ValueError("Must select at least one reduction pass to run")

    galaxy = Galaxy(args.btn, args.max_jump)
    galaxy.output_path = args.output

    sectors_list = args.sector
    if args.sectors is not None:
        sectors_list.extend(get_sectors(args.sectors, args.input))

    delta = DeltaDictionary()
    for sector_file in sectors_list:
        sector = SectorDictionary.load_traveller_map_file(sector_file)
        delta[sector.name] = sector

    logger.error("%s sectors read" % len(delta))

    # spin up reducer
    reducer = DeltaReduce(delta, args, args.interestingline, args.interestingtype)

    # check original input is interesting
    if args.run_init:
        reducer.is_initial_state_interesting()

    # do the reduction passes
    if args.run_sector:
        logger.error("Reducing by sector")
        reducer.reduce_sector_pass()
        reducer.is_initial_state_interesting()

    if args.run_subsector:
        logger.error("Reducing by subsector")
        reducer.reduce_subsector_pass()
        reducer.is_initial_state_interesting()

    if args.run_line:
        reducer.is_initial_state_interesting()
        logger.error("Reducing by line")
        reducer.reduce_line_pass()
        reducer.is_initial_state_interesting()

    # enforce 2-minimality
    if args.two_min:
        logger.error("Reducing by line - 2 minimality")
        reducer.reduce_line_two_minimal()

    if args.run_within:
        logger.error("Reducing within lines")
        reducer.reduce_within_line()

    # check final input is _still_ interesting
    reducer.is_initial_state_interesting()

    # now we're at the bitter end, spit out the remaining, minimised, sector files to output dir
    reducer.sectors.write_files(args.mindir)

    logger.info("reduction complete")


def get_sectors(sector, input_dir):
    try:
        lines = [line for line in codecs.open(sector, 'r', 'utf-8')]
    except (OSError, IOError):
        logger.error("sector file %s not found" % sector)
    sector_list = []
    for line in lines:
        sector_list.append(os.path.join(input_dir, line.strip() + '.sec'))
    logger.info(sector_list)
    return sector_list


if __name__ == '__main__':
    process()
