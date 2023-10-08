"""
Created on Jun 13, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaStar import DeltaStar


class Canonicalisation(object):

    def __init__(self, reducer):
        self.reducer = reducer

    def preflight(self):
        if self.reducer is not None and self.reducer.sectors is not None and 0 < len(self.reducer.sectors.lines):
            return True
        return False

    def run(self):
        # build substitution list - canonicalise _everything_
        subs_list = []
        for line in self.reducer.sectors.lines:
            canon = DeltaStar.reduce(line)
            assert isinstance(canon, str), "Candidate line " + line + " was not reduced to a string.  Got " + canon + " instead."
            subs_list.append((line, canon))

        if 0 == len(subs_list):
            # nothing to do, bail out early
            return

        temp_sectors = self.reducer.sectors.switch_lines(subs_list)

        interesting, msg, _ = self.reducer._check_interesting(self.reducer.args, temp_sectors)

        if interesting:
            self.reducer.sectors = temp_sectors
            msg = "Reduction found with full canonicalisation"
            self.reducer.logger.error(msg)
            return
