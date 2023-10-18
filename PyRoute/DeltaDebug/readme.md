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


What do I do with the result?
---------
