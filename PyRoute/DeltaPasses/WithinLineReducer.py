"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaReduce import DeltaReduce


class WithinLineReducer(object):

    reducer: DeltaReduce

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self):
        raise NotImplementedError

    def _build_subs_list(self):
        raise NotImplementedError

    def _assemble_segment(self, unreduced_lines, subs_list):
        nu_list = []

        for line in subs_list:
            if line[0] in unreduced_lines:
                continue
            nu_list.append((line[0], line[1]))

        return nu_list
