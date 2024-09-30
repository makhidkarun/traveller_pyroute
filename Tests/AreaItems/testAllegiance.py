import unittest

from PyRoute.AreaItems.Allegiance import Allegiance


class testAllegiance(unittest.TestCase):

    def testAslanAllegianceNotBeginningWithAs(self):
        code = "A8"
        name = "Aslan Hierate, Tlaukhu control, Seieakh (9), Akatoiloh (18), We'okurir (29)"
        pop = "Asla"

        alleg = Allegiance(code, name, False, pop)

        result, msg = alleg.is_well_formed()
        self.assertTrue(result, msg)
