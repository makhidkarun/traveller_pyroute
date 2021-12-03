"""
Created on Dec 04, 2021

@author: CyberiaResurrection

A dirt-simple adapter layer to abstract the differences in where Linux distros (currently, Ubuntu and Fedora)
store their font files away from the rest of the project
"""

from os import path
import functools

class FontLayer(object):
    fontdict = {}

    def __init__(self):
        self.fontdict['DejaVuSerifCondensed.ttf'] = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf',
            '/usr/share/fonts/dejavu-serif-fonts/DejaVuSerifCondensed.ttf'
        ]
        self.fontdict['LiberationMono-Bold.ttf'] = [
            '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
            '/usr/share/fonts/liberation-mono/LiberationMono-Bold.ttf'
        ]
        self.fontdict['FreeMono.ttf'] = [
            '/usr/share/fonts/truetype/freefont/FreeMono.ttf',
            '/usr/share/fonts/gnu-free/FreeMono.ttf'
        ]
        self.fontdict['Symbola-hint.ttf'] = [
            '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf',
            '/usr/share/fonts/gdouros-symbola/Symbola.ttf'
        ]

    @functools.cache
    def getpath(self, filename):
        # Deliberately lean on dictionaries blowing up on accessing absent keys to make it obvious
        # that we don't know how to handle what's being asked for
        filelist = self.fontdict[filename]

        for item in filelist:
            # for moment, don't care whether is a hard or softlinked file
            if path.exists(item):
                if not path.isdir(item):
                    return item

        return None
