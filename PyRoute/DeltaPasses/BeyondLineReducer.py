"""
Created on Apr 05, 2025

@author: CyberiaResurrection
"""
from DeltaDebug.DeltaDictionary import DeltaDictionary
from DeltaPasses.WidenHoleReducer import WidenHoleReducer


class BeyondLineReducer(object):

    def __init__(self, reducer):
        from DeltaDebug.DeltaReduce import DeltaReduce
        self.reducer: DeltaReduce = reducer
        self.breacher = WidenHoleReducer(reducer)

    def preflight(self) -> bool:
        return self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines)

    def write_files(self, sectors=None) -> None:
        if isinstance(sectors, DeltaDictionary):
            sectors.write_files(self.reducer.args.mindir)
        else:
            self.reducer.sectors.write_files(self.reducer.args.mindir)
