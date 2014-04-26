#!/usr/bin/python
'''
Created on Apr 12, 2014

@author: tjoneslo

Post-processor for the route generator to produce the needed output files 
for Traveller Map. This produces a set of files (one per sector) of
XML tags for the routes as specified by the TravellerMap conventions. 


'''

import re
import math
import argparse
from collections import defaultdict


def sort_key(aString):
    return aString[-8:-3]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='route remap for trade routes')
    parser.add_argument('route_file', help='PyRoute route (stars.txt) to process')
    args = parser.parse_args()

    tradeColors = ['99FF0000','BFFFFF00', '8000BF00', '9900FFFF', '990000FF', 'BF800080', 'violet' ]

    regex = ".*\((.*) (\d\d\d\d)\).*\((.*) (\d\d\d\d)\) .* 'trade': ([0-9]*[L]?)" 
    match = re.compile(regex)
    #Kuunaa (Core 0304) Irkigkhan (Core 0103) {'distance': 2, 'btn': 13, 'weight': 41, 'trade': 1000000000}
    with open(args.route_file) as f:
        content = f.readlines()
        
    sectors = defaultdict(list)
    output = []
    for entry in content:
        data = match.match(entry).groups()
        sectorStart = data[0]
        start = data[1]
        sectorEnd = data[2]
        end = data[3]
        trade = long(data[4])
        
        if trade == 0:
            continue
        
        btn = int(math.log(trade,10))
        
        if btn - 8 < 0:
            continue
        color = tradeColors[btn-8]
        routeType = 'btn%02d'%btn

        offset = " "
        if sectorStart != sectorEnd:
            startx = int(start[0:2])
            starty = int(start[2:4])
            endx = int(end[0:2])
            endy = int(end[2:4])
            
            if startx < 4 and endx > 28:
                offset += ' EndOffsetX="-1" '
            elif startx > 28 and endx < 4:
                offset += ' EndOffsetX="1" '
            if starty < 4 and endy > 36:
                offset += ' EndOffsetY="-1" '
            elif starty > 36 and endy < 4:
                offset += ' EndOffsetY="1" '
            #EndOffsetX="-1" EndOffsetY="+1"
            pass
        
        
        output = '<Route Start="{}" End="{}"{}Color="#{}" Type="{}"/>'.format(start, end, offset, color, routeType)
                
        sectors[sectorStart].append(output)

    for sector,output in sectors.iteritems():
        output.sort(key=sort_key)
        outFile = "maps/%s.xml" % sector
        with open (outFile, "wb") as f:
            for line in output:
                f.write(line + "\n")
        