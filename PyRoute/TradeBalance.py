import functools
from math import ceil

from PyRoute.Star import Star


class TradeBalance(dict):

    def __init__(self, stat_field=None, region=None, target="passenger", field="sectors", star_field="sector"):
        assert isinstance(stat_field, str), "Stat_field must be a string"
        from PyRoute.Galaxy import Galaxy
        assert isinstance(type(region), type(Galaxy)), "Region must be an Galaxy"
        assert isinstance(target, str)
        assert isinstance(field, str), "Target field must be a string"
        super().__init__()
        self.stat_field = stat_field
        self.region = region
        self.target = target
        self.field = field
        self.star_field = star_field
        pass

    def update(self, __m, **kwargs):
        for key in __m:
            self._check(key, __m[key])
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        self._check(item, value)
        super().__setitem__(item, value)

    def log_odd_unit(self, star: Star, target: Star):
        sector_tuple = self._balance_tuple(star[self.star_field].name, target[self.star_field].name)
        if sector_tuple not in self:
            self[sector_tuple] = 0
        self[sector_tuple] += 1
        if 1 < self[sector_tuple]:
            star[self.star_field].stats[self.stat_field] += 1
            target[self.star_field].stats[self.stat_field] += 1
            self[sector_tuple] -= 2

    def single_unit_imbalance(self):
        sector_balance = dict()

        for key in self:
            left = key[0]
            right = key[1]
            if left not in sector_balance:
                sector_balance[left] = 0
            if right not in sector_balance:
                sector_balance[right] = 0

            balance = self[key]
            sector_balance[left] += balance
            sector_balance[right] += balance

        return sector_balance

    def multilateral_balance(self):
        if 0 == len(self):
            return

        # assemble per-sector imbalances
        sector_balance = self.single_unit_imbalance()

        # if no sector has 2 or more half-unit against it, return
        if 0 == len(sector_balance) or 2 > max(sector_balance.values()):
            return

        for key in sector_balance:
            if 2 > sector_balance[key]:
                continue

            comp = [k for k in self.keys() if k[0] == key or k[1] == key]
            self.region[self.field][key].stats[self.stat_field] += 1
            self[comp[0]] -= 1
            self[comp[1]] -= 1
            left = comp[0][0] if comp[0][1] == key else comp[0][1]
            right = comp[1][0] if comp[1][1] == key else comp[1][1]
            adjkey = self._balance_tuple(left, right)

            self[adjkey] += 1
            if 1 < self[adjkey]:
                self.region[self.field][left].stats[self.stat_field] += 1
                self.region[self.field][right].stats[self.stat_field] += 1
                self[adjkey] -= 2

            sector_balance = self.single_unit_imbalance()

    def is_balanced(self):
        num_sector = len(self.region[self.field])

        assert 2 > self.maximum, "Uncompensated " + str(self.target) + " imbalance present"

        assert self.sum <= ceil(num_sector / 2), "Uncompensated multilateral " + str(self.target) +" imbalance present"

    @property
    def maximum(self):
        if 0 == len(self):
            return 0
        return max(self.values())

    @property
    def sum(self):
        if 0 == len(self):
            return 0
        return sum(self.values())

    @staticmethod
    def _check(key: tuple, value: int):
        assert isinstance(key, tuple), "Key must be tuple"
        assert 2 == len(key), "Key must be 2-element tuple"
        assert isinstance(key[0], str) and isinstance(key[1], str), "Key must be 2-element tuple of strings"
        assert isinstance(value, int), "Value must be integer"

    @staticmethod
    @functools.cache
    def _balance_tuple(name_from, name_to):
        if name_from <= name_to:
            return (name_from, name_to)
        return (name_to, name_from)
