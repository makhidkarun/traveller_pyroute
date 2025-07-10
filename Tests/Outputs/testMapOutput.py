from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.Map import Map, MapOutput
from Tests.baseTest import baseTest


class testMapOutput(baseTest):
    def test_initial_fonts(self):
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")

        expectedFonts = {
            'title': None,
            'info': None,
            'sector': None,
            'system_port': None,
            'system_uwp': None,
            'system_name': None,
            'base code': None
        }
        self.assertEqual(expectedFonts, map.fonts, "Unexpected font setting")

    def test_initial_colours(self):
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")

        expectedColours = {
            'background': None,
            'title': None,
            'info': None,
            'sector': None,
            'system_port': None,
            'system_uwp': None,
            'system_name': None,
            'base code': None,

            'grid': None,
            'hexes': None,
            'red zone': None,
            'amber zone': None,
            'gg refuel': None,
            'wild refuel': None,
            'comm': None,
        }
        self.assertEqual(expectedColours, map.colours, "Unexpected font setting")

    def test_doc(self):
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")

        self.assertIsNone(map.doc, "Unexpected doc value")

    def test_clipping(self):
        minpos = Cursor(0, 0)
        maxpos = Cursor(300, 300)

        values = [
            (-100, -100, -50, -50, None, None),
            (100, 100, 50, 50, Cursor(100, 100), Cursor(50, 50)),
            (100, 100, -50, -50, Cursor(100, 100), Cursor(0, 0)),
            (400, 400, 50, 50, Cursor(300, 300), Cursor(50, 50)),
            (100, 0, 200, 0, Cursor(100, 0), Cursor(200, 0)),
            (100, 300, 200, 300, Cursor(100, 300), Cursor(200, 300)),
            (0, 100, 0, 200, Cursor(0, 100), Cursor(0, 200)),
            (300, 100, 300, 200, Cursor(300, 100), Cursor(300, 200)),
            (100, 100, 100, 100, Cursor(100, 100), Cursor(100, 100))
        ]

        for start_x, start_y, end_x, end_y, exp_start, exp_finish in values:
            with self.subTest():
                start = Cursor(start_x, start_y)
                end = Cursor(end_x, end_y)

                act_start, act_finish = Map.clipping(minpos, maxpos, start, end)
                self.assertEqual(exp_start, act_start, "Unexpected act_start value")
                self.assertEqual(exp_finish, act_finish, "Unexpected act_finish value")
