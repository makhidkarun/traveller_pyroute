import argparse
import os
import tempfile
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

    def _make_args(self):
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = "Weight of edge"
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = tempfile.gettempdir()
        args.mp_threads = 1
        args.debug_flag = False
        return args

    def _make_args_no_line(self):
        args = self._make_args()
        args.interestingline = None

        return args

if __name__ == '__main__':
    unittest.main()
