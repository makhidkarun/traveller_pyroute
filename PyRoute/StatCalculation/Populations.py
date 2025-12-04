"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
from PyRoute.Star import Star


class Populations(object):
    def __init__(self) -> None:
        self.code = ""
        self.homeworlds: list[Star] = []
        self.count = 0
        self.population = 0

    def add_population(self, population, homeworld) -> None:
        self.count += 1
        self.population += population
        if homeworld:
            self.homeworlds.append(homeworld)

    def __lt__(self, other):
        return self.population < other.population

    def __eq__(self, other):
        if self.__hash__() != other.__hash__():
            return False
        if self.code != other.code:
            return False
        if self.count != other.count:
            return False
        if self.population != other.population:
            return False
        return self.homeworlds == other.homeworlds

    def __hash__(self) -> int:
        key = (self.code, self.count, self.population)
        return hash(key)
