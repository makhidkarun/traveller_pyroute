import unittest
from PyRoute.Outputs.Map import Map
from PyRoute.Outputs.Cursor import Cursor


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.min_pos = Cursor(25, 25)
        self.max_pos = Cursor(100, 100)

    def test_internal(self) -> None:
        start = Cursor(30, 30)
        end = Cursor(75, 75)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)

        self.assertEqual(start, clip_start)
        self.assertEqual(end, clip_end)

    def test_external(self) -> None:
        start = Cursor(0, 0)
        end = Cursor(10, 10)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)

        self.assertIsNone(clip_start)
        self.assertIsNone(clip_end)

    def test_top_line(self) -> None:
        start = Cursor(30, 25)
        end = Cursor(50, 25)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)
        self.assertEqual(start, clip_start)
        self.assertEqual(end, clip_end)

    def test_top_clip(self) -> None:
        start = Cursor(30, 20)
        end = Cursor(50, 50)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)
        self.assertEqual(int(clip_start.x), 33)
        self.assertEqual(clip_start.y, 25)
        self.assertEqual(clip_end.x, 50)
        self.assertEqual(clip_end.y, 50)

    def test_right_clip(self) -> None:
        start = Cursor(150, 40)
        end = Cursor(50, 50)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)
        self.assertEqual(int(clip_start.x), 100)
        self.assertEqual(clip_start.y, 45)
        self.assertEqual(clip_end.x, 50)
        self.assertEqual(clip_end.y, 50)

    def test_left_clip(self) -> None:
        start = Cursor(15, 40)
        end = Cursor(50, 50)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)
        self.assertEqual(int(clip_start.x), 25)
        self.assertEqual(int(clip_start.y), 42)
        self.assertEqual(clip_end.x, 50)
        self.assertEqual(clip_end.y, 50)

    def test_bottom_clip(self) -> None:
        start = Cursor(45, 150)
        end = Cursor(50, 50)
        clip_start, clip_end = Map.clipping(self.min_pos, self.max_pos, start, end)
        self.assertEqual(int(clip_start.x), 47)
        self.assertEqual(int(clip_start.y), 100)
        self.assertEqual(clip_end.x, 50)
        self.assertEqual(clip_end.y, 50)


if __name__ == '__main__':
    unittest.main()
