"""
Created on Nov 23, 2023

@author: CyberiaResurrection

Along the lines of TradeCodes, pull all the system-star handling, checking, etc into one class that _just_ does system
stars, rather than the multi-concern mashup that is the Star class

"""
import re

from SystemData.SystemStar import SystemStar


class StarList(object):

    stellar_line = '([OBAFGKM][0-9] ?(?:Ia|Ib|II|III|IV|V|VI|VII|D)|D|NS|PSR|BH|BD)'
    star_line = '^([OBAFGKM])([0-9]) ?(Ia|Ib|II|III|IV|V|VI)'

    stellar_match = re.compile(stellar_line)
    star_match = re.compile(star_line)

    # Limits
    max_stars = 8  # T5.10 book 3 p 21, "A system may to have up to eight stars:"

    def __init__(self, stars_line):
        self.stars_line = stars_line
        stars = StarList.stellar_match.match(stars_line)
        if not stars:
            raise ValueError("No stars found")

        self.stars_list = []
        matches = stars.groups()
        for match in matches:
            item = SystemStar(match)
            self.stars_list.append(item)

    def is_well_formed(self):
        msg = ""
        if 8 < len(self.stars_list):
            msg = "Max stars exceeded"
            return False, msg
        if 0 == len(self.stars_list):
            msg = "Star list must not be empty"
            return False, msg

        return True, msg
