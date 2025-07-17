"""
Created on May 05, 2025

@author: CyberiaResurrection
"""
from DeltaPasses.WithinLineReducer import WithinLineReducer
from DeltaStar import DeltaStar


class NoblesTrimLineReduce(WithinLineReducer):

    def _build_subs_list(self):
        self.full_msg = "Reduction found with nobles trim"
        self.start_msg = "Commencing nobles trim within-line reduction"

        # build substitution list - reduce _everything_
        subs_list = []
        segment = []
        num_lines = len(self.reducer.sectors.lines)
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce(line, trim_noble_codes=True)
            assert isinstance(canon,
                              str), "Candidate line " + line + " was not reduced to a string.  Got " + canon + " instead."
            # Skip already-reduced lines
            if 2 < num_lines and line.startswith(canon):
                continue
            subs_list.append((line, canon))
            segment.append(line)
        return segment, subs_list
