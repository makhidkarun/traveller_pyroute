"""
Created on Dec 27, 2023

@author: CyberiaResurrection
"""

from lark import Lark
import re


def dashrepl(m):
    group = m.group().replace('  ', ' ')
    return group


class StarlineParser:

    starline_grammar = r"""
    starline: position starname trade extensions nobles base zone world_alg residual?

    position: /^((0[1-9]|[1-2]\d|3[0-2])(0[1-9]|40|[1-3]\d))/

    starname: /(.{15,}) ([A-HXYa-hxy\?][0-9A-Fa-f\?][\w\?]{2,2}[0-9A-Fa-f\?][0-9A-Xa-x\?][0-9A-Ja-j\?]-[\w\?]) /

    trade: TRADECODE*
    TRADECODE: MINOR_DIEBACK | BINARY | POPCODE | MINOR_SOPHONT | OWNED_COLONY | MAJOR_SOPHONT | RESIDUAL | SINGLETON
    BINARY.3: /[A-Z][a-z]/
    POPCODE.3: /[A-Z][a-z!]{1,3}[W\d]{0,1}/
    MINOR_SOPHONT.3: /\([^\)\{\(]{1,}\)[W\d\?]{0,1}/
    MINOR_DIEBACK.3: /Di\([^\)]{1,}\)[\d]{0,1}/
    MAJOR_SOPHONT.3: /\[[^\]\{]{1,}\][W\d\?]{0,1}/
    OWNED_COLONY.3: /[OC]:[X\d\?]{0,4}/ | /[OC]:[A-Z][A-Za-z]{3,3}[-\:]{0,1}\d{4,4}/
    RESIDUAL.2: /[0-9A-Za-z?\-+*()\'\{\}\[\]]{2,}/
    SINGLETON: /[0-9AC-Za-z\+\*()?\']/

    extensions: ix ex cx | /( ) ( ) ( )/

    ix: /\{ *[ +-]?[0-6] ?\}|-/
    ex: /\([0-9A-Za-z]{3}[+-]\d\)|-/
    cx: /(\[[0-9A-Za-z]{4}[\]\}]|-)/

    nobles: /([BcCDeEfFGH]{1,5}|-| )/

    base: /([A-Z]{1,3}|-|\*)/

    zone: /([ARUFGBarufgb]|-| )[ ]{0,}/

    pbg: /[0-9X?][0-9A-FX?][0-9A-FX?]/

    residual: /(.{1,})/

    world_alg: pbg worlds allegiance
    worlds: /(\d{1,2} | |-)/

    allegiance: /[A-Z0-9?-][A-Za-z0-9?-]{1,3}/

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """

    def __init__(self):
        self.parser = Lark(self.starline_grammar, start='starline')

    def parse(self, text):
        text = re.sub(r'[\w\-]  [\w\-]', dashrepl, text)

        return self.parser.parse(text), text
