#!/usr/bin/python3
"""
Created on Jan 12, 2025

@author: CyberiaResurrection
"""

import argparse
import logging
import codecs

logger = logging.getLogger('PyRoute')


def process():
    parser = argparse.ArgumentParser(
        description='Traveller trade route sector list deduplicator.'
    )
    parser.add_argument(
        '--infile',
        help='file with list of sector names to process',
        default="sectorlist.txt"
    )
    parser.add_argument(
        '--outfile',
        help='file to write deduplicated list of sector names to',
        default="sectorlist_uniq.txt"
    )
    parser.add_argument(
        '--log-level',
        default='INFO'
    )

    args = parser.parse_args()
    set_logging(args.log_level)

    srcfile = args.infile
    outfile = args.outfile
    if outfile is None:
        outfile = srcfile

    # read srcfile in, line by line:
    try:
        with codecs.open(srcfile, 'r', 'utf-8') as infile:
            lines = [line for line in infile]
    except FileNotFoundError as e:
        logger.error("Sector file " + srcfile + " not found.  Cannot continue.")
        raise e

    line_set = set()
    for line in lines:
        line_set.add(line)

    lines = list(line_set)
    lines.sort()

    try:
        with codecs.open(outfile, "w", "utf-8") as targfile:
            targfile.writelines(lines)
    except Exception as e:
        logger.error("Deduplicated sector file " + outfile + " could not be created.  Cannot continue")
        raise e

    logger.info("process complete")


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
