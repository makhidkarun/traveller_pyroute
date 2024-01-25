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
        '0000 000000000000000 ???????-? 000000000000000       -         - 0 000   01',
        '0000 000000011111111 ???????-? 9BD00QRV)(alo{{       1 * 0  011       1000000 000{',
        '0000 000000000000000 ???????-? 000000000000000 {0} -  -         - 0 000   00',
        '0000 000000000000000 ???????-? 0000000000000 {       - - 0 000    00',
        '0000 000000000000000 ???????-? 0000000000000 [       - - 0 000    00',
        '0000 000000000000000 ???????-? 0000000000000 0         - 0 000    00',
        '0000 000000000000000 ???????-? 000000000000000       -       - 0   000   01',
        '0000 000000000000000 ???????-? 0000000000000 0 {0} -  -    - 0 000   00',
        '0000 000000000000000 0000000-0 000000000000000       -       - 0   000   00',
        '0000 000000000000000 ???????-? 000000000000 00         - 0 000    00',
        '0000 000000000000000 0000000-0 000000000000000       - -         0   000   01',
        '0000 000000000000000 ???????-? 000000000000000       - -         0   001   00',
        '0000 000000000000000 ???????-? 000000000000000       - -         0   002   00',
        '0000 000000000000000 0000000-0 000000000000000 {0} (000-0) [0000]       - - 0 000   00?',
        '0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]       - - 0 000   00?'
    ]

    candidate = draw(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    assume(67 != len(candidate))
    assume(candidate not in rejects)
    data = ParseStarInput.starline.match(candidate).groups()
    if '{' in data[3] and '}' in data[3] and '[' in data[3] and ']' in data[3] and '(' in data[3] and ')' in data[3]:
        assume(False)  # Skip generating cases where all three extensions end up in trade codes
    if '*' in data[3]:
        assume(False)
    bitz = data[3].split(' ')
    numbitz = len(bitz)
    singleton = [item for item in bitz if 1 == len(item)]
    if singleton:
        assume(not singleton)
    if 15 < len(data[3]):
        if '' == data[11] or ' ' == data[11]:  # Skip generating noble-code spillovers
            assume(False)
        if '' == data[12] or ' ' == data[12]:  # Skip generating base-code spillovers
            assume(False)
        if '' == data[13] or ' ' == data[13]:  # Skip generating zone-code spillovers
            assume(False)
    for i in range(0, numbitz):
        bit = bitz[i]
        # homeworld codes with a pop digit _and_ something following will already be parsed differently, skip them here
        if 3 > len(bit):
            continue
        if bit.startswith('(') and ')' in bit:
            if ')' != bit[-1] and ')' != bit[-2]:
                assume(False)
            if ')' == bit[-2] and not (bit[-1].isdigit() or bit[-1] in 'WX?'):
                assume(False)
        if bit.startswith('[') and ']' in bit:
            if ']' != bit[-1] and ']' != bit[-2]:
                assume(False)
            if ']' == bit[-2] and not (bit[-1].isdigit() or bit[-1] in 'WX?'):
                assume(False)
        if i < numbitz - 1:
            second = bitz[i+1]
            if 3 > len(second):
                continue
            if bit.startswith('(') and ')' in second:
                if ')' != second[-1] and ')' != second[-2]:
                    assume(False)
                if ')' == second[-2] and not (second[-1].isdigit() or second[-1] in 'WX?'):
                    assume(False)
            if bit.startswith('[') and ']' in second:
                if ']' != second[-1] and ']' != second[-2]:
                    assume(False)
                if ']' == second[-2] and not (second[-1].isdigit() or second[-1] in 'WX?'):
                    assume(False)

    assume(3 > len(data[15]))  # Skip generating overlong world/allegiance codes
    assume(not data[16].isdigit())  # Skip generating numeric allegiances
    badminor = r'\([^\)]{1,}\)[\d]{2,}'
    badmatch = re.findall(badminor, data[3])  # Skip generating malformed minor-sophont pop codes
    if 0 < len(badmatch):
        assume(False)

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
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   0000', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -   [0000] - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         - 0   000   00', True)
    @example('0001 000000000000000 ???????-? 000000000000000         - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 0000000-0000000       - - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {   0} -  [0000] - - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000   000000', True)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000 0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000 0 01', True)
    @example('0000 000000000000000 ???????-? 000000000000001         * 0   000 0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -      [0000] - - 0 000 0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000 ', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - -  0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000  0       - - 0 000    00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000  0 00000', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0 0       0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000         * 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00000 0', True)
    @example('0000 000000000000000 0000000-0 000000000000000         - 0     000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000         - 0   000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   00{0', True)
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
    @example('0000 000000011111111 ???????-? 9BD00QRV)(alo{{       1 * 0  011       1000000 000{', False)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000   0 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000 00   00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000   00 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   000 00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0      - 0 000   00', True)
    @example('0000 000000000000000 ???????-? 0000000000000 0         - 0 000    00', True)
    @example('0000 000000000000000 0000000-0 000000000000000       - - 0 000    ?0', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - 000 0 001   00', True)
    @example('0000 000000000000000 ???????-? 0000000000000 0 {0} -  -    - 0 000   00', True)
    @example('0000 000000000000000 0000000-0 000000000000  0       - - 0 000   000', True)
    @example('0000 000000000000000 ???????-? 000000000000000         *       0 000   00', True)
    @example('0000 000000000000000 ???????-? 000000000000 00         - 0 000    00', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   0 00? 0', True)
    @example('0000 000000000000000 0000000-0 (000000000000)?       - - 0 000   00?', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000] 0      - 0 000   00?', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   ?0 0 0', True)
    @example('0000 000000000000  0 ???????-? 000000000000000       - - 0 000   00?', True)
    @example('0000 000000000000000 ???????-? 00000 (00000000 {0} (000-0) -  - - 0 000   00?', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]      - 0 000   0?', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000] 0 0       0 000   ?0', True)
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   0 00? 0 0', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0 0      0 000 000 000?0', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0 *      0 001 000 ?0000', True)
    @example('0000 000000000000000 ???????-? 000000000000000       0 0      0 000   000 ?0000', True)
    @example('0000 000000000000000 ???????-? 000000000 00 00       - 000 0 000   ?0', True)
    @example('0000 000000000000000 ???????-? 0000000000 00 00       - 000 0 000   0?', True)
    @example('0000 000000000000000 ???????-? 00000000000 00 00       - 000 0 000   ?0', True)
    @example('0000 000000000000000 0000000-0 000000000000000       00 *       0 000   00?', True)
    # Examples below this line tripped up live run
    @example('0102                      X100000-0 Ba Lo Ni Va                         - - - 003   -- M1 V               \n', True)
    @example('0302                      X501000-0 Ba Ic Lo Ni Va                      - - - 030   -- M2 V M1 D          \n', True)
    @example('2309                      X476000-0 Ba Lo Ni                            - - - 006   -- F0 V M4 D M2 D     \n', True)
    @example('0605                      C9EA764-A Wa O:????             {  1 } (A69+1) [7879] ', True)
    @example('3015 Anix Nuno            C446953-B Hi In (Anixii)W Da          {  3 } (68A-5) [7CAC] - - A 901 11 HvFd M3 V M4 V      \n', True)
    @example('0101 Dujj\'t\'kzo         E331000-0 Ba Po                       { -3 } (900-4) [0000] - - - 003 8 Ia   M3 IV M4 V    \n', True)
    @example('1708                      E32579A-7 Pi X!tkW Pz                  { -2 } (761+2) [3566] - -  A 705 14 KkTw A0 V            ', True)
    @example('0201 Yaweakhea\'e         D762445-6 Ni O:Hare3240        {-3} (A30-2) [1134] - - - 300   As F4 V            \n', True)
    @example('3227                      E242662-7 Ni Po Cy O:Porl:0528         { -3 } (550-1) [2318] - -  - 601 7  NaXX A4 V G7 V     ', True)
    @example('3137 Xakigraxtu           A778565-7 Ag Ni O:GhXh-0137    { 0 }  (542+3) [4564] - M - 423 11 CsTw F3 V           \n', True)
    @example('2619 Aestera              A8A2362-C Fl He Ho Ht Lo O:1518         { 2 }  (B22+5) [416B] - KMV - 823 12 Ou   B7 V D BD A2 V M2 V       \n', True)
    # More weird cases accumulated along the way
    @example('0000 000000000000000 ???????-? 000000000000000       0 00       0 000   ?0', True)
    @example('0000 000000000000000 ???????-? 00000000000 00 00       - 00G 0 000   0?', True)
    @example('0000 000000000000000 ???????-? 000000000000000       00 0       0 000   ?0', True)
    @example('0000 000000000000000 ???????-? 0000000000000 00       0 0       0 000   ?0', True)
    @example('0000 000000000000000 ???????-? 0000000000000?  00       - - 0 000   0?', True)
    @example('0000 000000000000000 ???????-? 000000000000000 {  0} (000-0) [0000]   - 0   000   00?', True)
    # Cases where original regex output was wonky
    @example('0000 000000000000000 ???????-? 000000000000000       -       - 0   000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       -         - 0 000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       -       - 0   000 0 00', False)
    @example('0000 000000000000000 0000000-0 000000000000000       -         - 0 000 0 00', False)
    @example('0001 000000000000000 ???????-? 000000000000000       -         - 0 000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       -         - 0 000   01', False)
    @example('0000 000000000000000 ???????-? 000000000000000       -       - 0   000   01', False)
    @example('0000 000000000000000 0000000-0 000000000000000       -       - 0   000   00', False)
    @example('0000 000000000000000 0000000-0 000000000000000       - -         0   000   01', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   001   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000       - -         0   002   00', False)
    @example('0000 000000000000000 0000000-0 000000000000000       00         - 0 000   00', False)
    @example('0000 000000000000000 0000000-0 (000000000000)A       - - 0 000   00?', False)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} (000-0) [0000]       - - 0 000   ?0', False)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} (000-0)       -    - 0 000   0?', False)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} (000-0) [0000]       - - 0 000   00?', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]       - - 0 000   00?', False)
    @example('0000 000000000000000 ???????-? 000000000 (00)A       - - 0 000    0?', False)
    @example('0000 000000000000000 0000000-0 000000000000000       - -         0   000   00', False)
    @example('0000 000000000000000 0000000-0 000000000000000 {0} -  -         - 0 000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -         - 0 000 0 00', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -         - 0 000   00', False)
    @example('0000 000000000000000 ???????-? 000000000000000 {0} -  -       - 0   000   00', False)
    @example('0000 000000000000000 0000000-0 (00000000000)0)       - - 0 000   00?', False)
    # Weird parsing cases
    @example('0000 000000000000000 ???????-? (00000000000000       - - 0 000   00?)', 'weird')
    @example('0000 000000000000000 ???????-? [00000000000000       - - 0 000   00?]', 'weird')
    def test_starline_parser_against_regex(self, s, match):
        # if it's a known weird-parse case, assume it out now
        assume(match != 'weird')
        matches = ParseStarInput.starline.match(s)
        assume(matches is not None)
        hyp_line = "Hypothesis input: " + s
        data = list(matches.groups())
        data[1] = StarlineTransformer.boil_down_double_spaces(data[1].strip())
        data[3] = StarlineTransformer.boil_down_double_spaces(data[3].strip())
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
            data[17] = StarlineTransformer.boil_down_double_spaces(data[17].strip())

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
