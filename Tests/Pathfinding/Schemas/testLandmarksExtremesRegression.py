"""
Created on 05 Sep, 2024

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes
from Tests.baseTest import baseTest


class testLandmarksExtremesRegression(baseTest):

    def testZeroArgsInTransposeLandmarks(self):
        sourcefile = self.unpack_filename('../DeltaFiles/zero_arg_in_transpose_landmarks/Bar\'kakr.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True)]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        foo = LandmarksTriaxialExtremes(galaxy)
        expected = [
            {0: 56}, {0: 95}, {0: 43}, {0: 59}, {0: 0}, {0: 68}, {}
        ]
        actual, _ = foo.get_landmarks(index=True, btn=btn)
        self.assertEqual(expected, actual)
