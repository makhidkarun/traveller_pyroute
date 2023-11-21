"""
Created on Nov 21, 2023

Supporting utilities needed by various SystemData components

@author: CyberiaResurrection
"""


class Utilities:

    @staticmethod
    def ehex_to_int(value):
        val = int(value, 36) if value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' else 0
        val -= 1 if val > 18 else 0
        val -= 1 if val > 22 else 0
        return val

    @staticmethod
    def int_to_ehex(value):
        if 10 > value:
            return str(value)
        # Ehex doesn't use I, as it's too easily confused with the numeric 1, likewise with 0 and O
        if 9 < value < 18:
            valstring = 'ABCDEFGH'
            return valstring[value - 10]
        if 17 < value:
            valstring = 'JKLMNOPQRSTUVWXYZ'
            value += 1 if 22 < value else 0
            return valstring[value - 18]
