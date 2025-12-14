import functools
from math import ceil
import logging

from PyRoute.Star import Star


class TradeBalance(dict):

    def __init__(self, stat_field=None, region=None, target="passenger", field="sectors", star_field="sector",
                 target_property="name"):
        assert isinstance(stat_field, str), "Stat_field must be a string"
        from PyRoute.AreaItems.Galaxy import Galaxy
        assert isinstance(region, Galaxy), "Region must be an Galaxy"
        assert isinstance(target, str)
        assert isinstance(field, str), "Target field must be a string"
        super().__init__()
        self.stat_field = stat_field
        self.region = region
        self.target = target
        self.field = field
        self.star_field = star_field
        self.target_property = target_property
        self.logger = logging.getLogger('PyRoute.TradeBalance')

    def update(self, __m, **kwargs) -> None:  # type:ignore[override]
        for key in __m:
            self._check(key, __m[key])
        super().update(__m, **kwargs)  # pragma: no mutate

    def __setitem__(self, item, value):
        self._check(item, value)
        super().__setitem__(item, value)

    def log_odd_unit(self, star: Star, target: Star) -> None:
        sector_tuple = self._balance_tuple(
            star[self.star_field][self.target_property],
            target[self.star_field][self.target_property]
        )
        if sector_tuple not in self:
            self[sector_tuple] = 0
        self[sector_tuple] += 1
        if 1 < self[sector_tuple]:
            star[self.star_field].stats[self.stat_field] += 1
            target[self.star_field].stats[self.stat_field] += 1
            self[sector_tuple] -= 2

    def single_unit_imbalance(self) -> dict[str, int]:
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

    def multilateral_balance(self) -> None:
        # assemble per-sector imbalances
        sector_balance = self.single_unit_imbalance()

        # if no sector has 2 or more half-unit against it, return
        if 0 == len(sector_balance) or 2 > max(sector_balance.values()):
            return
        maxloops = max(sector_balance.values())
        counter = 0

        while 1 < max(sector_balance.values()) and counter <= maxloops:  # pragma: no mutate
            counter += 1
            for key in sector_balance:
                if 2 > sector_balance[key]:
                    continue

                comp = [k for k in self.keys() if (k[0] == key or k[1] == key) and self[k] > 0]
                if 2 > len(comp):
                    continue
                self.region[self.field][key].stats[self.stat_field] += 1
                self[comp[0]] -= 1
                self[comp[1]] -= 1

                sector_balance = self.single_unit_imbalance()
            self_max = self.maximum
            if 1 < self_max:  # pragma: no mutate
                adjkey = max(self, key=self.get)  # type: ignore[arg-type]
                adjvalue = self[adjkey] // 2
                left = adjkey[0]
                right = adjkey[1]
                self.region[self.field][left].stats[self.stat_field] += adjvalue
                self.region[self.field][right].stats[self.stat_field] += adjvalue
                self[adjkey] -= (2 * adjvalue)

            sector_balance = self.single_unit_imbalance()
            self.logger.debug('Iteration ' + str(counter) + ', sector balance ' + str(sector_balance))

    def is_balanced(self) -> None:
        num_sector = len(self.region[self.field])

        assert 2 > self.maximum, "Uncompensated " + str(self.target) + " imbalance present"

        assert self.sum <= ceil(num_sector / 2), f"Uncompensated multilateral {self.target} imbalance present in {self.field}"

    @property
    def maximum(self) -> int:
        if 0 == len(self):
            return 0
        return max(self.values())

    @property
    def sum(self) -> int:
        if 0 == len(self):
            return 0
        return sum(self.values())

    @staticmethod
    def _check(key: tuple, value: int):
        assert isinstance(key, tuple), "Key must be tuple"
        assert 2 == len(key), "Key must be 2-element tuple"
        assert isinstance(key[0], str) and isinstance(key[1], str), "Key must be 2-element tuple of strings"
        assert key[0] != key[1], "Elements of key must differ"
        assert isinstance(value, int), "Value must be integer"

    @staticmethod
    @functools.cache
    def _balance_tuple(name_from, name_to):
        if name_from <= name_to:
            return (name_from, name_to)
        return (name_to, name_from)
