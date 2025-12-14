"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
from collections import OrderedDict

from PyRoute.UWPCodes import UWPCodes
from PyRoute.StatCalculation.ObjectStatistics import ObjectStatistics


class UWPCollection(object):
    def __init__(self):
        self.uwp = OrderedDict()
        for uwpCode in UWPCodes.uwpCodes:
            self.uwp[uwpCode] = {}

    def stats(self, code, value) -> ObjectStatistics:
        return self.uwp[code].setdefault(value, ObjectStatistics())

    def __getitem__(self, index):
        return self.uwp[index]

    def __setitem__(self, index, value):
        self.uwp[index] = value
