"""
Created on Mar 03, 2024

@author: CyberiaResurrection
"""


class DeltaLogicError(AssertionError):

    @staticmethod
    def delta_assert(condition, message):
        if not condition:
            raise DeltaLogicError(message)
