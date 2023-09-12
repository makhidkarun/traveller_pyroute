import os
import unittest


class baseTest(unittest.TestCase):
    def unpack_filename(self, filename):
        # try unpacked filename directly
        sourcefile = os.path.abspath(filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('Tests/' + filename)
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/' + filename)

        return sourcefile


if __name__ == '__main__':
    unittest.main()
