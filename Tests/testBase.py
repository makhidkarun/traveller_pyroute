import argparse
import tempfile
import unittest


class testBase(unittest.TestCase):
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
        return args

    def _make_args_no_line(self) -> argparse.ArgumentParser:
        args = self._make_args()
        args.interestingline = None

        return args
