from PyRoute.Galaxy import AreaItem


class TradeBalance(dict):

    def __init__(self, area_item=None):
        assert isinstance(area_item, AreaItem), "AreaItem parm must be an instance of AreaItem"
        super().__init__()

        self.area_item = area_item
        pass

    def update(self, __m, **kwargs):
        for key in __m:
            self._check(key, __m[key])
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        self._check(item, value)
        super().__setitem__(item, value)

    @staticmethod
    def _check(key: tuple, value: int):
        assert isinstance(key, tuple), "Key must be tuple"
        assert 2 == len(key), "Key must be 2-element tuple"
        assert isinstance(key[0], str) and isinstance(key[1], str), "Key must be 2-element tuple of strings"
        assert isinstance(value, int), "Value must be integer"
