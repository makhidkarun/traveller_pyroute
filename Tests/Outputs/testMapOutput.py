import logging

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.Map import Map, MapOutput
from Tests.baseTest import baseTest


class testMapOutput(baseTest):
    def test_initial_fonts(self) -> None:
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

    def test_initial_colours(self) -> None:
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

    def test_doc(self) -> None:
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")

        self.assertIsNone(map.doc, "Unexpected doc value")

    def test_output_path(self) -> None:
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")

        self.assertEqual('./', map.output_path, "Unexpected output value")

    def test_logger(self) -> None:
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")
        logger = logging.getLogger('PyRoute.Outputs.MapOutput')

        self.assertEqual(logger, map.logger, "Unexpected logger value")

    def test_image_size(self) -> None:
        galaxy = Galaxy(8)
        map = MapOutput(galaxy, "trade", "./", "writer")
        image_size = Cursor(0, 0)

        self.assertEqual(image_size, map.image_size, "Unexpected image_size value")

    def test_clipping(self) -> None:
        minpos = Cursor(0, 0)
        maxpos = Cursor(300, 300)

        values = [
            ("Outside box", -100, -100, -50, -50, None, None),
            ("Within box", 100, 100, 50, 50, Cursor(100, 100), Cursor(50, 50)),
            ("Crossing boundary down", 100, 100, -50, -50, Cursor(100, 100), Cursor(0, 0)),
            ("Crossing boundary up", 400, 400, 50, 50, Cursor(300, 300), Cursor(50, 50)),
            ("On left boundary", 100, 0, 200, 0, Cursor(100, 0), Cursor(200, 0)),
            ("On right boundary", 100, 300, 200, 300, Cursor(100, 300), Cursor(200, 300)),
            ("On bottom boundary", 0, 100, 0, 200, Cursor(0, 100), Cursor(0, 200)),
            ("On top boundary", 300, 100, 300, 200, Cursor(300, 100), Cursor(300, 200)),
            ("Zero-length within box", 100, 100, 100, 100, Cursor(100, 100), Cursor(100, 100)),
            ("Parallel to box beyond left border", 0, -100, 100, -100, None, None),
            ("Parallel to box beyond bottom border", -100, 0, -100, 100, None, None),
            ("Parallel to box beyond right border", 0, 400, 100, 400, None, None),
            ("Parallel to box beyond top border", 400, 0, 400, 100, None, None),
            ("Parallel to box beyond left border, scaled", 0, -0.1, 0.1, -0.1, None, None),
            ("Parallel to box beyond bottom border, scaled", -0.1, 0, -0.1, 0.1, None, None),
            ("Parallel to box beyond right border, scaled", 0, 300.1, 100, 300.1, None, None),
            ("Parallel to box beyond top border, scaled", 300.1, 0, 300.1, 100, None, None),
        ]

        for msg, start_x, start_y, end_x, end_y, exp_start, exp_finish in values:
            with self.subTest(msg):
                start = Cursor(start_x, start_y)
                end = Cursor(end_x, end_y)

                act_start, act_finish = Map.clipping(minpos, maxpos, start, end)
                self.assertEqual(exp_start, act_start, "Unexpected act_start value")
                self.assertEqual(exp_finish, act_finish, "Unexpected act_finish value")
                if exp_start is not None and exp_finish is not None:
                    self.assertTrue(act_start.x >= minpos.x, "Act_start x value below minpos.x")
                    self.assertTrue(act_finish.x >= minpos.x, "Act_finish x value below minpos.x")
                    self.assertTrue(act_start.y >= minpos.y, "Act_start y value below minpos.y")
                    self.assertTrue(act_finish.y >= minpos.y, "Act_finish y value below minpos.y")
                    self.assertTrue(act_start.x <= maxpos.x, "Act_start x value above maxpos.x")
                    self.assertTrue(act_finish.x <= maxpos.x, "Act_finish x value above maxpos.x")
                    self.assertTrue(act_start.y <= maxpos.y, "Act_start y value above maxpos.y")
                    self.assertTrue(act_finish.y <= maxpos.y, "Act_finish y value above maxpos.y")
