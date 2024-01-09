"""
Created on Dec 27, 2023

@author: CyberiaResurrection
"""

import copy
import logging
import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, composite, integers, floats, lists, sampled_from, booleans, none

from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Inputs.StarlineParser import StarlineParser
from PyRoute.Inputs.StarlineTransformer import StarlineTransformer


@composite
def comparison_line(draw):
    rejects = [
        '0000 000000000000000 ???????-? 000000000000000         - 0   000   00',
        '0000 000000000000000 0000000-0 000000000000000       - - 0 000 00 00',
        '0000 000000000000000 ???????-? 0000000000000 0       - - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000000       -       - 0   000   00',
        '0000 000000000000000 ???????-? 000000000000000       - -         0   000   00',
        '0000 000000000000000 ???????-? 000000000000000         - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000000         - 0 001   00',
        '0000 000000000000000 ???????-? 000000000000000         - 0 000   01',
        '0001 000000000000000 ???????-? 000000000000000         - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000001         - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000000       -         - 0 000   00',
        '0000 000000000000000 0000000-0 000000000000000       - -         0   000   00',
        '0002 000000000000000 ???????-? 000000000000000         - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000000         * 0   000 0 00',
        '0000 000000000000000 ???????-? 000000000000000         * 0   000 0 01',
        '0000 000000000000000 ???????-? 000000000000000 {0} -  -  - 000 0 000   00',
        '0000 000000000000000 0000000-0 000000000000000 {0} -  -         - 0 000 0 00',
        '0000 000000000000000 ???????-? 000000000000000       - -         0   000 0 00',
        '0000 000000000000000 ???????-? 000000000000001         * 0   000 0 00',
        '0000 000000000000000 ???????-? 000000000000000       -       - 0   000 0 00',
        '0000 000000000000000 0000000-0 000000000000000       -         - 0 000 0 00',
        '0000 000000000000000 ???????-? 000000000000000 {0} -  -         - 0 000 0 00',
        '0000 000000000000000 ???????-? 000000000000  0       - - 0 000    00',
        '0001 000000000000000 ???????-? 000000000000000       -         - 0 000   00',
        '0000 000000000000000 ???????-? 000000000000000       - - 0 000   00-',
        '0000 000000000000000 ???????-? 000000000000000       -         - 0 000   01'
    ]

    candidate = draw(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    assume(67 != len(candidate))
    assume(candidate not in rejects)
    return candidate


class testHypothesisStarlineParser(unittest.TestCase):

    @given(comparison_line(), none())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000?       - - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 00000000000000-       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000+       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000*       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000)       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000{       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000(       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000\'       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000[       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000]       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 00000000000000}       - - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000 0 00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000 00 00 M2 V', True)
    @example('0000 000000000000000  ???????-? 000000000000000       - - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - -      0 000   00', True)
    @example('0000 000000000000000 ???????-? 0000000000000000       - - 0 000   00', True)
    @example('2916 Khiinra Ash          BAE6362-8 Lo Syle1 (Bhu\'oovaakaylaa)9 O:2914 Sa { -1 } (920-5) [1214] B     -  - 704 7  ImSy M1 V M2 V', True)
    @example('3234 Gau                  B433764-C Na Po O:Forn-0135                     { 2 }  (B6C+1) [593A] B     -  - 520 8  ImDc K5 V M2 V', True)
    @example('1717 Vland                A967A9A-F Hi Cs [Vilani]            { 3 }  (D9F+5) [CD7H] BEFG N  - 310 7  ImDv F8 V           ', True)
    @example('1919 Khula                B575A77-E Hi In Pz Di(Khulans)      { 4 }  (D9G+4) [AE5E] BEf  N  A 510 10 ImDv M0 V', True)
    @example('0305 Ofilaq               A946823-B Pi Ph Pa Cs (Gurvin)8   {  2 } (A7C+1) [8A4B] - -  - 504 16 HvFd F9 V', True)
    @example('1119 Muan Irrzudh         A66A786-D Ri Wa VegaW                     { 3 }  (96C+1) [6A4C] BC   -  - 800 9  ImVd K6 V M0 V', True)
    @example('0102                      X332000-0 Ba Lo Ni Po                         - -  - 021   --               ', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -  - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 0000000000000 0       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       -       - 0   000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   0000', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -   [0000] - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         - 0   000   00', True)
    @example('0001 000000000000000 ???????-? 000000000000000         - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 0000000-0000000       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       -         - 0 000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - -         0   000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {   0} -  [0000] - - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000   000000', True)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000 0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000 0 01', True)
    @example('0000 000000000000000 ???????-? 000000000000001         * 0   000 0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -      [0000] - - 0 000 0 00', True)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} -  -         - 0 000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       -       - 0   000 0 00', False)
    @example('0000 000000000000000 0000000-0 000000000000000       -         - 0 000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -         - 0 000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000 ', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - -  0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000  0       - - 0 000    00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000  0 00000', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0 0       0 000   00', True)
    @example('0001 000000000000000 ???????-? 000000000000000       -         - 0 000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000 0', True)
    @example('0000 000000000000000 0000000-0 000000000000000         - 0     000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000         - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00{0', True)
    @example('0000 000000000000000 ???????-? 000000000000000       -         - 0 000   01', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]   -   0   000   00', True)
    # Examples below this line don't match straightup
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000  00 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00-', True)
    @example('0000 000000000000000 0000000-0 000000000000000         -   0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - -      0 000 0010 00+', True)
    @example('0000 000000000000000 0000000-0 000000000000000         - 0 000    00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000 00 00', True)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} -   -    - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000        - 000 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -  - 000 0 000   00', True)
    @example('0002 000000000000000 ???????-? 000000000000000         - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000001         - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         - 0 000   01', True)
    @example('0000 000000000000000 ???????-? 000000000000000         - 0 001   00', True)
    @example('0001 000000000000000 ???????-? 000000000000000         - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000 00 00', True)
    def test_starline_parser_against_regex(self, s, match):
        matches = ParseStarInput.starline.match(s)
        assume(matches is not None)
        hyp_line = "Hypothesis input: " + s
        data = list(matches.groups())
        data[1] = data[1].strip()
        data[3] = data[3].strip()
        self.square_up_extension_line(data)
        if data[5] is not None:
            data[5] = StarlineTransformer.boil_down_double_spaces(data[5])
        if data[6] is not None:
            data[6] = data[6].strip()
        if data[7] is not None:
            data[7] = data[7].strip()
        if data[7] is not None:
            data[7] = data[7].strip()
        if data[11] is not None:
            data[11] = data[11].strip()
        if data[13] is not None:
            data[13] = data[13].strip()
        if data[17] is not None:
            data[17] = data[17].strip()

        foo = StarlineParser()
        result, s = foo.parse(s)

        xform = StarlineTransformer(raw=s)
        transformed = xform.transform(result)

        if match is False:
            self.assertNotEqual(data, transformed, hyp_line)
        else:
            self.assertEqual(data, transformed, hyp_line)

    def square_up_extension_line(self, data):
        data[4] = data[4].replace('  [', ' [')
        data[4] = StarlineTransformer.boil_down_double_spaces(data[4])
        data[4] = data[4].strip()