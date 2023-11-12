import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings, reproduce_failure
from hypothesis.strategies import text, from_regex, composite, floats

from PyRoute.Galaxy import Sector


@composite
def position_string(draw):
    left = draw(text(min_size=2, alphabet='+- 0123456789'))
    right = draw(text(min_size=1, alphabet='+- 0123456789'))

    return left + ',' + right

@composite
def sector_name(draw):
    stem = draw(text(min_size=1))
    flip = draw(floats(min_value=0.0, max_value=1.0))

    if 0.9 > flip:
        return stem + " Sector"
    return stem


class testSector(unittest.TestCase):

    @given(sector_name(), position_string())
    @settings(
        suppress_health_check=[HealthCheck(3), HealthCheck(2)],  # suppress slow-data health check, too-much filtering
        deadline=timedelta(1000))
    @example('00', '0:,0')
    @example('00', '00,:')
    @example('00', '0A,0')
    @example('00', '0\x1f,0')
    @example('00', '0,0\x1f')
    @example('00', '00,0Ā')
    @example('00', '0-,0')
    @example('00', '0+,0')
    @example('00', '00,-')
    @example('00', '00,+')
    @example('00', '00-,0')
    @example('00', '00,0-')
    @example('00', '0 - 1, -1')
    @example('00', '0 -1, - 1')
    @example('00', '0 - 1, - 1')
    @example('00', '0 ,0')
    @example('00', '00, ')
    @example('0 ', '00,0')
    @example('Woop Woop Sector', '864+,059 -')
    def test_create_sector(self, s, t):
        sector = None
        allowed_value_errors = ["Name string too short", "Position string too short", "Position string malformed"]

        try:
            sector = Sector(s, t)
        except ValueError as e:
            if str(e) in allowed_value_errors:
                pass
            else:
                raise e
        assume(isinstance(sector, Sector))

        result, msg = sector.is_well_formed()
        self.assertTrue(result, msg)

        sec_name = sector.sector_name()
        self.assertIsNotNone(sec_name)
        self.assertTrue('Sector' not in sec_name)

        to_string = str(sector)
        self.assertIsNotNone(to_string)


if __name__ == '__main__':
    unittest.main()
