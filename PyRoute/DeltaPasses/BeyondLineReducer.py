"""
Created on Apr 05, 2025

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary
from PyRoute.DeltaPasses.WidenHoleReducer import WidenHoleReducer


class BeyondLineReducer(object):

    def __init__(self, reducer):
        self.reducer = reducer
        self.breacher = WidenHoleReducer(reducer)

    def preflight(self) -> bool:
        return self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines)

    def write_files(self, sectors=None) -> None:
        if isinstance(sectors, DeltaDictionary):
            sectors.write_files(self.reducer.args.mindir)
        else:
            self.reducer.sectors.write_files(self.reducer.args.mindir)
