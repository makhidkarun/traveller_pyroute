#!/usr/bin/pypy
"""
Created on Mar 2, 2014

@author: tjoneslow
"""

import argparse
import logging
import codecs
import os

from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Galaxy import Galaxy
from PyRoute.SpeculativeTrade import SpeculativeTrade
from PyRoute.Outputs.PDFHexMap import PDFHexMap
from PyRoute.Outputs.SubsectorMap2 import GraphicSubsectorMap
from PyRoute.StatCalculation import StatCalculation

logger = logging.getLogger('PyRoute')


def process():
    parser = argparse.ArgumentParser(description='Traveller trade route generator.', fromfile_prefix_chars='@')

    alleg = parser.add_argument_group('Allegiance', 'Alter processing of allegiances')
    alleg.add_argument('--borders', choices=['none', 'range', 'allygen', 'erode'], default='range',
                       help='Allegiance border generation, default [range]')
    alleg.add_argument('--ally-match', choices=['collapse', 'separate'], default='collapse',
                       help='Allegiance matching for borders, default [collapse]')

    route = parser.add_argument_group('Routes', 'Route generation options')
    route.add_argument('--routes', dest='routes',
                       choices=['trade', 'comm', 'xroute', 'owned', 'none', 'trade-mp'], default='trade',
                       help='Route type to be generated, default [trade]')
    route.add_argument('--min-btn', dest='btn', default=13, type=int,
                       help='Minimum BTN used for route calculation, default [13]')
    route.add_argument('--min-route-btn', dest='route_btn', default=8, type=int,
                       help='Minimum btn for drawing on the map, default [8]')
    route.add_argument('--max-jump', dest='max_jump', default=4, type=int, choices=range(1, 11),
                       help='Maximum jump distance for trade routes, default [4]')
    route.add_argument('--pop-code', choices=['fixed', 'scaled', 'benford'], default='scaled',
                       help='Interpretation of the population modifier code, default [scaled]')
    route.add_argument('--route-reuse', default=10, type=int,
                       help='Scale for reusing routes during route generation')
    route.add_argument('--ru-calc', default='scaled', choices=['scaled', 'negative'],
                       help='RU calculation, default [scaled]')
    route.add_argument('--speculative-version', choices=['CT', 'T5', 'None'], default='CT',
                       help='version of the speculative trade calculations, default [CT]')
    route.add_argument('--mp-threads', default=os.cpu_count() - 1, type=int,
                       help=f"Number of processes to use for trade-mp processing, default {os.cpu_count() - 1}")

    output = parser.add_argument_group('Output', 'Output options')

    output.add_argument('--output', default='maps', help='output directory for maps, statistics')
    output.add_argument('--owned-worlds', dest='owned', default=False, action=argparse.BooleanOptionalAction,
                        help='Generate the owned worlds report, used for review purposes')
    output.add_argument('--trade', default=True, action=argparse.BooleanOptionalAction,
                        help='Generate trade data with route information')
    output.add_argument('--maps', dest='maps', default=True, action=argparse.BooleanOptionalAction,
                        help='Generate sector level trade maps')
    output.add_argument('--subsector-maps', dest='subsectors', default=True, action=argparse.BooleanOptionalAction,
                        help='Generate subsector level maps')
    output.add_argument('--min-ally-count', dest='ally_count', default=10, type=int,
                        help='Minimum number of worlds in an allegiance for output, default [10]')
    output.add_argument('--json-data', dest='json_data', default=False, action='store_true',
                        help='Dump internal data structures as json for later further processing ')

    source = parser.add_argument_group('Input', 'Source of data options')
    source.add_argument('--input', default='sectors', help='input directory for sectors')
    source.add_argument('--sectors', default=None, help='file with list of sector names to process')
    source.add_argument('--deep-space', dest='deep_space', default=None, help='file with list of deep space stations to process')
    source.add_argument('sector', nargs='*', help='T5SS sector file(s) to process')

    debugging = parser.add_argument_group('Debug', "Debugging flags")
    debugging.add_argument('--debug', dest="debug_flag", default=False, action=argparse.BooleanOptionalAction,
                           help="Turn on trade-route debugging")
    debugging.add_argument('--fix-pop', dest="fix_pop", default=False, action=argparse.BooleanOptionalAction,
                           help="Fix incorrect pop codes when loading stars")

    parser.add_argument('--version', action='version', version='%(prog)s 0.4')
    parser.add_argument('--log-level', default='INFO')

    args = parser.parse_args()

    set_logging(args.log_level)

    logger.info("starting processing")

    galaxy = Galaxy(args.btn, args.max_jump)

    galaxy.output_path = args.output

    raw_sectors_list = args.sector
    if args.sectors is not None:
        raw_sectors_list.extend(get_sectors(args.sectors, args.input))

    sectors_list = []
    for sector in raw_sectors_list:
        if sector not in sectors_list:
            sectors_list.append(sector)
        else:
            logger.warning(sector + " is duplicated")

    raw_dss_list = args.deep_space
    deep_space_lines = []
    if raw_dss_list is not None:
        try:
            deep_space_lines = [line for line in codecs.open(raw_dss_list, 'r', 'utf-8')]
        except (OSError, IOError):
            pass

    deep_space = {}
    for line in deep_space_lines:
        bitz = line.split(',')
        if 2 != len(bitz):
            continue
        if bitz[0] not in deep_space:
            deep_space[bitz[0]] = []
        deep_space[bitz[0]].append(bitz[1].strip('\n'))

    readparms = ReadSectorOptions(sectors=sectors_list, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                  route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                  mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=args.fix_pop,
                                  deep_space=deep_space)
    galaxy.read_sectors(readparms)

    # galaxy.read_sectors(sectors_list, args.pop_code, args.ru_calc,
    #                    args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag,
    #                    fix_pop=args.fix_pop)

    logger.info("%s sectors read" % len(galaxy.sectors))

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
        pdfmap = PDFHexMap(galaxy, args.routes, args.route_btn)
        pdfmap.write_maps()

        if args.subsectors:
            graphMap = GraphicSubsectorMap(galaxy, args.routes, args.speculative_version)
            graphMap.write_maps()

    logger.info("process complete")


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


def set_logging(level):
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    process()
