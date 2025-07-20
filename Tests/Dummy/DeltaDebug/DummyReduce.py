"""
Created on Oct 09, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaReduce import DeltaReduce


class DummyReduce(DeltaReduce):

    def __init__(self, sectors, args, interesting_line=None, interesting_type=None):
        super().__init__(sectors, args, interesting_line=interesting_line, interesting_type=interesting_type)
        self.jam_interesting = None

    def _check_interesting(self, args, sectors):
        if self.jam_interesting is not None:
            return self.jam_interesting, "", None

        return DeltaReduce._check_interesting(args, sectors)
