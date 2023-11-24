"""
Created on Nov 23, 2023

@author: CyberiaResurrection

Along the lines of TradeCodes, pull all the system-star handling, checking, etc into one class that _just_ does system
stars, rather than the multi-concern mashup that is the Star class

"""
import re

from PyRoute.SystemData.SystemStar import SystemStar


class StarList(object):

    stellar_line = '([OBAFGKM][0-9] ?(?:Ia|Ib|II|III|IV|V|VI|VII|D)|D|NS|PSR|BH|BD)'
    star_line = '^([OBAFGKM])([0-9]) ?(Ia|Ib|II|III|IV|V|VI)'

    stellar_match = re.compile(stellar_line)
    star_match = re.compile(star_line)

    # Limits
    max_stars = 8  # T5.10 book 3 p 21, "A system may to have up to eight stars:"

    def __init__(self, stars_line):
        self.stars_line = stars_line
        stars = StarList.stellar_match.findall(stars_line)
        if not stars:
            raise ValueError("No stars found")
        if 8 < len(stars):
            raise ValueError("Max number of stars is 8")

        self.stars_list = []
        for s in stars:
            if s == "D" or s == "NS" or s == "PSR" or s == "BH" or s == "BD":
                item = SystemStar(s)
            else:
                bitz = s.split(' ')
                item = SystemStar(bitz[1], bitz[0][0], int(bitz[0][1]))
            self.stars_list.append(item)

    def move_biggest_to_primary(self):
        num_stars = len(self.stars_list)
        if 2 > num_stars:  # nothing to do, bail out now
            return
        biggest = self.stars_list[0]
        bigdex = 0
        for i in range(1, num_stars):
            if not biggest.is_bigger(self.stars_list[i]):
                biggest = self.stars_list[i]
                bigdex = i

        if 0 != bigdex:
            self.stars_list[0], self.stars_list[bigdex] = self.stars_list[bigdex], self.stars_list[0]

    def is_well_formed(self):
        msg = ""
        num_stars = len(self.stars_list)
        if 8 < num_stars:
            msg = "Max stars exceeded"
            return False, msg
        if 0 == num_stars:
            msg = "Star list must not be empty"
            return False, msg
        for i in range(1, num_stars):
            if not self.stars_list[0].is_bigger(self.stars_list[i]):
                msg = "Index " + str(i) + " better primary candidate than index 0"
                return False, msg

        return True, msg
