"""
Created on 21 Jul, 2024

@author: CyberiaResurrection
"""
import copy

from PyRoute.AllyGen import AllyGen
from PyRoute.AreaItems.AreaItem import AreaItem


class Allegiance(AreaItem):
    def __init__(self, code, name, base=False, population='Huma'):
        super(Allegiance, self).__init__(Allegiance.allegiance_name(name, code, base))
        self.code = code
        self.base = base
        self.population = population
        self._wiki_name = Allegiance.set_wiki_name(name, code, base)

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['alg_sorted']
        return state

    def __deepcopy__(self, memodict={}):
        foo = Allegiance(self.code, self.name, self.base, self.population)
        foo._wiki_name = self._wiki_name
        foo.alg_sorted = []
        foo.debug_flag = self.debug_flag
        foo.stats = copy.deepcopy(self.stats)

        return foo

    @staticmethod
    def allegiance_name(name, code, base):
        if not isinstance(name, str):
            raise ValueError("Name must be string - received " + str(name))
        if not isinstance(code, str):
            raise ValueError("Code must be string - received " + str(code))
        if 4 < len(code):
            raise ValueError("Code must not exceed 4 characters - received " + str(code))
        name = name.strip()
        if '' == name:
            raise ValueError("Name must not be empty string")
        if code.startswith('As') or "As" == AllyGen.same_align(code):
            if 5 < name.count(','):
                raise ValueError("Name " + name + ", must have at most five commas")
        else:
            if 1 < name.count(','):
                raise ValueError("Name " + name + ", must have at most one comma")
        namelen = 0
        while namelen != len(name):
            namelen = len(name)
            name = name.replace('  ', ' ')
        if base:
            return name
        names = name.split(',') if ',' in name else [name, '']
        names[0] = names[0].strip()
        names[1] = names[1].strip()
        if code.startswith('Na'):
            return '{} {}'.format(names[0], names[1])
        elif code.startswith('Cs'):
            return '{}s of the {}'.format(names[0], names[1])
        elif ',' in name:
            return '{}, {}'.format(names[0], names[1])
        return '{}'.format(name.strip())

    @staticmethod
    def set_wiki_name(name, code, base):
        if not isinstance(name, str):
            raise ValueError("Name must be string - received " + str(name))
        if not isinstance(code, str):
            raise ValueError("Code must be string - received " + str(code))
        name = name.strip()
        if '' == name:
            raise ValueError("Name must not be empty string")
        if ',' == name:
            raise ValueError("Name must not be pair of empty strings")
        if '[' in name or ']' in name:
            raise ValueError("Name must not contain square brackets - received " + name)

        names = name.split(',') if ',' in name else [name, '']
        names[0] = names[0].strip()
        names[1] = names[1].strip()
        if '' == names[0]:
            raise ValueError("First part of name string must not be an empty string itself")
        if '' == names[1] and ',' in name:
            raise ValueError("Second part of name string must not be an empty string itself")

        if code.startswith('Na'):
            return '[[{}]] {}'.format(names[0], names[1])
        elif code.startswith('Cs'):
            return '[[{}]]s of the [[{}]]'.format(names[0], names[1])
        elif ',' in name:
            if base:
                return '[[{}]]'.format(names[0])
            else:
                return '[[{}]], [[{}]]'.format(names[0], names[1])
        return '[[{}]]'.format(name)

    def __str__(self):
        return '{} ({})'.format(self.name, self.code)

    def is_unclaimed(self):
        return AllyGen.is_unclaimed(self)

    def is_wilds(self):
        return AllyGen.is_wilds(self)

    def is_client_state(self):
        return AllyGen.is_client_state(self)

    def are_allies(self, other):
        return AllyGen.are_allies(self.code, other.code)

    def is_well_formed(self):
        msg = ''
        if '' == self.name.strip():
            msg = "Allegiance name should not be empty"
            return False, msg
        if '  ' in self.name:
            msg = "Should not have successive spaces in allegiance name, " + self.name
            return False, msg
        if 1 < self.name.count(','):
            msg = "Should be at most one comma in allegiance name, " + self.name
            return False, msg

        return True, msg
