import functools

from PyRoute.Star import Star


class TradeBalance(dict):

    def __init__(self, stat_field=None):
        assert isinstance(stat_field, str), "Stat_field must be a string"
        super().__init__()
        self.stat_field = stat_field
        pass

    def update(self, __m, **kwargs):
        for key in __m:
            self._check(key, __m[key])
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        self._check(item, value)
        super().__setitem__(item, value)

    def log_odd_unit(self, star: Star, target: Star):
        sector_tuple = self._balance_tuple(star.sector.name, target.sector.name)
        if sector_tuple not in self:
            self[sector_tuple] = 0
        self[sector_tuple] += 1
        if 1 < self[sector_tuple]:
            star.sector.stats.passengers += 1
            target.sector.stats.passengers += 1
            self[sector_tuple] -= 2

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
