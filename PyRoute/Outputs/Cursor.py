"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""


class Cursor(object):

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.dx = 0
        self.dy = 0

    def __eq__(self, other):
        return self._x == other._x and self._y == other._y

    def __str__(self):
        return f"{self._x}, {self._y}"

    def set_deltas(self, dx=2, dy=2):
        self.dx = dx
        self.dy = dy

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value=0):
        # If in left margin, sets to minimum value.
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value=0):
        self._y = value

    # Changes this cursor
    def x_plus(self, dx=None):
        """
        Mutable x addition. Defaults to set delta value.
        """
        self._x += dx if dx is not None else self.dx

    def y_plus(self, dy=None):
        """
        Mutable y addition. Defaults to set delta value.
        """
        self._y += dy if dy is not None else self.dy

    def copy(self):
        new_cursor = self.__class__(self.x, self.y)
        new_cursor.set_deltas(self.dx, self.dy)
        return new_cursor

    def tuple(self) -> tuple[int, int]:
        """
        Express x,y co-ordinates as a 2-element tuple
        """
        return self.x, self.y
