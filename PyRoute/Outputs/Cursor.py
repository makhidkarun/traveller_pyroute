"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""


class Cursor(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

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
        if dx is None:
            self.x += self.dx
        else:
            self.x = self.x + dx

    def y_plus(self, dy=None):
        """
        Mutable y addition. Defaults to set delta value.
        """
        if dy is None:
            self.y += self.dy
        else:
            self.y = self.y + dy

    def copy(self):
        new_cursor = self.__class__(self.x, self.y)
        new_cursor.set_deltas(self.dx, self.dy)
        return new_cursor

    def __str__(self):
        return "({:f}, {:f})".format(self.x, self.y)
