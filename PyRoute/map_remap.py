#!/usr/bin/python
"""
Created on Apr 12, 2014

@author: tjoneslo

Post-processor for the route generator to produce the needed output files
for Traveller Map. This produces a set of files (one per sector) of
XML tags for the routes as specified by the TravellerMap conventions.


"""

import re
import math
import argparse
from collections import defaultdict
import xml.etree.ElementTree as ET
import os
import codecs
from xml.dom import minidom


def sort_key(aString):
    return aString[-8:-3]


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    rough_string = rough_string.replace(rough_string, '\r\n', '\n')
    rough_string = rough_string.replace(rough_string, '\n', '')
    rough_string = rough_string.replace(rough_string, '>    <', '><')
    rough_string = rough_string.replace(rough_string, '>  <', '><')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def output_link(start, end, color, routeType, sectorStart, sectorEnd):
    output = ET.Element('Route', {'Start': start, 'End': end, 'Color': color, 'Type': routeType})

    if sectorStart == sectorEnd:
        return (output, None)

    outStart = output
    outEnd = ET.Element('Route', {'Start': end, 'End': start, 'Color': color, 'Type': routeType})
    startx = int(start[0:2])
    starty = int(start[2:4])
    endx = int(end[0:2])
    endy = int(end[2:4])

    if startx <= 4 and endx >= 28:
        outStart.attrib['EndOffsetX'] = '-1'
        outEnd.attrib['EndOffsetX'] = '1'
    elif startx >= 28 and endx <= 4:
        outStart.attrib['EndOffsetX'] = '1'
        outEnd.attrib['EndOffsetX'] = '-1'
    if starty <= 4 and endy >= 36:
        outStart.attrib['EndOffsetY'] = '-1'
        outEnd.attrib['EndOffsetY'] = '1'
    elif starty >= 36 and endy <= 4:
        outStart.attrib['EndOffsetY'] = '1'
        outEnd.attrib['EndOffsetY'] = '-1'

    return (outStart, outEnd)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='route remap for trade routes')
    parser.add_argument('route_file', help='PyRoute route (stars.txt) to process')
    parser.add_argument('metadata_source', help='TravellerMap metadata xml source file directory')
    parser.add_argument('output_dir', help='output directory for xml metadata')
    args = parser.parse_args()

    tradeColors = ['#99FF0000', '#BFFFFF00', '#8000BF00', '#9900FFFF', '#990000FF', '#BF800080', 'violet']

    regex = ".*\((.*) (\d\d\d\d)\).*\((.*) (\d\d\d\d)\) .* 'trade': ([0-9]*[L]?)"
    match = re.compile(regex)
    # Kuunaa (Core 0304) Irkigkhan (Core 0103) {'distance': 2, 'btn': 13, 'weight': 41, 'trade': 1000000000}
    sectors = defaultdict(list)

    with open(args.route_file) as f:
        for entry in f:
            data = match.match(entry).groups()
            sectorStart = data[0]
            start = data[1]
            sectorEnd = data[2]
            end = data[3]
            trade = int(data[4])

            if trade == 0:
                continue

             btn = int(math.log(trade, 10))

            if btn - 8 < 0:
                continue
            color = tradeColors[btn - 8]
            routeType = 'btn%02d' % btn

            (outStart, outEnd) = output_link(start, end, color, routeType, sectorStart, sectorEnd)

            sectors[sectorStart].append(outStart)
            if outEnd is not None:
                sectors[sectorEnd].append(outEnd)

    for sector in sectors.keys():
        tree = ET.ElementTree()
        path = os.path.join(args.metadata_source, '%s.xml' % sector)
        tree.parse(path)
        routes = tree.find('Routes')
        if routes is not None:
            for route in routes.iter('Route'):
                if route.attrib.get('Type', '').startswith('btn'):
                    routes.remove(route)
        else:
            routes = ET.Element('Routes')
            tree.getroot().append(routes)

        routes.extend(sectors[sector])
        pretty = prettify(tree.getroot())
        outPath = os.path.join(args.output_dir, '%s.xml' % sector)
        with codecs.open(outPath, 'wb', 'utf-8') as f:
            f.write(pretty)
