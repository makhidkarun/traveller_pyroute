#!/usr/bin/pypy
'''
Created on Mar 2, 2014

@author: tjoneslo
'''


import argparse
import logging
import codecs
import os
from Galaxy import Galaxy
from HexMap import HexMap
from StatCalculation import StatCalculation

logger = logging.getLogger('PyRoute')

def process():
    parser = argparse.ArgumentParser(description='Traveller trade route generator.')
    parser.add_argument('--borders', choices=['none', 'range', 'allygen', 'erode'], default='range',
                        help='Allegiance border generation, default [range]')
    parser.add_argument('--ally-match', choices=['collapse', 'separate'], default='collapse',
                        help='Allegiance matching for borders, default [collapse]')
    parser.add_argument('--min-btn', dest='btn', default=13, type=int, 
                        help='Minimum BTN used for route calculation, default [13]')
    parser.add_argument('--min-ally-count', dest='ally_count', default=10, type=int,
                        help='Minimum number of worlds in an allegiance for output, default [10]')
    parser.add_argument('--min-route-btn', dest='route_btn', default=8, type=int,
                        help='Minimum btn for drawing on the map, default [8]' )
    parser.add_argument('--max-jump', dest='max_jump', default=4, type=int,
                        help='Maximum jump distance for trade routes, default [4]')
    parser.add_argument('--pop-code', choices=['fixed', 'scaled', 'benford'], default='scaled',
                        help='Interpretation of the population modifier code, default [scaled]')

    parser.add_argument('--owned-worlds', dest='owned', default=False, action='store_true')
    
    parser.add_argument('--routes', dest='routes', choices=['trade', 'comm','xroute', 'owned', 'none'], default='trade',
                        help='Route type to be generated, default [trade]')
    parser.add_argument('--route-reuse', default=10, type=int,
                        help='Scale for reusing routes during route generation')
    
    parser.add_argument('--output', default='maps', help='output directory for maps, statistics')
    
    parser.add_argument('--no-trade', dest='trade', default=True, action='store_false')
    parser.add_argument('--no-maps', dest='maps', default=True, action='store_false')
    parser.add_argument('--version', action='version', version='%(prog)s 0.3')
    parser.add_argument('--log-level', default='INFO')
    parser.add_argument('--input', default='sectors', help='input directory for sectors')
    parser.add_argument('--sectors', default=None, help='file with list of sector names to process')
    parser.add_argument('sector', nargs='*', help='T5SS sector file(s) to process')
    args = parser.parse_args()

    set_logging(args.log_level)
    
    logger.info("starting processing")
    
    galaxy = Galaxy(args.btn, args.max_jump, args.route_btn);
    galaxy.output_path = args.output
    
    sectors_list = args.sector
    if args.sectors is not None:
        sectors_list.extend(get_sectors(args.sectors, args.input))
    
    galaxy.read_sectors (sectors_list, args.pop_code, args.ally_match)
    
    logger.info ("%s sectors read" % len(galaxy.sectors))
    
    
    galaxy.generate_routes(args.routes, args.owned, args.route_reuse)
    
    galaxy.set_borders(args.borders, args.ally_match)


    if args.owned:
        galaxy.process_owned_worlds()

    if args.trade:
        galaxy.trade.calculate_routes()

    if args.routes:
        galaxy.write_routes(args.routes)

    stats = StatCalculation(galaxy)
    stats.calculate_statistics(args.ally_match)
    stats.write_statistics(args.ally_count)
    
    if args.maps:
        pdfmap = HexMap(galaxy, args.routes, args.route_btn)
        pdfmap.write_maps()
    
    logger.info("process complete")

def get_sectors(sector, input_dir):
    try:
        lines = [line for line in codecs.open(sector,'r', 'utf-8')]
    except (OSError, IOError):
        logger.error("sector file %s not found" % sector)
    sector_list = []
    for line in lines:
        sector_list.append(os.path.join(input_dir, line.strip()+'.sec'))
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
    