import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, composite, floats, integers

from PyRoute.AreaItems.Sector import Sector


@composite
def position_string(draw):
    left = draw(text(min_size=2, alphabet='+- 0123456789'))
    right = draw(text(min_size=1, alphabet='+- 0123456789'))

    return '# ' + left + ',' + right


@composite
def sector_name(draw):
    stem = '#' + draw(text(min_size=1))
    flip = draw(floats(min_value=0.0, max_value=1.0))

    if 0.9 > flip:
        return stem + " Sector"
    return stem


@composite
def two_sectors(draw):
    sx = draw(integers(min_value=-9999, max_value=9999))
    sy = draw(integers(min_value=-9999, max_value=9999))

    tx = draw(integers(min_value=-9999, max_value=9999))
    ty = draw(integers(min_value=-9999, max_value=9999))
    manhattan = abs(sx - tx) + abs(sy - ty)
    assume(manhattan > 1)

    direction = draw(integers(min_value=0, max_value=3))

    result = {'sx': sx, 'sy': sy, 'tx': tx, 'ty': ty, 'direction': direction}

    return result


class testSector(unittest.TestCase):

    @given(sector_name(), position_string())
    @settings(
        suppress_health_check=[HealthCheck(3), HealthCheck(2)],  # suppress slow-data health check, too-much filtering
        deadline=timedelta(1000))
    @example('00', '0:,0')
    @example('#00', '#00,:')
    @example('#00', '#0A,0')
    @example('#00', '#0\x1f,0')
    @example('#00', '#0,0\x1f')
    @example('#00', '#00,0Ā')
    @example('#00', '#0-,0')
    @example('#00', '#0+,0')
    @example('#00', '#00,-')
    @example('#00', '#00,+')
    @example('#00', '#00-,0')
    @example('#00', '#00,0-')
    @example('#00', '#0 - 1, -1')
    @example('#00', '#0 -1, - 1')
    @example('#00', '#0 - 1, - 1')
    @example('#00', '#0 ,0')
    @example('#00', '# 00, ')
    @example('#0 ', '# 00,0')
    @example('# Woop Woop Sector', '# 864+,059 -')
    def test_create_sector(self, s, t):
        sector = None
        allowed_value_errors = ["Name string too short", "Position string too short", "Position string malformed",
                                "Name string should start with #", "Position string should start with #"]

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

    @given(two_sectors())
    @example({'sx': -2316, 'sy': 117, 'tx': 107, 'ty': 3057, 'direction': 1})
    def test_non_adjacent_sectors_hooked_together_are_not_ok(self, payload):
        source_pos = '# ' + str(payload['sx']) + ", " + str(payload['sy'])
        target_pos = '# ' + str(payload['tx']) + ", " + str(payload['ty'])

        source = Sector('# Source', source_pos)
        target = Sector('# Target', target_pos)

        # assert both sectors are well-formed before the hookup
        result, msg = source.is_well_formed()
        self.assertTrue(result)
        result, msg = target.is_well_formed()
        self.assertTrue(result)

        direct = payload['direction']
        if 0 == direct:
            source.coreward = target
            target.rimward = source
        elif 1 == direct:
            source.spinward = target
            target.trailing = source
        elif 2 == direct:
            source.rimward = target
            target.coreward = source
        elif 3 == direct:
            source.trailing = target
            target.spinward = source

        result, msg = source.is_well_formed()
        self.assertFalse(result, msg)
        result, msg = target.is_well_formed()
        self.assertFalse(result, msg)

    def testSectorPositionRegressions(self):
        cases = [
            ('Zarushagar', '# Zarushagar', '# -1,-1')
        ]

        for sec_name, name, position in cases:
            with self.subTest(sec_name):
                sector = Sector(name, position)
                result, _ = sector.is_well_formed()
                self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
