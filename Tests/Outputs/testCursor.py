
import unittest

from PyRoute.Outputs.Cursor import Cursor


class TestCursor(unittest.TestCase):

    def testSimple(self):
        cursor = Cursor(0, 0)
        self.assertEqual(cursor.x, 0)
        self.assertEqual(cursor.y, 0)

    def testdx(self):
        cursor = Cursor(1, 1)
        cursor.x_plus()
        self.assertEqual(cursor.x, 1)
        cursor.x_plus(1)
        self.assertEqual(cursor.x, 2)

    def testdy(self):
        cursor = Cursor(1, 1)
        cursor.y_plus()
        self.assertEqual(cursor.y, 1)
        cursor.y_plus(1)
        self.assertEqual(cursor.y, 2)

    def testSetDeltas(self):
        cursor = Cursor(1, 1)
        cursor.set_deltas()
        cursor.x_plus()
        self.assertEqual(cursor.x, 3)
        self.assertEqual(cursor.y, 1)
        cursor.y_plus()
        self.assertEqual(cursor.x, 3)
        self.assertEqual(cursor.y, 3)

    def testSetDeltaOverride(self):
        cursor = Cursor(1, 1)
        cursor.set_deltas(4, 4)
        cursor.x_plus()
        self.assertEqual(cursor.x, 5)
        self.assertEqual(cursor.y, 1)
        cursor.y_plus()
        self.assertEqual(cursor.x, 5)
        self.assertEqual(cursor.y, 5)

    def testString(self):
        cursor = Cursor(1, 1)
        self.assertEqual(str(cursor), "1, 1")

    def testEquals(self):
        cursor1 = Cursor(1, 1)
        cursor2 = Cursor(3, 3)
        self.assertFalse(cursor2 == cursor1)
        cursor1.x_plus(2)
        cursor1.y_plus(2)
        self.assertTrue(cursor2 == cursor1)

    def testAssignValues(self):
        cursor = Cursor(1, 1)
        cursor.x = -1
        self.assertEqual(cursor.x, -1)
        self.assertEqual(cursor.y, 1)
        cursor.y = -3
        self.assertEqual(cursor.x, -1)
        self.assertEqual(cursor.y, -3)

    def testCopy(self):
        cursor = Cursor(1, 1)
        cursor_new = cursor.copy()

        self.assertTrue(cursor == cursor_new)


if __name__ == "__main__":
    unittest.main()
