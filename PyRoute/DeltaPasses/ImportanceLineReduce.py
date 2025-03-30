"""
Created on Jul 14, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaPasses.WithinLineReducer import WithinLineReducer
from PyRoute.DeltaStar import DeltaStar


class ImportanceLineReduce(WithinLineReducer):

    def _build_subs_list(self):
        self.full_msg = "Reduction found with importance line reduction"
        self.start_msg = "Commencing importance-related within-line reduction"
        # build substitution list - reduce _everything_
        subs_list = []
        segment = []
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce_importance(line)
            assert isinstance(canon,
                              str), "Candidate line " + line + " was not reduced to a string.  Got " + canon + " instead."
            # Skip already-reduced lines
            if line.startswith(canon):
                continue
            subs_list.append((line, canon))
            segment.append(line)
        return segment, subs_list
