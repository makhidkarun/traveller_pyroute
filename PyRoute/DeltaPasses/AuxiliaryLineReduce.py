"""
Created on Jul 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaPasses.WithinLineReducer import WithinLineReducer
from PyRoute.DeltaStar import DeltaStar


class AuxiliaryLineReduce(WithinLineReducer):

    def _build_subs_list(self):
        self.full_msg = "Reduction found with auxiliary line reduction"
        self.start_msg = "Commencing auxiliary within-line reduction"
        # build substitution list - reduce _everything_
        subs_list = []
        segment = []
        num_lines = len(self.reducer.sectors.lines)
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce_auxiliary(line.strip())
            assert isinstance(canon,
                              str), "Candidate line " + line + " was not reduced to a string.  Got " + canon + " instead."
            # Skip already-reduced lines
            if 2 < num_lines and line == canon:
                continue
            subs_list.append((line, canon))
            segment.append(line)
        return segment, subs_list
