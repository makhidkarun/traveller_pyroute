Delta Debugging for PyRoute
===========================

What is delta debugging?
------------------------
Delta debugging is an approach to shrinking a failure-causing input by removing parts of that input whose presence is accidental - that part didn't cause the failure, it just happened to be in the neighbourhood.

In other words, the input has an essential core, alongside a mass of irrelevant dross.  Delta debugging aims to preserve that essential core, and remove as much of the dross as it can, while still causing the original problem.

Why should I care?
------------------
If you're reading this, you've likely run into some problem with PyRoute, and you'd prefer to see it fixed.

The more effort _you_ put into making your problem simple to understand and, more importantly, reproduce, the more likely it is to be fixed in the first place, fixed _correctly_, and _stay fixed_.

To help you simplify your problem by handling most of the heavy lifting, enter delta debugging, stage left.

Reducing the sheer size of your failure-causing input doesn't bog down the person fixing it with (quite as much) irrelevant stuff.

For example, one of PyRoute's major contributors, Alex Goodwin, has found digging through Dagudashaag's entirety (558 stars) in pursuit of a bug to be too difficult.  A shrunken 16-star Dagudashaag, on the other end, is no problem.

A reduced-size test case also helps identify (semi-)duplicate reported bugs, by making it more obvious those reports are different facets of the same underlying problem.

How is delta debugging being applied here, and what problem is it solving?
-----------------
PyRoute's version of delta debugging takes a list of input sectors, a definition of the problem, and automates the grunt work of reducing the input's size by:

- Discarding irrelevant sectors completely
- Discarding irrelevant subsectors
- Discarding irrelevant star systems

This default setting works reasonably well - in the worked example below, starting with Zarushagar and a broken copy of Dagudashaag (approx 1050 stars in total), those default settings reduced the input to 1 sector file (Dagudashaag) with only 2 star systems in it.

There are three extra, currently-experimental, passes available:
- Discarding irrelevant allegiances (runs after sector discard)
- Discarding irrelevant _pairs_ (not merely adjacent pairs) of star systems (runs after single-system discard)
- Discarding irrelevant _portions_ (eg trade codes, high/low TL) of a given star system (runs after double-system discard)

You might need one or more of these experimental passes if your particular problem doesn't reduce well with the standard ones.

How do I run it?
----------------
Invoking DeltaDebug.py with the --help parameter gives:

```
usage: DeltaDebug.py [-h] [--borders {none,range,allygen,erode}]
                     [--ally-match {collapse,separate}]
                     [--routes {trade,comm,xroute,owned,none}] [--min-btn BTN]
                     [--min-route-btn ROUTE_BTN] [--max-jump MAX_JUMP]
                     [--pop-code {fixed,scaled,benford}]
                     [--route-reuse ROUTE_REUSE] [--ru-calc {scaled,negative}]
                     [--speculative-version {CT,T5,None}]
                     [--mp-threads MP_THREADS] [--output OUTPUT]
                     [--owned-worlds] [--no-trade] [--no-maps]
                     [--no-subsector-maps] [--min-ally-count ALLY_COUNT]
                     [--json-data] [--debug] [--input INPUT]
                     [--sectors SECTORS] [--output-dir OUTPUTDIR]
                     [--min-dir MINDIR] [--interesting-line INTERESTINGLINE]
                     [--interesting-type INTERESTINGTYPE] [--two-minimise]
                     [--no-sector] [--no-subsector] [--no-line]
                     [--within-line] [--allegiance] [--assume-interesting]
                     [sector ...]

PyRoute input minimiser.

optional arguments:
  -h, --help            show this help message and exit

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
  --mp-threads MP_THREADS
                        Number of processes to use for trade-mp processing,
                        default 3

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

Debug:
  Debugging flags

  --debug               Turn on trade-route debugging

Debugging:
  Parameters for the delta-debugging procedure itself

  --input INPUT         input directory for sectors
  --sectors SECTORS     file with list of sector names to process
  sector                T5SS sector file(s) to process
  --output-dir OUTPUTDIR
                        Output folder to place any maps generated during
                        minimisation.
  --min-dir MINDIR      Output folder to place minimised sector files
                        generated during minimisation.
  --interesting-line INTERESTINGLINE
                        Line required to classify run output as interesting
  --interesting-type INTERESTINGTYPE
                        Exception type required to classify run output as
                        interesting
  --two-minimise        Try all pairs of star lines to see if any can be
                        removed
  --no-sector           Skip sector-level reduction
  --no-subsector        Skip subsector-level reduction
  --no-line             Skip line-level reduction. At least one of sector,
                        subsector, line and two-minimisation must be selected
  --within-line         Try to remove irrelevant components (eg base codes)
                        from _within_ individual lines
  --allegiance          Try to remove irrelevant allegiances
  --assume-interesting  Assume initial input is interesting.
```

The parameters outside the debugging section are passed through to the PyRoute engine, so we'll skip over them here.

The debugging parameters control delta debugging itself.

First, the mundane path parameters:

```--input``` tells DeltaDebug where your input sector files (that you want to reduce) are stored.

```--output-dir``` tells DeltaDebug where to place any PyRoute-generated output that might be generated.

```--min-dir``` tells DeltaDebug where to place the final, reduced, files after it's done its job.  The output files
will have ```-min``` appended to them - eg ```Zhdant.sec``` would become, after reduction, ```Zhdant.sec-min```.

Second, the interesting parameters:

```--interesting-line``` contains the string that must appear _somewhere_ in an error message for it to count as "interesting".

```--interesting-type``` contains the exception type that must occur for an error to count as "interesting".

You don't have to set either of these - the default case is to treat _any_ and _all_ python errors and exceptions as interesting.

However, if you're trying to isolate, say, a NullReferenceException, then it's a fair assumption that, right now, you
don't care about AssertionErrors, NotImplementedErrors, etc.  In this case, supplying 
```--interesting-type NullReferenceException``` on the command line will focus DeltaDebug where you want.

Likewise, if your run blows up with the error message "This route from Arglebargle to Bargleargle has already been processed",
supplying ```--interesting-line "This route from Arglebargle to Bargleargle has already been processed"``` will focus
delta debugging on that _specific_ route being processed twice, or using ```--interesting-line " has already been processed"```
if you want delta debugging to chase down _any_ route being processed twice, no matter the source or destination.

Third, the reduction passes themselves, which fall into two groups:

Non-experimental, on by default, in their running order:

```--no-sector``` :  Disable sector-level reduction.  Sectors are the coarsest reduction units used, with finer-grained
reductions (eg subsector, line, etc) intended to happen _after_ coarser passes have run.

You can definitely skip sector level reduction, but it's not a good idea on your first attempt to reduce a given
problem's input.

This will have no effect if you are reducing exactly one sector file.

```--no-subsector``` :  Disable subsector-level reduction.  Subsectors are the second-coarsest reduction units
routinely used.

Like with sector level reduction, it's not a good idea to skip subsector reduction on your first attempt reducing a given
problem's input.

This will have no effect if you are reducing exactly one sector file with stars in exactly one subsector.

```--no-line``` :  Disable single-starline-level reduction.  Starlines are the finest reduction units routinely used.

Leaving sector and subsector reduction enabled while disabling single-line reduction often results in a reasonable
first, rough, reduction that can either be manually investigated further, or fed back in to a full reduction.

Experimental, off by default:

```--allegiance``` :  Enable allegiance-level reduction, running between sector and subsector reduction.

Sub-allegiances - such as "ImDd" and "ImDv" - are counted as different from both each other, and the parent "Im"
allegiance for this pass.

Allegiances vary in coarseness - "ImDs" ranges across multiple sectors (let alone the various non-aligned allegiances),
but (for instance) "Sb" (Serendip Belt) is limited to two systems in Reft sector.

```--two-reduce``` :  Enable double-starline-level reduction, running after single-line reduction.

It is a _really_ daft idea to run just this pass on 1 or more un-reduced sectors, as the number of reduction attempts
is quadratic in the number of total star lines in the input.

For instance, running just this pass on Dagudashaag (558 stars) could result, worst case, in approx 155,400 reduction
attempts.

Two-minimisation, as its name suggests, looks for any combinations of _two_ starlines that can be removed from the
current input, which can often enable further reductions after single-line reduction has stalled.

```--within-line``` : Enable within-line reduction, running after double-line reduction.

Unlike the other passes, this pass concentrates on removing elements _within_ a given starline - in effect, simplifying
each starline.

For example:

```"0627 Taku                 AA676AD-C Ag Ni Ri Cp Da            { 4 }  (B58+5) [AA9G] BCF  NS A 912 14 ImDa K1 V M1 V      Xb:0524 Xb:1029"```

could get shrunk to (dropping capitals, other trade codes, nobles, bases, and setting PBG back to 100):

```0627 Taku                 AA676AD-C                                       { 1 }  (B58+5) [AA9G]      -  - 100 14 ImDa K1 V           Xb:0524 Xb:1029                          ```


What does it do?
----------------
That might be a lot to take in.  It's time for a simple worked example.

We'll be using the following pathfinding settings:
- min-btn: 15
- max-jump: 2
- routes: trade
- borders: erode
- pop-code: scaled
- input: ./deltasectors
- output: ./deltamaps
- no-subsector-maps

All paths will be relative to the repo root directory.

1.  Create the ```./deltasectors``` directory.
2.  Copy the ```./Tests/DeltaFiles/Dagudashaag-spiked.sec``` and ```./Tests/DeltaFiles/Zarushagar.sec``` files to ```./deltasectors/```.
3.  Create the ```./deltalist.txt``` file and add ```Dagudashaag-spiked``` and ```Zarushagar``` to it, on separate lines.
4.  From the repo root, run ```python ./PyRoute/route.py --min-btn 15 --max-jump 2 --routes trade --borders erode --pop-code scaled --input ./deltasectors --output ./deltamaps --sectors ./deltalist.txt --no-subsector-maps```

You should rapidly get something like the following:
```
2023-10-19 01:51:49,608 - INFO - starting processing
2023-10-19 01:51:49,609 - INFO - ['/home/alex/gitstuf/traveller_pyroute/deltasectors/Zarushagar.sec', '/home/alex/gitstuf/traveller_pyroute/deltasectors/Dagudashaag-spiked.sec']
2023-10-19 01:51:52,086 - INFO - Sector Zarushagar (-1,-1) loaded 496 worlds
Traceback (most recent call last):
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/route.py", line 159, in <module>
    process()
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/route.py", line 100, in process
    galaxy.read_sectors(sectors_list, args.pop_code, args.ru_calc,
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/Galaxy.py", line 320, in read_sectors
    assert star not in sec.worlds, "Star " + str(star) + " duplicated in sector " + str(sec)
AssertionError: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)

```

You'll need somewhere to _store_ the reduced sector files.  For this pass, you'll just be using the default settings.

1.  Create the ```./reduced``` directory.
2.  Run delta debugging from the repo root: ```python ./PyRoute/DeltaDebug/DeltaDebug.py --min-btn 15 --max-jump 4 --routes trade --borders erode --pop-code scaled --min-dir ./reduced/ --output ./prof-maps/ --sectors ./deltalist.txt --input ./deltasectors/ --interesting-line=duplicated```

The output will take longer this time, and _be_ longer.  Something like:

```
2 sectors read
Reducing by sector
# of lines: 1057, # of chunks: 2, # of sectors: 2
Sector reduction: Attempting chunk 1/2
Sector reduction: Attempting chunk 2/2
Reduction found: new input has 561 lines and 1 sectors
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)
Reducing by subsector
# of lines: 561, # of chunks: 2, # of subsectors: 16
Subsector reduction: Attempting chunk 1/2
Reduction found: new input has 293 lines and 8 subsectors
# of lines: 293, # of chunks: 2, # of subsectors: 8
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 147 lines and 4 subsectors
# of lines: 147, # of chunks: 2, # of subsectors: 4
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 69 lines and 2 subsectors
# of lines: 69, # of chunks: 2, # of subsectors: 2
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 37 lines and 1 subsectors
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)
Reducing by line
# of lines: 37, # of chunks: 2
Line reduction: Attempting chunk 1/2
Line reduction: Attempting chunk 2/2
# of lines: 37, # of chunks: 4
Line reduction: Attempting chunk 1/4
Line reduction: Attempting chunk 2/4
Reduction found: new input has 27 lines
Widening breach backwards
# of lines: 27
Reduction found: new input has 26 lines
Reduction found: new input has 24 lines
Reduction found: new input has 20 lines
Reduction found: new input has 12 lines
Reduction found: new input has 8 lines
Widening breach complete
Line reduction: Attempting chunk 3/4
Reduction found: new input has 5 lines
Widening breach backwards
# of lines: 5
Reduction found: new input has 5 lines
Widening breach complete
Line reduction: Attempting chunk 4/4
# of lines: 5, # of chunks: 4
Line reduction: Attempting chunk 1/4
Line reduction: Attempting chunk 2/4
Reduction found: new input has 3 lines
Widening breach backwards
# of lines: 3
Reduction found: new input has 2 lines
Widening breach complete
Line reduction: Attempting chunk 3/4
# of lines: 2, # of chunks: 2
Line reduction: Attempting chunk 1/2
Line reduction: Attempting chunk 2/2
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)

Process finished with exit code 0
```

After that's done, you should have one file in ```./reduced```, namely ```Dagudashaag-spiked.sec-min```.

The last few lines of that file should be:
```
Hex  Name                 UWP       Remarks                               {Ix}   (Ex)    [Cx]   N    B  Z PBG W  A    Stellar         Routes                                   
---- -------------------- --------- ------------------------------------- ------ ------- ------ ---- -- - --- -- ---- --------------- -----------------------------------------
0103 Kashmiir             A9687BB-C Ag Ri Cp Pz                           { 4 }  (D6E+5) [9B7E] BCF  N  A 313 10 ImDv M1 V M2 V
0103 Kashmiir             A9687BB-C Ag Ri Cp Pz                           { 4 }  (D6E+5) [9B7E] BCF  N  A 313 10 ImDv M1 V M2 V
```

This is a somewhat simplified example, but the general result should be clear.

Instead of having 1,057 starlines to wade through over 2 sectors, you now have 2 starlines in 1 sector - approx 500x less to look through. 

If you want to keep that file, copy it somewhere.  Let's now do a second run, but this time skipping single-line reduction and enabling within-line reduction.

The command line you will need is:
```python ./PyRoute/DeltaDebug/DeltaDebug.py --min-btn 15 --max-jump 4 --routes trade --borders erode --pop-code scaled --min-dir ./reduced/ --output ./prof-maps/ --sectors ./deltalist.txt --input ./deltasectors/ --interesting-line=duplicated --no-line --within-line```

That will result in something like the following output:
```
2 sectors read
Reducing by sector
# of lines: 1057, # of chunks: 2, # of sectors: 2
Sector reduction: Attempting chunk 1/2
Sector reduction: Attempting chunk 2/2
Reduction found: new input has 561 lines and 1 sectors
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)
Reducing by subsector
# of lines: 561, # of chunks: 2, # of subsectors: 16
Subsector reduction: Attempting chunk 1/2
Reduction found: new input has 293 lines and 8 subsectors
# of lines: 293, # of chunks: 2, # of subsectors: 8
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 147 lines and 4 subsectors
# of lines: 147, # of chunks: 2, # of subsectors: 4
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 69 lines and 2 subsectors
# of lines: 69, # of chunks: 2, # of subsectors: 2
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 37 lines and 1 subsectors
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)
Reducing within lines
Reduction found with full canonicalisation
Commencing full within-line reduction
start - # of unreduced lines: 37
Reduction found with full line reduction

Process finished with exit code 0
```

The resulting file should have these lines at its end:
```
Hex  Name                 UWP       Remarks                               {Ix}   (Ex)    [Cx]   N    B  Z PBG W  A    Stellar         Routes                                   
---- -------------------- --------- ------------------------------------- ------ ------- ------ ---- -- - --- -- ---- --------------- -----------------------------------------
0103 Kashmiir             C9687BB-8                                       { -1 } (D6E+5) [9B7E]      -  - 100 1  ImDv M1 V
0105 Kedaa                C551410-8                                       { -2 } (834-3) [1515]      -  - 100 1  ImLc M0 V
0106 Akimu                C9B69CC-8                                       { 0 }  (E8C+5) [CB8C]      -  - 100 1  ImLc K9 V
0108 Zukchurukh           C582867-8                                       { -1 } (G78+1) [8858]      -  - 100 1  ImLc M2 V
0109 Tscho                C685767-8                                       { -1 } (D69+1) [7858]      -  - 100 1  ImLc K2 V
0110 Kaza                 C542510-8                                       { -2 } (D43-5) [1414]      -  - 100 1  ImLc G4 V
0201 Nuikh                C310200-8                                       { -2 } (511-3) [131A]      -  - 100 1  ImDv K9 V
0202 Osakis               C675723-8                                       { -1 } (966-4) [4623]      -  - 100 1  ImDv M2 V
0208 Mimu                 C583AC9-8                                       { 0 }  (H9F+4) [BD6G]      -  - 100 1  ImLc F8 V
0210 Rathas               C95A8DB-8                                       { -1 } (D7C+4) [AA7D]      -  - 100 1  ImLc M2 V
0301 Halimaa              C6B85AA-8                                       { -2 } (A41-1) [727A]      -  - 100 1  ImDv F7 V
0302 Karrana'ch           C555541-8                                       { -2 } (A44-4) [1515]      -  - 100 1  ImDv M0 V
0307 Manoh                C000667-8                                       { -2 } (C54+1) [665A]      -  - 100 1  ImLc M7 V
0401 Ges                  C868431-8                                       { -2 } (631-5) [1111]      -  - 100 1  ImDv G4 V
0402 Serpent's Reach      C66975A-8                                       { -1 } (E6E+5) [9A7G]      -  - 100 1  ImDv K1 V
0405 Tree'chuakh          C789753-8                                       { -1 } (A6D+1) [4A29]      -  - 100 1  ImLc M1 V
0406 Muikha               C000524-8                                       { -2 } (B45-1) [363C]      -  - 100 1  ImLc K4 V
0407 Kaldi                C94736B-8                                       { -2 } (920+1) [517A]      -  - 100 1  ImLc M0 V
0408 Tae                  C552664-8                                       { -2 } (C52-4) [4436]      -  - 100 1  ImLc K0 V
0502 Ushkhuur             CA7A774-8                                       { -1 } (A69-2) [5737]      -  - 100 1  ImDv G2 V
0503 Geka                 C311553-8                                       { -2 } (B43-4) [2427]      -  - 100 1  ImDv M9 III
0504 Gushnemasha          C888778-8                                       { -1 } (967+1) [7756]      -  - 100 1  ImLc M2 V
0505 Iiu                  C5A689B-8                                       { -1 } (C7B+4) [AA7C]      -  - 100 1  ImLc M4 V
0506 Siakmasfa            C540233-8                                       { -2 } (811-2) [132A]      -  - 100 1  ImLc K2 V
0509 Refuge               C578664-8                                       { -2 } (852-4) [4433]      -  - 100 1  ImLc K1 V
0601 Ninaan               C544543-8                                       { -2 } (F44-3) [2526]      -  - 100 1  ImDv M1 V
0604 Seminary             C422425-8                                       { -2 } (633-2) [2439]      -  - 100 1  ImLc M1 V
0610 Zishku               C7A5776-8                                       { -1 } (F69-1) [6748]      -  - 100 1  ImDv K0 V
0705 Zuiar                C550967-8                                       { 0 }  (G8E+3) [9C5C]      -  - 100 1  ImLc K0 V
0707 Khumara              C561520-8                                       { -2 } (741-5) [1212]      -  - 100 1  ImLc M1 V
0708 Ssi                  C75886A-8                                       { -1 } (D7C+4) [AA7E]      -  - 100 1  ImLc K6 V
0709 Irshe                C94A100-8                                       { -2 } (701-3) [1218]      -  - 100 1  ImLc M2 V
0801 Shéaniki             C612521-8                                       { -2 } (742-5) [1313]      -  - 100 1  ImDv M2 V
0802 Khan                 C89A5A9-8                                       { -2 } (742-1) [6368]      -  - 100 1  ImLc K2 V
0803 Chiauk               C431557-8                                       { -2 } (A45+1) [565F]      -  - 100 1  ImLc M2 V
0810 Andalusia            C572348-8                                       { -2 } (521+1) [345B]      -  - 100 1  ImDv G4 V
0103 Kashmiir             C9687BB-8                                       { -1 } (D6E+5) [9B7E]      -  - 100 1  ImDv M1 V
```

In this run, note how a lot of the within-line stuff (trade codes, base codes, noble codes, etc) was _shown_ to be irrelevant.

What do I do with the result?
---------
