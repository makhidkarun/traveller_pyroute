PyRoute for Traveller
=====================

PyRoute is a trade route generation program for Traveller.

The data for the maps comes from [Traveller Map](http://www.travellermap.com/),based upon the Traveller 5th edition second survey data, plus many of the fan created sectors from aound the internet and across the years.

The trade rules are from [GURPS Traveller: Far trader](http://www.sjgames.com/traveller/fartrader/). These rules are based upon the idea of a gravity trade model. Each world is given a weight,called the World Trade Number (WTN) based upon population, starport, and other factors. For each pair of worlds, a Bilateral Trade (BTN) number is calculated based upon the two WTNs, and adjusted for distance and other factors. 

The routes followed for trade are created by the shortest path algorithms from [NetworkX](http://networkx.github.io/), a library for managing graphs. 

The final output of the generation is created by [PyPDFLite](https://github.com/katerina7479/pypdflite). You will need version 0.1.22 or later to include the ellipse and text rotation features. 


For the math and layout of hex maps, I recommend the [Hexagonal Grids](http://www.redblobgames.com/grids/hexagons/) page, which contains every item you will need to draw and manage hexagon maps.I recommend all the articles on the Red Blob Games site.

The original version of this program, [nroute.c](http://wiki.travellerrpg.com/Nroute.c), was written by Anthony Jackson. 
