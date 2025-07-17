"""
Created on Jan 19, 2025

@author: CyberiaResurrection
"""

import os


class UnpackFilename(object):

    @staticmethod
    def unpack_filename(filename: str) -> str:
        # try unpacked filename directly
        sourcefile = os.path.abspath(filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('Tests/' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('Tests/Tests/' + filename)
        if not os.path.isfile(sourcefile):
            raise BaseException(sourcefile + " not mapped to a file")

        return sourcefile
