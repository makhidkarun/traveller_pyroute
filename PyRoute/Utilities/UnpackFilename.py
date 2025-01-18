"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""

import os


class UnpackFilename:

    @staticmethod
    def unpack_filename(filename):
        # try unpacked filename directly
        sourcefile = os.path.abspath(filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('Tests/' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/' + filename)

        return sourcefile
