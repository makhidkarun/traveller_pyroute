"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
from PyRoute import Star
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Utilities.NoNoneDefaultDict import NoNoneDefaultDict
from PyRoute.StatCalculation.Populations import Populations
from PyRoute.StatCalculation.ObjectStatistics import ObjectStatistics
from Tests.baseTest import baseTest


class testObjectStatistics(baseTest):

    def test_init(self) -> None:
        stats = ObjectStatistics()
        notint = [
            'populations', 'maxPort', 'port_size', 'code_counts', 'bases', 'star_count', 'primary_count', 'homeworlds',
            'high_pop_worlds', 'high_tech_worlds', 'subsectorCp', 'sectorCp', 'otherCp', '__dict__'
        ]
        brackets = [
            'homeworlds', 'high_pop_worlds', 'high_tech_worlds', 'subsectorCp', 'sectorCp', 'otherCp'
        ]
        self.assertEqual({}, stats.__getitem__('__dict__'))
        for key in ObjectStatistics.__slots__:
            if key in notint:
                if key in brackets:
                    value = stats.__getitem__(key)
                    self.assertIsNotNone(value, key)
                    self.assertEqual([], value, key)
                continue
            value = stats.__getitem__(key)
            self.assertIsNotNone(value, key)
            self.assertEqual(0, value, key)

    def test_hash(self) -> None:
        stats = ObjectStatistics()
        self.assertEqual(0, stats.__hash__())

    def test_getstate(self) -> None:
        stats = ObjectStatistics()
        exp_dict = {
            'TLmean': 0,
            'TLstddev': 0,
            '__dict__': {},
            'bases': NoNoneDefaultDict(int),
            'code_counts': NoNoneDefaultDict(int),
            'col_be': 0,
            'economy': 0,
            'eti_cargo': 0,
            'eti_pass': 0,
            'eti_worlds': 0,
            'gg_count': 0,
            'im_be': 0,
            'maxPop': 0,
            'maxPort': 'X',
            'maxTL': 0,
            'milBudget': 0,
            'number': 0,
            'passengers': 0,
            'percapita': 0,
            'population': 0,
            'populations': NoNoneDefaultDict(Populations),
            'port_size': NoNoneDefaultDict(int),
            'primary_count': NoNoneDefaultDict(int),
            'shipyards': 0,
            'spa_people': 0,
            'star_count': NoNoneDefaultDict(int),
            'stars': 0,
            'sum_ru': 0,
            'trade': 0,
            'tradeDton': 0,
            'tradeDtonExt': 0,
            'tradeExt': 0,
            'tradeVol': 0,
            'worlds': 0
        }
        self.assertEqual(exp_dict, stats.__getstate__())

    def test_hi_pop_worlds(self) -> None:
        sector = Sector("# Core", "# 0,0")
        star = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        stats = ObjectStatistics()
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        stats.high_pop_worlds.append(star)
        self.assertEqual(7, stats.high_pop_worlds_count())
        self.assertEqual(['{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}',
                          '{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}',
                          '{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}'],
                         stats.high_pop_worlds_list())

    def test_hi_tech_worlds(self) -> None:
        sector = Sector("# Core", "# 0,0")
        star = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        stats = ObjectStatistics()
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        stats.high_tech_worlds.append(star)
        self.assertEqual(7, stats.high_tech_worlds_count())
        self.assertEqual(['{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}',
                          '{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}',
                          '{{WorldS|Irkigkhan|Core|0103}}', '{{WorldS|Irkigkhan|Core|0103}}'],
                         stats.high_tech_worlds_list())

    def test_blank_eq(self) -> None:
        stats1 = ObjectStatistics()
        stats2 = ObjectStatistics()
        self.assertEqual(stats1, stats2)

    def test_non_object_stats_eq(self) -> None:
        stats1 = ObjectStatistics()
        stats2 = 42
        self.assertNotEqual(stats1, stats2)

    def test_equality_deep_dive(self) -> None:
        cases = (
            'maxTL', 'TLmean', 'TLstddev', 'maxPop', 'maxPort', 'trade', 'tradeExt', 'tradeDton', 'tradeDtonExt',
            'tradeVol'
        )

        for item in cases:
            with self.subTest(item):
                value = 'C' if 'maxPort' == item else 2
                stats1 = ObjectStatistics()
                stats2 = ObjectStatistics()
                stats2[item] = value
                self.assertNotEqual(stats1, stats2, item)

    def test_setitem(self) -> None:
        stats = ObjectStatistics()
        stats.__setitem__('foo', 'bar')
        self.assertEqual('bar', stats.__getitem__('foo'))

    def test_deepcopy(self) -> None:
        stats1 = ObjectStatistics()
        stats1.__setitem__('__dict__', {'bar': 'foo'})
        stats2 = stats1.__deepcopy__()
        self.assertEqual(stats1['bar'], stats2['bar'])
