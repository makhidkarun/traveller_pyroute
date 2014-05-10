PyRoute for Traveller
=====================

PyRoute is a trade route generation program for Traveller.

The data for the maps comes from [Traveller Map](http://www.travellermap.com/), based upon the Traveller 5th edition second survey data, plus many of the fan created sectors from around the Internet and across the years.

The trade rules are from [GURPS Traveller: Far trader](http://www.sjgames.com/traveller/fartrader/). These rules are based on a gravity trade model. Each world is given a weight called the World Trade Number (WTN) calculated from population, starport, and other factors. For each pair of worlds a Bilateral Trade (BTN) number is generated based upon the two WTNs, and adjusted for distance and other factors. 

The routes followed for trade are created by the shortest path algorithms from [NetworkX](http://networkx.github.io/), a library for managing graphs.

The final output, the map of trade routes, is created by [PyPDFLite](https://github.com/katerina7479/pypdflite). You will need version 0.1.22 or later to include the ellipse and text rotation features. 

You can install both of these libraries using pip:

    pip install networkx pypdflite


For the math and layout of hex maps, I recommend the [Hexagonal Grids](http://www.redblobgames.com/grids/hexagons/) page, which contains every item you will need to draw and manage hexagon maps.I recommend all the articles on the Red Blob Games site.

The original version of this program, [nroute.c](http://wiki.travellerrpg.com/Nroute.c), was written by Anthony Jackson. 

Running the program
===================

    $ python PyRoute/route.py --help 
    usage: route.py [-h] [--borders {none,range,allygen}] [--min-btn BTN]
                    [--min-ally-count ALLY_COUNT] [--min-route-btn ROUTE_BTN]
                    [--max-jump MAX_JUMP] [--pop-code {fixed,scaled,benford}]
                    [--owned-worlds] [--routes {trade,comm,none}] [--no-trade]
                    [--no-maps] [--version]
                    sector [sector ...]

    Traveller trade route generator.

    positional arguments:
      sector                T5SS sector file(s) to process

    optional arguments:
      -h, --help            show this help message and exit
      --borders {none,range,allygen}
                        Allegiance border generation
      --min-btn BTN         Minimum BTN used for route calculation, default [13]
      --min-ally-count ALLY_COUNT
                        Minimum number of worlds in an allegiance for output,
                        default [10]
      --min-route-btn ROUTE_BTN
                        Minimum btn for drawing on the map, default [8]
      --max-jump MAX_JUMP   Maximum jump distance for trade routes, default [4]
      --pop-code {fixed,scaled,benford}
                        Interpretation of the population modifier code
      --owned-worlds
      --routes {trade,comm,none}
                        Route type to be generated
      --no-trade
      --no-maps
      --version             show program's version number and exit

The default values used for the program are scaled for the standards set by the Traveller world generation used in the T5 Second Survey, and by extension, the values used by most of the Traveller world generation systems. The parameters are present to allow generating routes in areas where the worlds don't conform to Imperial standards. 

``borders`` select the algorithm used to draw the borders between various allegiances. `none` sets no borders on the map. `range` (the default) uses the border generation from the nroute.c code. This is a quick border generation system, but can generate odd borders where empires overlap. `allygen` is based upon the [allygen](http://dotclue.org/t20/) code created by J. Greely. This is a more comprehensive border generation system, which produced better, but not perfect borders. 

The ``min-btn`` argument sets the minimum BTN, trade levels between worlds. Worlds where the calculated trade between two worlds is below this threshold are ignored. This serves as an optimization to avoid calculating trade between two worlds which won't add much to the overall trade. The default value (13) works well for the Imperium, but for areas where worlds are less populous, or have lower TLs overall, setting this lower allow generating more routes. 

The ``min-route-btn`` defines the minimum BTN drawn on the map. The default (8) is scaled for the Imperial standard. For poorer areas, setting this lower will include routes for more worlds. The ``min-route-btn`` and ``min-btn`` work together to produce a better map. For optimal results set ``min-btn`` to `min-route-btn` * 2 - 1 (15 for the default settings). 

``max-jump`` selects the maximum distance used for trade route generation. Changing this can be based on jump drive availability. For lower TL areas or eras, setting this to 2 or 3 makes the rules reflect an earlier era. For an area where the stars are spread, setting this higher 5 or 6 may include routes across the gaps. 

``min-ally-count`` controls which allegiance codes are output in the `top_summary.wiki` file. For a map with many small empires it may be worth while setting this to 0 to include all of them in the output file. 

``pop-code`` controls the interpretation of the population modifier. `fixed` is the standard Traveller interpretation of the code.  `benford` re-distributes, using a random number generator, the existing population codes to match [Benford's Law](http://en.wikipedia.org/wiki/Benford%27s_law). This produces a more accurate population distribution, and reduces the population by about 30%. `scaled` treats the value as a index into a scaled array of values, attempting to produce the same results as the `benford` population multiplier, but without the random generation. 

``owned-worlds`` is used by the T5 Second Survey team to verify the owned (Government type 6) worlds have a valid controlling world government. When enabled it produces an `owned-worlds.txt` report. This report lists each owned world, the current listed owner (if any), and a list of candidate worlds 

The ``routes`` option select the route processing for drawing on the map. The `trade` option drawn the trade routes as described above. The `comm` option drawn a communications network, connecting the most important worlds, capitals, naval depots, and scout way stations within the various empires. `none` produces maps with no routes drawn. The last option is useful for producing the statistical output without the longer route production time. 

Input format
------------

PyRoute assumes the input files are the generated raw data files from [Traveller Map](http://www.travellermap.com). The raw data format is described [here](http://travellermap.com/doc/secondsurvey.html). But the header information, especially the sector name, location, and the _Alleg_ information is also required and will cause failure or unexpected results if incorrectly formatted. 


Output files
------------

There are three types of output files: 

1) The PDF maps. The data on the maps, including the interpretations of the trade line colors is kept in the [Trade map key](http://wiki.travellerrpg.com/Trade_map_key). The maps are generated one per sector based upon the input files.

2) The raw route data. Three files called `stars.txt`, `routes.txt`, and `ranges.txt` are the output of the three internal data structures used to generate the trade map. `ranges.txt` is the list of trade partner pairs. This is the list driving the route generation process. `routes.txt` is the list of all possible routes of max-jump between each star, which is then trimmed. `stars.txt` also built from the max-jump distance star pairs and holds the final trade route information. 

3) The wiki summary, formatted for putting into the Traveller wiki in the [Trade map summary](http://wiki.travellerrpg.com/Trade_map_summary) page, and consisting of the following files:

* `summary.wiki` contains the economic breakdown by sector. 
* `top_summary.wiki` contains the economic breakdown by Allegiance code, and a summary breakdown of the UWP components.
* `tcs_summary.wiki` contains a sector level breakdown of the [Trillion Credit Squadron](http://wiki.travellerrpg.com/Trillion_Credit_Squadron) economic and military budgets. 
* `subsector_summary.wiki` contains the same economic breakdown as `summary.wiki`, but by sub-sector. 


Performance
-----------

The process takes between O(n^2) and O(n^3) processing time, meaning the more stars (and hence routes), the longer the process takes. Experimentation has shown:

* Small areas (100-200 stars) take a few seconds
* Full sectors (400-600 stars) take one to two minutes 
* Multi-sector areas (around 2000 stars) take 20 to 30 minutes
* The T5 Second survey area (30 sectors, 12880 stars) takes 3 hours
* The entirely of charted space (114 sectors, 44,977 stars) takes 11 hours 15 minutes

