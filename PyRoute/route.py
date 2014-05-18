'''
Created on Mar 2, 2014

@author: tjoneslo
'''


import argparse
import logging
from Galaxy import Galaxy
from HexMap import HexMap
from StatCalculation import StatCalculation

logger = logging.getLogger('PyRoute')

def process():
    parser = argparse.ArgumentParser(description='Traveller trade route generator.')
    parser.add_argument('--borders', choices=['none', 'range', 'allygen'], default='range',
                        help='Allegiance border generation')
    parser.add_argument('--ally-match', choices=['collapse', 'separate'], default='collapse',
                        help='Allegiance matching for borders')
    parser.add_argument('--min-btn', dest='btn', default=13, type=int, 
                        help='Minimum BTN used for route calculation, default [13]')
    parser.add_argument('--min-ally-count', dest='ally_count', default=10, type=int,
                        help='Minimum number of worlds in an allegiance for output, default [10]')
    parser.add_argument('--min-route-btn', dest='route_btn', default=8, type=int,
                        help='Minimum btn for drawing on the map, default [8]' )
    parser.add_argument('--max-jump', dest='max_jump', default=4, type=int,
                        help='Maximum jump distance for trade routes, default [4]')
    parser.add_argument('--pop-code', choices=['fixed', 'scaled', 'benford'], default='scaled',
                        help='Interpretation of the population modifier code')

    parser.add_argument('--owned-worlds', dest='owned', default=False, action='store_true')
    
    parser.add_argument('--routes', dest='routes', choices=['trade', 'comm','xroute', 'none'], default='trade',
                        help='Route type to be generated')
    
    parser.add_argument('--output', default='maps', help='output directory for maps, statistics')
    
    parser.add_argument('--no-trade', dest='trade', default=True, action='store_false')
    parser.add_argument('--no-maps', dest='maps', default=True, action='store_false')
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')
    parser.add_argument('sector', nargs='+', help='T5SS sector file(s) to process')
    args = parser.parse_args()
    
    logger.info("starting processing")
    
    galaxy = Galaxy(args.btn, args.max_jump, args.route_btn);
    galaxy.output_path = args.output
    
    galaxy.read_sectors (args.sector, args.pop_code, args.ally_match)
    
    logger.info ("%s sectors read" % len(galaxy.sectors))
    
    
    galaxy.generate_routes(args.routes, args.owned)
    
    galaxy.set_borders(args.borders, args.ally_match)


    if args.owned:
        galaxy.process_owned_worlds()

    if args.trade:
        galaxy.trade.calculate_routes()
    
    if args.maps:
        pdfmap = HexMap(galaxy, args.routes, args.route_btn)
        pdfmap.write_maps()
        
    if args.routes:
        galaxy.write_routes()
    
    stats = StatCalculation(galaxy)
    stats.calculate_statistics(args.ally_match)
    stats.write_statistics(args.ally_count)
    
    logger.info("process complete")


def set_logging():
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == '__main__':
    set_logging()
    process()
    