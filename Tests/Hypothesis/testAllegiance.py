import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, composite, floats, booleans

from PyRoute.AreaItems.Allegiance import Allegiance


@composite
def text_or_none(draw, alphabet=None) -> composite:
    choice = draw(floats(min_value=0.0, max_value=1.0))

    if 0.8 < choice:
        return None

    if alphabet is not None:
        return draw(text(alphabet=alphabet))
    return draw(text())


@composite
def text_starts_with(draw, starts="Na", min_size=2, max_size=4) -> composite:
    min_size = max(2, min_size)
    max_size = min(4, max_size)
    max_size = max(max_size, min_size)
    start_len = len(starts)

    add = draw(text(min_size=min_size - start_len, max_size=max_size - start_len))

    return starts + add


@composite
def text_flanking_comma(draw) -> composite:
    before = draw(text(min_size=1, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    after = draw(text(min_size=1, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))

    return before + ',' + after


class testAllegiance(unittest.TestCase):

    @given(text_or_none(), text_or_none(), booleans())
    @settings(max_examples=1100)
    @example(None, '', True)
    @example(None, '', False)
    @example(None, None, True)
    @example(None, None, False)
    @example('', '00000', False)
    @example('', '00000', True)
    @example('', '', True)
    @example('', '', False)
    @example('0,,', '00', True)
    @example('0,,', '00', False)
    @example('[', '', False)
    def test_allegiance_creation_without_specified_population(self, name, code, base) -> None:
        alg = None
        allowed = [
            "Name must be string - received",
            "Code must be string - received",
            "Code must not exceed 4 characters - received",
            "Name must not be empty string",
            "must have at most one comma",
            "Name must not contain square brackets",
            'First part of name string must not be an empty string itself',
            'Second part of name string must not be an empty string itself',
            'Name must not be pair of empty strings'
        ]

        try:
            alg = Allegiance(code, name, base)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e

        assume(alg is not None)

        as_str = str(alg)
        self.assertIsNotNone(as_str)
        title = alg.wiki_title()
        self.assertIsNotNone(title)
        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)

    @given(
        text(min_size=3, alphabet=',0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'),
        text_starts_with(starts="Na"),
        booleans()
    )
    @example('00 ', 'Na', False)
    def test_allegiance_creation_with_nonaligned_code(self, name, code, base) -> None:
        assume('' != name.strip())
        alg = None
        allowed = [
            'First part of name string must not be an empty string itself',
            'Name must not contain square brackets',
            'Second part of name string must not be an empty string itself',
            'must have at most one comma'
        ]

        try:
            alg = Allegiance(code, name, base)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e

        assume(alg is not None)

        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)

    @given(
        text(min_size=3, alphabet=',0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'),
        text_starts_with(starts="Cs"),
        booleans()
    )
    @example('00 ', 'Cs', False)
    @example('0  ', 'Cs', True)
    @example('0  0', 'Cs', False)
    @example('0   0', 'Cs', False)
    @example('00[', 'Cs', False)
    @example('0,,', 'Cs', False)
    def test_allegiance_creation_with_client_state_code(self, name, code, base) -> None:
        assume('' != name.strip())
        alg = None

        allowed = [
            'Name must not contain square brackets',
            'First part of name string must not be an empty string itself',
            'Second part of name string must not be an empty string itself',
            'must have at most one comma'
        ]

        try:
            alg = Allegiance(code, name, base)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e

        assume(alg is not None)

        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)

    @given(
        text_flanking_comma(),
        text(min_size=2, max_size=4),
        booleans()
    )
    def test_allegiance_creation_with_comma_in_name(self, name, code, base) -> None:
        assume('' != name.strip())
        alg = None

        allowed = [
            "Name must not be pair of empty strings",
            'First part of name string must not be an empty string itself',
            'Second part of name string must not be an empty string itself',
            'Name must not contain square brackets'
        ]

        try:
            alg = Allegiance(code, name, base)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e

        assume(alg is not None)

        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)

    @given(
        text_or_none(alphabet=',0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'),
        text_starts_with(starts="Na"),
        booleans()
    )
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], max_examples=1100)
    @example(None, None, True)
    @example(None, None, False)
    @example('', None, True)
    @example('', None, False)
    @example(',', '', False)
    @example('0,', '', False)
    @example(',0', '', False)
    @example('[,0', 'Na', False)
    @example('],0', 'Na', False)
    def test_set_wiki_name(self, name, code, base) -> None:
        allowed = [
            "Name must be string - received",
            "Code must be string - received",
            "Code must not exceed 4 characters - received",
            "Name must not be empty string",
            "Name must have at most one comma",
            "Name must not be pair of empty strings",
            "First part of name string must not be an empty string itself",
            "Second part of name string must not be an empty string itself",
            "Name must not contain square brackets"
        ]

        wiki_name = None
        try:
            wiki_name = Allegiance.set_wiki_name(name, code, base)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e

        assume(wiki_name is not None)
        self.assertNotIn('[]', wiki_name, "Empty square brackets not allowed in wiki name")

    def test_string_representation(self) -> None:
        alg = Allegiance("Test", "Test Allegiance Plz Ignore")

        expected = 'Test Allegiance Plz Ignore (Test)'
        self.assertEqual(expected, str(alg), "Unexpected string representation")
        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)

    def test_long_aslan_allegiance(self) -> None:
        code = 'AsT0'
        name = 'Aslan Hierate, Tlaukhu control, Yerlyaruiwo (1), Hrawoao (13), Eisohiyw (14), Ferekhearl (19)'

        alg = Allegiance(code, name)
        expected = 'Aslan Hierate, Tlaukhu control (AsT0)'
        self.assertEqual(expected, str(alg), "Unexpected string representation")
        result, msg = alg.is_well_formed()
        self.assertTrue(result, msg)


if __name__ == '__main__':
    unittest.main()
