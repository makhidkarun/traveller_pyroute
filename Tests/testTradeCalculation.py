import unittest
import re
import sys

sys.path.append('../PyRoute')
from Star import Star
from Galaxy import Sector, Galaxy
from TradeCalculation import TradeCalculation


class testTradeCalculation(unittest.TestCase):
    def test_negative_route_weight_trips_assertion(self):
        expected = 'Weight of edge between Irkigkhan (Core 0103) and Irkigkhan (Core 0103) must be positive'
        actual = None
        try:
            sector = Sector(' Core', ' 0, 0')
            star1 = Star.parse_line_into_star(
                "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                sector, 'fixed', 'fixed')

            galaxy = Galaxy(min_btn=13)
            tradecalc = TradeCalculation(galaxy)

            tradecalc.route_weight(star1, star1)
        except AssertionError as e:
            actual = str(e)
            pass

        self.assertEqual(expected, actual)

    def test_zero_route_weight_trips_assertion(self):
        expected = 'Weight of edge between Irkigkhan (Core 0103) and Irkigkhan (Core 0103) must be positive'
        actual = None
        try:
            sector = Sector(' Core', ' 0, 0')
            star1 = Star.parse_line_into_star(
                "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                sector, 'fixed', 'fixed')
            star1.importance = 0

            galaxy = Galaxy(min_btn=13)
            tradecalc = TradeCalculation(galaxy)

            tradecalc.route_weight(star1, star1)
        except AssertionError as e:
            actual = str(e)
            pass

        self.assertEqual(expected, actual)

    def test_positive_route_weight_doesnt_trip_assertion(self):
            sector = Sector(' Core', ' 0, 0')
            star1 = Star.parse_line_into_star(
                "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                sector, 'fixed', 'fixed')
            star1.importance = -1

            galaxy = Galaxy(min_btn=13)
            tradecalc = TradeCalculation(galaxy)

            self.assertEqual(2, tradecalc.route_weight(star1, star1))

    def test_single_link_route_weight(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

        galaxy = Galaxy(min_btn=13)
        tradecalc = TradeCalculation(galaxy)

        route = [star1, star2]
        galaxy.stars.add_node(star1)
        galaxy.stars.add_node(star2)
        galaxy.ranges.add_node(star1)
        galaxy.ranges.add_node(star2)
        galaxy.stars.add_edge(star1, star2, distance=1,
                              weight=10, trade=0, btn=10, count=0)

        expected_weight = 10
        actual_weight = tradecalc.route_cost(route)
        self.assertEqual(expected_weight, actual_weight, "Route cost unexpected")

if __name__ == '__main__':
    unittest.main()
