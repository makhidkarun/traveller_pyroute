"""
Created on Dec 15, 2025

@author: CyberiaResurrection
"""
from collections import OrderedDict


class UWPCodes(object):
    uwpCodes = ['Starport',
                'Size',
                'Atmosphere',
                'Hydrographics',
                'Population',
                'Government',
                'Law Level',
                'Tech Level',
                'Pop Code',
                'Starport Size',
                'Primary Type',
                'Importance',
                'Resources']

    def __init__(self):
        self.codes = OrderedDict()
        for uwpCode in UWPCodes.uwpCodes:
            self.codes[uwpCode] = "X"
