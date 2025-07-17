"""
Created on Dec 04, 2021

@author: CyberiaResurrection

A dirt-simple adapter layer that used to abstract the differences in where Linux distros (currently, Ubuntu and Fedora)
store their font files away from the rest of the project.  Now, it still serves as a SPOT for font locations, even
though they're now bundled with the project.
"""

import os
import functools

from Utilities.UnpackFilename import UnpackFilename


class FontLayer(object):
    fontdict: dict[str, list[str]] = {}

    def __init__(self):
        self.fontdict['DejaVuSerifCondensed.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/DejaVuSerifCondensed.ttf')
        ]
        self.fontdict['DejaVuSerifCondensed-Bold.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/DejaVuSerifCondensed-Bold.ttf')
        ]
        self.fontdict['LiberationMono-Bold.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/LiberationMono-Bold.ttf')
        ]
        self.fontdict['FreeMono.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/FreeMono.ttf')
        ]
        self.fontdict['Symbola-hint.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/Symbola-hint.ttf')
        ]

        self.fontdict['ZapfDingbats_Regular.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/ZapfDingbats-Regular.ttf')
        ]

        self.fontdict['ZapfDingbats-Regular.ttf'] = [
            UnpackFilename.unpack_filename('../PyRoute/Fonts/ZapfDingbats-Regular.ttf')
        ]

    @functools.cache
    def getpath(self, filename) -> str:
        # Deliberately lean on dictionaries blowing up on accessing absent keys to make it obvious
        # that we don't know how to handle what's being asked for
        filelist = self.fontdict[filename]

        for item in filelist:
            # for moment, don't care whether is a hard or softlinked file
            if os.path.exists(item) and not os.path.isdir(item):
                return item

        assert False, "Font mapping for " + filename + " not found.  Tried " + " ".join(filelist)
