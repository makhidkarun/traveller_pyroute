PyRoute Delta Debugging - Actual Example from its author
--------------------------------------------------------

While setting up the worked example in the delta debugging readme, I discovered what seemed like an actual bug in PyRoute.

The set up is the same as the worked example, but the command line is different (I didn't specify any interesting-related restrictions):

```
python ./PyRoute/DeltaDebug/DeltaDebug.py --min-btn 15 --max-jump 2 --routes trade --borders erode --pop-code scaled --min-dir ./reduced/ --output ./prof-maps/ --sectors ./deltalist.txt --input ./deltasectors/
```

The result wasn't what I was expecting:
```
1 sectors read
Reducing by sector
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
Reduction found: new input has 78 lines and 2 subsectors
# of lines: 78, # of chunks: 2, # of subsectors: 2
Subsector reduction: Attempting chunk 1/2
Subsector reduction: Attempting chunk 2/2
Reduction found: new input has 40 lines and 1 subsectors
Shortest error message: Star Kashmiir (Dagudashaag 0103) duplicated in sector Dagudashaag (-1,0)
Reducing by line
# of lines: 40, # of chunks: 2
Line reduction: Attempting chunk 1/2
Line reduction: Attempting chunk 2/2
# of lines: 40, # of chunks: 4
Line reduction: Attempting chunk 1/4
Line reduction: Attempting chunk 2/4
Reduction found: new input has 30 lines
Widening breach backwards
# of lines: 30
Reduction found: new input has 29 lines
Reduction found: new input has 27 lines
Reduction found: new input has 23 lines
Widening breach complete
Line reduction: Attempting chunk 3/4
Line reduction: Attempting chunk 4/4
Reduction found: new input has 13 lines
Widening breach backwards
# of lines: 13
Reduction found: new input has 13 lines
Reduction found: new input has 12 lines
Widening breach complete
# of lines: 12, # of chunks: 4
Line reduction: Attempting chunk 1/4
Reduction found: new input has 9 lines
Line reduction: Attempting chunk 2/4
Line reduction: Attempting chunk 3/4
Reduction found: new input has 6 lines
Widening breach backwards
# of lines: 6
Reduction found: new input has 5 lines
Reduction found: new input has 4 lines
Widening breach complete
Line reduction: Attempting chunk 4/4
# of lines: 4, # of chunks: 4
Line reduction: Attempting chunk 1/4
Reduction found: new input has 3 lines
Line reduction: Attempting chunk 2/4
Reduction found: new input has 2 lines
Line reduction: Attempting chunk 3/4
Reduction found: new input has 1 lines
Line reduction: Attempting chunk 4/4
# of lines: 1, # of chunks: 1
Line reduction: Attempting chunk 1/1
Shortest error message: float division by zero

Process finished with exit code 0
```

The "float division by zero" was the unexpected bit.

The last three lines of the reduced file were:
```
Hex  Name                 UWP       Remarks                               {Ix}   (Ex)    [Cx]   N    B  Z PBG W  A    Stellar         Routes                                   
---- -------------------- --------- ------------------------------------- ------ ------- ------ ---- -- - --- -- ---- --------------- -----------------------------------------
2123 Kediiga              B778411-8 Ni Pa                                 { -1 } (832-5) [1314] Bc   -  - 920 9  ImDv G6 V
```

Renaming the result from ```Dagudashaag-spieked.sec-min``` to ```Dagudashaag-zero.sec``` and feeding it into plain PyRoute gave:
```
2023-10-19 03:41:49,419 - INFO - starting processing
2023-10-19 03:41:49,420 - INFO - ['/home/alex/gitstuf/traveller_pyroute/deltasectors/Dagudashaag-zero.sec']
2023-10-19 03:41:49,427 - ERROR - Kediiga (Dagudashaag 2123) - Calculated "Ni" not in trade codes []
2023-10-19 03:41:49,427 - ERROR - Kediiga (Dagudashaag 2123)-C778411-8 Calculated "Pa" not in trade codes []
2023-10-19 03:41:49,427 - WARNING - Kediiga (Dagudashaag 2123) - CX Calculated acceptance 3 does not match generated acceptance 2
2023-10-19 03:41:49,430 - INFO - Sector Dagudashaag (-1,0) loaded 1 worlds
2023-10-19 03:41:49,431 - INFO - Total number of worlds: 1
2023-10-19 03:41:49,431 - INFO - 1 sectors read
2023-10-19 03:41:49,431 - INFO - generating jumps...
2023-10-19 03:41:49,432 - INFO - base routes: 0  -  ranges: 0
2023-10-19 03:41:49,432 - INFO - calculating routes...
2023-10-19 03:41:49,432 - INFO - Final route count 0
2023-10-19 03:41:49,432 - INFO - setting borders...
2023-10-19 03:41:49,432 - INFO - Processing worlds for erode map drawing
2023-10-19 03:41:49,443 - INFO - sorting routes...
2023-10-19 03:41:49,445 - INFO - processed 0 routes at BTN 0
2023-10-19 03:41:49,446 - INFO - Processing ETI for worlds
2023-10-19 03:41:49,446 - INFO - Processing TradeGoods for worlds
2023-10-19 03:41:49,450 - INFO - Calculating statistics for 1 worlds
2023-10-19 03:41:49,455 - INFO - Charted star count: 1
2023-10-19 03:41:49,456 - INFO - Charted population 0
Traceback (most recent call last):
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/route.py", line 159, in <module>
    process()
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/route.py", line 123, in process
    stats.write_statistics(args.ally_count, args.ally_match, args.json_data)
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/StatCalculation.py", line 387, in write_statistics
    wiki.write_statistics()
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/wikistats.py", line 53, in write_statistics
    self.sector_statistics_template()
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/wikistats.py", line 86, in sector_statistics_template
    self.output_template('sectors.wiki', 'sectors.wiki',
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/wikistats.py", line 75, in output_template
    f.write(template.render(parameters))
  File "/home/alex/gitstuf/traveller_pyroute/venv2/lib64/pypy3.9/site-packages/jinja2/environment.py", line 1301, in render
    self.environment.handle_exception()
  File "/home/alex/gitstuf/traveller_pyroute/venv2/lib64/pypy3.9/site-packages/jinja2/environment.py", line 936, in handle_exception
    raise rewrite_traceback_stack(source=source)
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/templates/sectors.wiki", line 11, in top-level template code
    {{ stats.stats_table(sector.stats, global_stats) }}
  File "/home/alex/gitstuf/traveller_pyroute/venv2/lib64/pypy3.9/site-packages/jinja2/runtime.py", line 777, in _invoke
    rv = self._func(*arguments)
  File "/home/alex/gitstuf/traveller_pyroute/PyRoute/templates/statistics_table.wiki", line 5, in template
    |align="right"|{{"{:5.2f}".format(stats.population / (global_stats.population / 100.0)) }}%
ZeroDivisionError: float division by zero

Process finished with exit code 1
```

Not only did the error reproduce, we now know where it is.

Where to from here?

The simplest route would be to open an issue on PyRoute, describe what you were doing, and attach the reduced results from
delta debugging.  You've already done a lot by finding the issue, and making it very easy to reproduce.

I've submitted this bug here, to give you an idea of what to put in: https://github.com/makhidkarun/traveller_pyroute/issues/67

The more complex route is continuing to the other side of that coin, which ties into our development process.

Whoever ends up tackling your problem has to:

1.  Take the report and turn it into an automated regression test.  Not only does that tell whoever's fixing your problem that they have actually fixed it, but (more importantly) that if it gets broken later on, we know about it.

I added the minimised Dagudashaag version to ```./Tests/DeltaFiles/stat_calc_division_by_zero_population/Dagudashaag-zero.sec ```.

The regression test, in ```./Tests/Pathfinding/testStatCalcRegression.py``` is:

```
    def testStatsCalcWithZeroPopulation(self):
        sourcefile = self.unpack_filename('DeltaFiles/stat_calc_division_by_zero_population/Dagudashaag-zero.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 2
        args.min_btn = 15

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

        stats = StatCalculation(galaxy)
        stats.calculate_statistics(args.ally_match)
        stats.write_statistics(args.ally_count, args.ally_match, args.json_data)
```

Run the regression test to double-check that it reproduces the problem being tackled.

2.  With regression test in hand, actually investigate and fix your problem.  The regression test gives quick feedback as to whether a supposed fix has actually fixed anything.

In this case, it was a two-line change to ```./PyRoute/templates/statistics_table.wiki```:

```
-|align="right"|{{"{:5.2f}".format(stats.population / (global_stats.population / 100.0)) }}%
+|align="right"|{{"{:5.2f}".format(stats.population / ([global_stats.population, 1]|max / 100.0)) }}%
```

The first line in that block is the original line that contained the division-by-zero bug, and the second is the fixed line.

3.  Re-run your regression test to verify the fix actually works.  Running ```pytest -k {testname}``` from the repo root is what's needed.  

3.  With the tentative fix in hand, run the entire test suite to check that nothing _else_ got broken in the process.
Run ```pytest``` on its own, this time.

4.  Submit a pull request to PyRoute.

Ordinarily I would do this, but I found this bug _while writing the delta debugging docs_, so I've put it in that pull request.
