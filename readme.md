PyRoute for Traveller
=====================

PyRoute is a trade route generation program for Traveller. PyRoute has been ported to python3, there is a branch with 
the python2 version.

The data for the maps comes from [Traveller Map](http://www.travellermap.com/) based upon the Traveller 5th edition 
second survey data plus many of the fan created sectors from around the Internet and across the years. Traveller Map 
presents the sector data in a consistent format, making the input processing considerably easier. 

The trade rules are from [GURPS Traveller: Far trader](http://www.sjgames.com/traveller/fartrader/). These rules are 
based on a gravity trade model. Each world is given a weight called the World Trade Number (WTN) calculated from 
population, starport, and other factors. For each pair of worlds a Bilateral Trade Number (BTN) generated based upon 
the two WTNs and adjusted for distance and other factors. 

The routes followed for trade are created by the shortest path algorithms from [NetworkX](http://networkx.github.io/), 
a library for managing graphs. You will need version 2.1 or later for the Unicode handling. 

The final output, the map of trade routes, is created by [PyPDFLite](https://github.com/katerina7479/pypdflite). You 
will need the python3 branch version of this library. 

You can install the required libraries using pip:

    pip install -r requirements.txt

The map generation requires several fonts not normally installed in the system:

    apt-get install fonts-dejavu fonts-liberation fonts-freefont-ttf fonts-ancient-scripts fonts-symbola

For the math and layout of hex maps, I recommend the
[Hexagonal Grids](http://www.redblobgames.com/grids/hexagons/) page which contains every item you
will need to draw and manage hexagon maps.I recommend all the articles on the Red 
Blob Games site.

The original version of this program, [nroute.c](http://wiki.travellerrpg.com/Nroute.c), was
written by Anthony Jackson. 

Running the program
===================

    $ python PyRoute/route.py --help
    usage: route.py [-h] [--borders {none,range,allygen,erode}]
                [--ally-match {collapse,separate}]
                [--routes {trade,comm,xroute,owned,none}] [--min-btn BTN]
                [--min-route-btn ROUTE_BTN] [--max-jump MAX_JUMP]
                [--pop-code {fixed,scaled,benford}]
                [--route-reuse ROUTE_REUSE] [--ru-calc {scaled,negative}]
                [--speculative-version {CT,T5,None}] [--output OUTPUT]
                [--owned-worlds] [--no-trade] [--no-maps]
                [--no-subsector-maps] [--min-ally-count ALLY_COUNT]
                [--json-data] [--input INPUT] [--sectors SECTORS] [--version]
                [--log-level LOG_LEVEL]
                [sector [sector ...]]
    
    Traveller trade route generator.
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
    
    Allegiance:
      Alter processing of allegiances
    
      --borders {none,range,allygen,erode}
                        Allegiance border generation, default [range]
      --ally-match {collapse,separate}
                        Allegiance matching for borders, default [collapse]
    
    Routes:
      Route generation options
    
      --routes {trade,comm,xroute,owned,none}
                        Route type to be generated, default [trade]
      --min-btn BTN         Minimum BTN used for route calculation, default [13]
      --min-route-btn ROUTE_BTN
                        Minimum btn for drawing on the map, default [8]
      --max-jump MAX_JUMP   Maximum jump distance for trade routes, default [4]
      --pop-code {fixed,scaled,benford}
                        Interpretation of the population modifier code,
                        default [scaled]
      --route-reuse ROUTE_REUSE
                        Scale for reusing routes during route generation
      --ru-calc {scaled,negative}
                        RU calculation, default [scaled]
      --speculative-version {CT,T5,None}
                        version of the speculative trade calculations, default
                        [CT]
    
    Output:
      Output options
    
      --output OUTPUT       output directory for maps, statistics
      --owned-worlds        Generate the owned worlds report, used for review
                        purposes
      --no-trade            Do not generate any trade data, only the default
                        statistical data
      --no-maps             Do not generate sector level trade maps
      --no-subsector-maps   Do not generate subsector level maps
      --min-ally-count ALLY_COUNT
                        Minimum number of worlds in an allegiance for output,
                        default [10]
      --json-data           Dump internal data structures as json for later
                            further processing
                        
    
    Input:
      Source of data options
    
      --input INPUT         input directory for sectors
      --sectors SECTORS     file with list of sector names to process
    sector                T5SS sector file(s) to process

The default values are scaled for the standards set by the Traveller world generation used in the T5 Second Survey and,
by extension, the values used by most of the Traveller world generation systems. The parameters are present to allow
generating routes in areas where the worlds don't conform to Imperial standards. 

``borders`` select the algorithm used to draw the borders between various allegiances. `none` sets no borders on the 
map. `range` (the default) uses the border generation from the nroute.c code. `allygen` is based upon the 
[allygen](http://dotclue.org/t20/) code created by J. Greely. `erode` is based upon the border system from 
[TravellerMap](http://travellermap.com/borders/doc.htm).

``ally-match`` determine how the more detailed T5 allegiance codes are either grouped or separated to determine where
borders are drawn. 

The ``min-btn`` argument sets the minimum BTN, trade levels between worlds. Where the calculated trade between two
worlds is below this threshold the routes are ignored. This serves as an optimization to avoid calculating trade
between two worlds which won't add much to the overall trade. The default value (13) works well for the Imperium, but
for areas where worlds are less populous, or have lower TLs overall, setting this lower allow generating more routes. 

The ``min-route-btn`` defines the minimum BTN drawn on the map. The default (8) is scaled for the Imperial standard.
For poorer areas, setting this lower will include routes for more worlds. The ``min-route-btn`` and ``min-btn`` work
together to produce a better map. For optimal results set ``min-btn`` to `min-route-btn` * 2 - 1 (15 for the default settings). 

``max-jump`` selects the maximum distance used for trade route generation. Changing this can be based on jump drive
availability. For lower TL areas or eras, setting this to 2 or 3 makes the rules reflect an earlier era. For an area
where the stars are spread, set to 5 or 6 to include routes across the gaps. 

``min-ally-count`` controls which allegiance codes are output in the `alleg_summary.wiki` file. The value is the minimum
number of worlds in an empire to be includes in the output. The default is 10 worlds. For a map with many small empires
setting this to 0 to include all of them in the output file. 

``pop-code`` controls the interpretation of the population modifier. `fixed` is the standard Traveller interpretation
of the code.  `benford` re-distributes, using a random number generator, the existing population codes to match
[Benford's Law](http://en.wikipedia.org/wiki/Benford%27s_law). This produces a more accurate population distribution,
and reduces the population by about 30%. `scaled` treats the value as a index into a scaled array of values, attempting
to produce the same results as the `benford` population multiplier, but without the random generation. 

``owned-worlds`` is used by the T5 Second Survey team to verify the owned (Government type 6) worlds have a valid
controlling world government. When enabled it produces an `owned-worlds.txt` report. This report lists each owned
world, the current listed owner (if any), and a list of candidate worlds 

The ``routes`` option select the route processing for drawing on the map. The `trade` option drawn the trade routes
as described above. The `comm` option drawn a communications network, connecting the most important worlds, capitals,
naval depots, and scout way stations within the various empires. `xroute` is a second option to draw a communications
route for the Imperial sectors. `none` produces maps with no routes drawn. The last option is useful for producing the
statistical output without the longer route production time. 

The ``route-reuse`` option affects the `trade` route generation. As routes are generated from larger WTN worlds to
smaller WTN worlds, the system prefers to use an already established (probably large) route even if it is slightly
longer (in both parsecs and number of jumps). The default value is 10, and is an arbitrary value. Setting this lower
results in more main routes with a few spiky connectors. Setting it higher results in many nearby (almost overlapping)
routes. Setting it to 30 or above results in every short distance route being individually mapped. 

Input format
------------

PyRoute assumes the input files are the generated raw data files from [Traveller Map](http://www.travellermap.com).
The raw data format is described [here](http://travellermap.com/doc/secondsurvey.html). PyRoute requires the header 
information, especially the sector name, location, subsectors list, and the _Alleg_ information. The parser is not
especially robust and will fail or produce unexpected results if the data is incorrectly formatted. 

Output files
------------

There are four types of output files: 

1) The PDF maps. The data on the maps, including the interpretations of the trade line colors is kept in the
[Trade map key](http://wiki.travellerrpg.com/Trade_map_key). PyRoute generates one map per sector based upon the input files.

1) The raw route data. Two files called `stars.txt` and `ranges.txt` are the output of the two internal data
structures PyRoute uses to generate the trade map. `ranges.txt` is the list of trade partner pairs. This is the list
driving the route generation process. The `stars.txt` is the list of all possible routes of max-jump distances between
each star. This list is trimmed of the longer, or unused routes. This list holds the final trade route information. 

1) The wiki summary formatted for putting into the Traveller wiki in the
[Trade map summary](http://wiki.travellerrpg.com/Trade_map_summary) page, and consisting of the following files:
    * `summary.wiki` contains a summary table of the analysis and a summary breakdown of the UWP components.
    * `sectors.wiki` contains an economic breakdown by sector and detailed analysis for each sector. 
    * `subsectors.wiki` contains a detailed analysis for each subsector, ordered by sector, 
    and by position in the sector. 
    * `allegiance.wiki` contains an economic breakdown by Allegiance code and a detailed analysis of each interstellar
    government.

1) The per sector generated data. PyRoute generates a fair amount of data including the
    trade information, economic data, passenger information, and armed forces numbers for each world. These files 
    captures all of this data for each world, output in a similar format to the sector files. 
    * `<sector name>.sector.wiki` has a table of the T5 sector information in wiki table format
    * `<sector nane>.economic.wiki` has a table of the economic information for each world in a wiki table format
    
1) As an option you can output the input data and generated statistics in json format. This contain the data as loaded
from the source sector files, and the analysis done by the different internal processes. 
    * `galaxy.json` contains the global information, including allegiances and statistics.
    * `<secor name>.json` contains the information about the individual sector, including allegiances, stars, and statistical information. 

Performance
-----------

The process takes between O(n^2) and O(n^3) processing time, meaning the more stars (and hence routes), the longer
the process takes. Experimentation has shown:

* Small areas (100-200 stars) take a few seconds
* Full sectors (400-600 stars) take one to two minutes 
* Multi-sector areas (around 2000 stars) take 20 to 30 minutes
* The T5 Second survey area (30 sectors, 12880 stars) takes 3-4 hours
* The entire of charted space (132 sectors, 50,598 stars) takes 15 to 18 hours. 

Map Borders
===========

PyRoute has four border generation algorithms, with one option for selection of allies. 

`ally-match` option determines if similar allied groups are grouped as one empire, or separated into their component
parts. The T5 Second Survey Allegiance codes are 4 characters. This allows identifying sub-groups within a larger
empire. For example the Third Imperium (original code Im) now has different codes for each domain (for example, ImDe for
the Domain of Deneb). Setting `ally-match` to `collapse` considered the worlds in the Domain of Deneb and the Domain of
Vland to be in the same empire. Setting `ally-match` to `separate` determines these to be different empires and draws a
border between the two domains. 

The four systems for determining how borders are drawn are: 

* `none` - draw no borders on the map. 
* `range` - This is a simple system from the original nroute.c code. This is a two pass process. The first pass sets the alignment of each empty hex around each world to that of the world. The second pass extends the empty hex alignment selection to the next circle of hexes. If a hex already has an alignment, either because there is a world there or selected by earlier step, the previous selection is kept. 
* `allygen` - This is a partial re-implementation of the system presented in [allygen](http://dotclue.org/t20/) code created by J. Greely. As implemented here, this is a three pass process. The first pass marks each hex around every world as aligned with that world. The distance of selected hexes depends upon the center world's starport (E,X ports have none, A ports have range of 4). If there is more than one world claiming an empty hex, the list of claimants is kept. The second pass, the alignments of the empty hexes is resolved by selecting (in order) the single claimant, the closer world, or the larger empire. In a third pass, some of the hexes at the edge of each empire are set back to unaligned to avoid having odd protuberances.
*  `erode` - Based upon the border drawing system from [TravellerMap](http://travellermap.com/borders/doc.htm). The page has an excellent description of the reason for borders and the algorithm. This is a multi-pass system. The first step is to mark some of the empty hexes with an allegiance code. As described (and implemented) the original system picks one allegiance code and marks every hex on the map. The PyRoute implementation uses slightly modified version of the allygen selection process to perform the initial marking of the empty hexes. This uses the first two steps of the allygen process to mark empty hexes in a radius around each world, then uses a system to select one allegiance for each empty hex. The third pass uses the alternating erode and span breaking system from the border drawing system to reset alignments of empty hexes outside the empire. The fourth step, bridge building, is mention in the article and implemented in code, re-establishes the alignments of some empty hexes between aligned worlds otherwise separated by the third step. 
