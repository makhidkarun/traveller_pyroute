PyRoute for Traveller
=====================

PyRoute is a trade route generation program for Traveller.

The data for the maps comes from [Traveller Map](http://www.travellermap.com/),based upon the Traveller 5th edition second survey data, plus many of the fan created sectors from aound the internet and across the years.

The trade rules are from [GURPS Traveller: Far trader](http://www.sjgames.com/traveller/fartrader/). These rules are based upon the idea of a gravity trade model. Each world is given a weight,called the World Trade Number (WTN) based upon population, starport, and other factors. For each pair of worlds, a Bilateral Trade (BTN) number is calculated based upon the two WTNs, and adjusted for distance and other factors. 

The routes followed for trade are created by the shortest path algorithms from [NetworkX](http://networkx.github.io/), a library for managing graphs.

The final output of the generation is created by [PyPDFLite](https://github.com/katerina7479/pypdflite). You will need version 0.1.22 or later to include the ellipse and text rotation features. 

You can install both of these libraries using pip:

    pip install networkx pypdflite


For the math and layout of hex maps, I recommend the [Hexagonal Grids](http://www.redblobgames.com/grids/hexagons/) page, which contains every item you will need to draw and manage hexagon maps.I recommend all the articles on the Red Blob Games site.

The original version of this program, [nroute.c](http://wiki.travellerrpg.com/Nroute.c), was written by Anthony Jackson. 

Running the program
===================

    $ python PyRoute/route.py --helpusage: route.py [-h] [--borders {none,range,allygen}] [--min-btn BTN]
    [--min-ally-count ALLY_COUNT] [--min-route-btn ROUTE_BTN]
    [--max-jump MAX_JUMP] [--no-routes] [--no-trade] [--version]
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
      --pop-code {fixed,scaled}
                        Interpretation of the population modifier code
      --no-routes
      --no-trade
      --version             show program's version number and exit

The default values used for the program are scaled for the standards set by the Traveller world generation used in the T5 Second Survery, and by extension, the values used by most of the Traveller world generation systems. The parameters are present to allow generating routes in areas where the worlds don't conform to Imperial standards. 

The ``borders`` argument defines how borders between various alleginaces are drawn. `none` sets no borders on the map. `range` (the default) uses the border generation from the nroute.c code. This is a quick border generation system, but can generate odd borders where empire overlap. `allygen` is based upon the (allygen)[http://dotclue.org/t20/] code created by J. Greely. This is a more comprehensive border generation system, which produced better, but not perfect borders. 

The ``min-btn`` argument sets the minimum BTN, trade levels between worlds. Worlds where the calculated trade between two worlds is below this threshold are ignored. This serves as an optimization to avoid calculating trade between two worlds which won't add much to the overall trade. The default value (13) works well for the imperium, but for areas where worlds are less populous, or have lower TLs overall, setting this lower will generate more trade. 

The ``min-route-btn`` defines the minimum BTN drawn on the map. The default (8) is scaled for the Imperial standard. For poorer areas, setting this lower will include routes for more worlds. The ``min-route-btn`` and ``min-btn`` work together to produce a better map. For optimal results set ``min-btn`` to `min-route-btn` * 2 - 1 (15 for the default settings). 

``max-jump`` selects the maximum distance used for trade route generation. Changing this can be based on jump drive availablity. For lower TL areas or eras, setting this to 2 or 3 makes the rules reflect an earlier era. 

``min-ally-count`` controls which allegiance codes are output in the top_summary.wiki file. For a map with many small empires it may be worth while setting this to 0 to include all of them in the output file. 

``pop-code`` controls the interpretation of the population modifier. `fixed` is the standard Traveller interpretation of the code. `scaled` treats the value as a index into a scaled array of values.

Input format
------------

PyRoute assumes the input files are the generated raw data files from [Traveller Map](http://www.travellermap.com). The raw data format is described [here](http://travellermap.com/doc/secondsurvey.html). But the header information, especially the sector name, location, and the Alleg information is also required and will cause failure or unexpected results if incorrectly formatted. 


Output files
------------

There are three types of output files: 

1) The PDF maps. The data on the maps, including the interpretations of the trade line colors is kept in the (Trade map key)[http://wiki.travellerrpg.com/Trade_map_key]. The maps are generated one per sector based upon the input files.

2) The raw route data. Three files called `stars.txt`, `routes.txt`, and `ranges.txt` are the output of the three internal data structures used to generate the trade map. `ranges.txt` is the list of trade partner pairs. This is the list driving the route generation process. `routes.txt` is the list of all possible routes of max-jump between each star, which is then trimmed. `stars.txt` also built from the max-jump distance star pairs and holds the final trade route information. 

3) The wiki summary. Two files called `summary.wiki` and `top_summary.wiki` have the accumulated statistical information. This data is formatted for putting into the Traveller wiki in the (Trade map summary)[http://wiki.travellerrpg.com/Trade_map_summary] page. 

Performance
-----------

The process takes an O(n^2) processing time, meaning the more stars (and hence routes), the longer the process takes. Expeimentation has shown that small areas (100-200 stars) take a few seconds, full sectors (400-600 stars) take a minute, multi-sector areas (around 2000 stars) take 20 minutes, and the entirely of charted space (114 sectors, 44,977 stars) takes 11 hours 15 minutes

