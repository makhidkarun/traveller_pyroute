"""
Created on Nov 21, 2023

Supporting utilities needed by various SystemData components

@author: CyberiaResurrection
"""


class Utilities:

    tax_rate = {'0': 0.50, '1': 0.8, '2': 1.0, '3': 0.9, '4': 0.85,
                '5': 0.95, '6': 1.0, '7': 1.0, '8': 1.1, '9': 1.15,
                'A': 1.20, 'B': 1.1, 'C': 1.2, 'D': 0.75, 'E': 0.75,
                'F': 0.75,
                # Aslan Government codes
                'G': 1.0, 'H': 1.0, 'J': 1.2, 'K': 1.1, 'L': 1.0,
                'M': 1.1, 'N': 1.2,
                # Unknown Gov Codes
                'I': 1.0, 'P': 1.0, 'Q': 1.0, 'R': 1.0, 'S': 1.0, 'T': 1.0,
                '': 1.0, 'U': 1.0, 'V': 1.0, 'W': 1.0, 'X': 1.0, '?': 0.0
                }

    @staticmethod
    def ehex_to_int(value) -> int:
        if not isinstance(value, str):
            raise ValueError("Value must be string")
        val = int(value, 36) if value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' else 0
        val -= 1 if val > 18 else 0
        val -= 1 if val > 22 else 0
        return val

    @staticmethod
    def int_to_ehex(value: int) -> str:
        if not isinstance(value, int):
            raise ValueError("Value must be integer")
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
        assert False  # pragma: no mutate
