import argparse
import logging
import os
import tempfile
import unittest

from PyRoute.Utilities.UnpackFilename import UnpackFilename


class baseTest(unittest.TestCase):

    # Set up logging information
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    def unpack_filename(self, filename: str) -> str:
        return UnpackFilename.unpack_filename(filename)

    def unpack_workdir(self, dirname) -> str:
        # try unpacked directory directly
        workdir = os.path.abspath(dirname)

        cwd = os.getcwd()
        if not os.path.isdir(workdir):
            workdir = os.path.abspath(cwd + dirname)

        return workdir

    def _make_args(self) -> argparse.ArgumentParser:
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
        args.map_type = "classic"
        return args

    def _make_args_no_line(self) -> argparse.ArgumentParser:
        args = self._make_args()
        args.interestingline = None

        return args


if __name__ == '__main__':
    unittest.main()
