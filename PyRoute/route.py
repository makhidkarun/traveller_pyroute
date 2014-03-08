'''
Created on Mar 2, 2014

@author: tjoneslo
'''


import argparse
import logging
import Galaxy

logger = logging.getLogger('PyRoute')

def read_sectors(sectors):
    logger.info(sectors)

def process():
    parser = argparse.ArgumentParser(description='Traveller trade route generator.')
    parser.add_argument('sectors', nargs='+')
    args = parser.parse_args()
    
    logger.info("starting processing")
    
    galaxy = Galaxy.Galaxy(20,20);
    
    galaxy.read_sectors (args.sectors)
    
    logger.info ("sectors read")
    
    galaxy.set_edges()
#    galaxy.set_borders()
    galaxy.calculate_routes()

    galaxy.write_routes()
    
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
    