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
    parser.add_argument('--min-btn', dest='btn', default=13, type=int, 
                        help='Minimum BTN used for route calculation, default [13]')
    parser.add_argument('--min-ally-count', dest='ally_count', default=10, type=int,
                        help='Minimum number of worlds in an allegiance for output, default [10]')
    parser.add_argument('--min-route-btn', dest='route_btn', default=8, type=int,
                        help='Minimum btn for drawing on the map, default [8]' )
    parser.add_argument('--max-jump', dest='max_jump', default=4, type=int,
                        help='Maximum jump distance for trade routes, default [4]')
    parser.add_argument('--no-routes', dest='routes', default=True, action='store_false')
    parser.add_argument('--no-trade', dest='trade', default=True, action='store_false')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('sector', nargs='+', help='T5SS sector file(s) to process')
    args = parser.parse_args()
    
    logger.info("starting processing")
    
    galaxy = Galaxy(args.btn, args.max_jump, args.route_btn);
    galaxy.read_sectors (args.sector)
    
    logger.info ("%s sectors read" % len(galaxy.sectors))
    
    galaxy.set_edges(args.routes)
    galaxy.set_borders(args.borders)


    if args.routes and args.trade:
        galaxy.trade.calculate_routes()
        
    if args.routes:
        galaxy.write_routes()
    
    pdfmap = HexMap(galaxy, args.route_btn)
    pdfmap.write_maps()
    
    stats = StatCalculation(galaxy)
    stats.calculate_statistics()
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
    