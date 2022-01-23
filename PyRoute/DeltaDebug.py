"""
Created on Dec 28, 2021

@author: CyberiaResurrection

A dirt-simple wrapper to enable error-causing inputs to be minimised
through applying the delta-debugging approach.

In brief, delta debugging notes that a given input triggering some
sort of program misbehaviour contains a (usually relatively) small
amount of input relevant to the failure, and a much larger amount
of irrelevant input.  Delta-debugging aims to produce a reasonable
approximation of _just_ the relevant input, while removing the bulk
of the irrelevant input, chunk by chunk.

For the moment, it can only handle a single sector file input, and
requires the user to specify a line that must appear in the run output
for that run to count as "interesting".
"""

import argparse
import logging
import codecs
import os
import math

from Galaxy import Galaxy, Sector, Subsector, Allegiance
from AllyGen import AllyGen
from Star import Star
from SpeculativeTrade import SpeculativeTrade
from HexMap import HexMap
from SubsectorMap2 import GraphicSubsectorMap
from StatCalculation import StatCalculation
from wikistats import WikiStats


logger = logging.getLogger('PyRoute')


def process():
    parser = argparse.ArgumentParser(description='PyRoute input minimiser.')
    logger.setLevel(logging.CRITICAL)

    pyroute = parser.add_argument_group('PyRoute', 'Parameters used by PyRoute directly')
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

    delta = parser.add_argument_group('Debugging', 'Parameters for the delta-debugging procedure itself')
    delta.add_argument('--source-file', dest="sourcefile",
                       help='Sector file to be minimised.  Minimised result will have -min added to its filename')
    delta.add_argument('--output-dir', dest="outputdir",
                       help='Output folder to place any maps generated during minimisation.')
    delta.add_argument('--interesting-line', dest="interestingline", default=None,
                       help="Line required to classify run output as interesting")
    delta.add_argument('--interesting-type', dest="interestingtype", default=None,
                       help="Exception type required to classify run output as interesting")

    args = parser.parse_args()

    sourcefile = args.sourcefile
    basename = os.path.basename(sourcefile)
    lines = [line for line in codecs.open(sourcefile, 'r', 'utf-8')]
    outname = os.path.join(args.outputdir, basename) + "-min"

    headers, starlines = partition_file(lines)

    # set up master copy of galaxy data structure for later reuse
    sec = Sector(lines[3], lines[4])
    sec.filename = basename

    galaxy = Galaxy(args.btn, args.max_jump, args.route_btn)
    galaxy.output_path = args.outputdir
    galaxy.sectors[sec.name] = sec

    for line in headers:
        # swiped holus bolus from Galaxy's read_sectors method
        if line.startswith('# Subsector'):
            data = line[11:].split(':', 1)
            pos = data[0].strip()
            name = data[1].strip()
            sec.subsectors[pos] = Subsector(name, pos, sec)
        if line.startswith('# Alleg:'):
            alg_code = line[8:].split(':', 1)[0].strip()
            alg_name = line[8:].split(':', 1)[1].strip().strip('"')

            # A work around for the base Na codes which may be empire dependent.
            alg_race = AllyGen.population_align(alg_code, alg_name)

            base = AllyGen.same_align(alg_code)
            if base not in galaxy.alg:
                galaxy.alg[base] = Allegiance(base, AllyGen.same_align_name(base, alg_name), base=True,
                                            population=alg_race)
            if alg_code not in galaxy.alg:
                galaxy.alg[alg_code] = Allegiance(alg_code, alg_name, base=False, population=alg_race)

    galaxy.set_bounding_subsectors()
    lines = starlines

    # now header file is partitioned, we can run the original input to verify that it is actually interesting
    interesting, firstmsg, interesting_stars = process_lines(args, galaxy, lines, sec)

    if not interesting:
        raise Exception("Original input not interesting - aborting")
    print("Original input has " + str(len(starlines)) + " lines")

    # now that original input is interesting, we can start minimisation
    # partition original starlines
    finallines, shortmsg = process_delta(args, galaxy, starlines, sec, interesting_stars)

    if shortmsg is None:
        shortmsg = firstmsg

    # now finallines is 1-minimal - removing any 1 element would stop making it interesting.
    # every remaining element has been demonstrated to be individually necessary for
    # interestingness, and collectively sufficient for interestingness.
    # we're done, write out the minimised file as a sector file
    if shortmsg is not None:
        print("Shortest interesting exception message: " + shortmsg)
    print("Writing results out to " + outname)
    write_file(outname, headers, finallines)


def process_delta(args, galaxy, lines, sec, interesting_stars):
    num_chunks = 2
    singleton_not_run = True
    short_msg = None

    while num_chunks <= len(lines):
        chunks = chunk_lines(lines, num_chunks)
        remove = []
        best_lines = None
        print("# of lines: " + str(len(lines)) + ", # of chunks: " + str(num_chunks))
        for i in range(0, num_chunks):
            if i >= len(chunks):
                continue
            raw_lines = []
            # Assemble all _but_ the ith chunk
            for j in range(0, num_chunks):
                if i == j:
                    continue
                if j >= len(chunks):
                    continue
                raw_lines.extend(chunks[j])
            interesting, msg, temp_stars = process_lines(args, galaxy, raw_lines, sec)
            # We've found a chunk of input and have _demonstrated_ its irrelevance,
            # empty that chunk, update best lines so far, and continue
            if interesting:
                if i < len(chunks):
                    if msg is not None:
                        if short_msg is None:
                            short_msg = msg
                        elif len(msg) < len(short_msg):
                            short_msg = msg

                    chunks[i] = []
                    remove.append(i)
                    best_lines = raw_lines
                    interesting_stars = temp_stars
                    print("Reduction found: new input has " + str(len(best_lines)) + " lines")

        if 0 < len(remove):
            assert (best_lines is not None, "Best_lines not set during minimisation")
            num_chunks -= len(remove)
            lines = best_lines

        num_chunks *= 2

        if num_chunks > len(lines):
            if singleton_not_run:
                num_chunks = len(lines)
                singleton_not_run = False

    print("Base reduction complete - verifying 1-minimality")
    i = 0
    while i < len(lines):
        raw_lines = lines.copy()
        del raw_lines[i]
        interesting, msg, temp_stars = process_lines(args, galaxy, raw_lines, sec)
        if interesting:
            lines = raw_lines
            interesting_stars = temp_stars
            print("Reduction found: new input has " + str(len(lines)) + " lines")
        else:
            i += 1

    assert interesting_stars is not None, "Interesting-star edge list must be set by time reduction is complete"
    # now reduction is complete, borrow wikistats to dump out galaxy.stars
    galaxy.stars = interesting_stars
    wikistat = WikiStats(galaxy, None, 10, 'collapse', True)
    wikistat.write_json()
    galaxy.write_routes(delimiter='&')

    print("Reduction complete: reduced input has " + str(len(lines)) + " lines")

    return lines, short_msg


def process_lines(args, galaxy, lines, sec):
    galaxy.reset_stars()
    interesting = False
    msg = None
    interesting_stars = None

    try:
        for line in lines:
            if line.startswith('#') or len(line) < 20:
                continue
            star = Star.parse_line_into_star(line, sec, args.pop_code, args.ru_calc)
            if star:
                sec.worlds.append(star)
                sec.subsectors[star.subsector()].worlds.append(star)
                star.alg_base_code = AllyGen.same_align(star.alg_code)

                galaxy.set_area_alg(star, galaxy, galaxy.alg)
                galaxy.set_area_alg(star, sec, galaxy.alg)
                galaxy.set_area_alg(star, sec.subsectors[star.subsector()], galaxy.alg)

                star.tradeCode.sophont_list.append("{}A".format(galaxy.alg[star.alg_code].population))

        logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds)))

        galaxy.set_positions()

        logger.info("%s sectors read" % len(galaxy.sectors))

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

        if interesting:
            interesting_stars = galaxy.stars

    return interesting, msg, interesting_stars


def partition_file(lines):
    """
        Break lines out into headers section, which is retained, and starlines, which gets minimised - this assumes
        downloaded-from-TravellerMap sector file
    """
    headers = []
    starlines = []
    isheader = True
    for line in lines:
        if isheader:
            headers.append(line)
            if line.startswith('----'):
                isheader = False
        else:
            starlines.append(line)
    return headers, starlines


def write_file(out_name, headers, lines):
    handle = codecs.open(out_name, 'w', 'utf-8')
    for line in headers:
        handle.write(line)

    for line in lines:
        handle.write(line)

    handle.close()


def chunk_lines(lines, num_chunks):
    n = math.ceil(len(lines) / num_chunks)
    return [lines[i:i + n] for i in range(0, len(lines), n)]


if __name__ == '__main__':
    process()
