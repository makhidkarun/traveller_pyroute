'''
Created on Mar 2, 2014

@author: tjoneslo
'''


import argparse
import logging

def process():
    parser = argparse.ArgumentParser(description='Traveller trade route generator.')
    parser.add_argument('sectors', nargs='+')
    args = parser.parse_args()
    
    logging.info("starting processing")
    



if __name__ == '__main__':
    process