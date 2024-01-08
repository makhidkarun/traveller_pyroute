"""
Created on Dec 27, 2023

@author: CyberiaResurrection
"""

from lark import Transformer, Token


class StarlineTransformer(Transformer):

    strip_list = [
        'pbg',
        'nobles',
        'zone',
        'allegiance',
        'base',
        'residual'
    ]

    def __init__(self, visit_tokens: bool = True, raw=None):
        super().__init__(visit_tokens)
        self.raw = raw

    def starname(self, starname):
        bitz = [item for item in starname.split(' ') if 0 < len(item)]
        uwp = bitz[-1]
        bitz = bitz[:-1]
        return [' '.join(bitz), uwp]

    def trade(self, trade):
        codes = []

        for kid in trade.children:
            codes.append(kid.value)

        return ' '.join(codes)

    def extensions(self, extensions):
        if 1 == len(extensions.children):  # Fallback no-extensions
            return None, None, None
        data = {}
        for kid in extensions.children:
            val = str(kid.data)
            data[val] = kid.children[0].value
            data[val] = self.boil_down_double_spaces(data[val])

        return data['ix'], data['ex'], data['cx']

    def world_alg(self, world_alg):
        data = {}
        for kid in world_alg.children:
            val = str(kid.data)
            data[val] = kid.children[0].value
        if 1 < len(data['worlds']):
            data['worlds'] = data['worlds'].strip()
        return data['pbg'], data['worlds'], data['allegiance']

    def transform(self, tree):
        parsed = {'ix': None, 'ex': None, 'cx': None, 'residual': ''}
        self.trim_raw_string(tree)

        for kid in tree.children:
            if isinstance(kid, Token):
                parsed['trade'].append(kid.value)
                continue

            dataval = str(kid.data)
            if 'starname' == dataval:
                rawval = kid.children[0].value
                result = self.starname(rawval)
                parsed['name'] = result[0]
                parsed['uwp'] = result[1]
            elif 'trade' == dataval:
                parsed['trade'] = self.trade(kid)
            elif 'extensions' == dataval:
                parsed['ix'], parsed['ex'], parsed['cx'] = self.extensions(kid)
            elif 'world_alg' == dataval:
                parsed['pbg'], parsed['worlds'], parsed['allegiance'] = self.world_alg(kid)
            else:
                rawval = kid.children[0].value
                parsed[dataval] = rawval

        self.square_up_overspilled_trade_codes(parsed)

        for line in self.strip_list:
            parsed[line] = parsed[line].strip()

        no_extensions = parsed['ix'] is None and parsed['ex'] is None and parsed['cx'] is None
        ex_ix = parsed['ix'] if parsed['ix'] is not None else ' '
        ex_ix = self.boil_down_double_spaces(ex_ix)
        extensions = (ex_ix) + ' ' + \
                     (parsed['ex'] if parsed['ex'] is not None else ' ') + ' ' + \
                     (parsed['cx'] if parsed['cx'] is not None else ' ')

        spacer = ' ' if no_extensions else None
        if no_extensions:
            extensions = ''

        # Currently aiming to drop-in replace the starline regex output
        data = [parsed['position'], parsed['name'], parsed['uwp'], parsed['trade'], extensions, parsed['ix'], parsed['ex'], parsed['cx'], spacer, spacer, spacer, parsed['nobles'], parsed['base'], parsed['zone'], parsed['pbg'], parsed['worlds'], parsed['allegiance'], parsed['residual']]

        return data

    def square_up_overspilled_trade_codes(self, parsed):
        if parsed['ix'] is not None or parsed['ex'] is not None or parsed['cx'] is not None:
            return
        tradebitz = parsed['trade'].split(' ')
        if 3 > len(tradebitz):
            return
        if '' != parsed['nobles'].strip():
            return
        parsed['zone'] = parsed['base']
        parsed['base'] = tradebitz[-1]
        parsed['nobles'] = tradebitz[-2]
        tradebitz = tradebitz[:-2]
        parsed['trade'] = ' '.join(tradebitz)
        self.raw = parsed['nobles'] + ' ' + parsed['base'] + ' ' + self.raw

    def trim_raw_string(self, tree):
        assert self.raw is not None, "Raw string not supplied before trimming"
        strip_list = ['position', 'starname', 'trade', 'extensions']

        for kid in tree.children:
            dataval = str(kid.data)
            if dataval not in strip_list:
                continue
            if 'trade' == dataval:
                for item in kid.children:
                    rawval = item.value
                    self.raw = self.raw.replace(rawval, '', 1)
            elif 'extensions' == dataval:
                if 1 == len(kid.children):
                    rawval = kid.children[0].value
                    self.raw = self.raw.replace(rawval, '', 1)
                else:
                    for item in kid.children:
                        rawval = item.children[0].value
                        self.raw = self.raw.replace(rawval, '', 1)
            else:
                rawval = kid.children[0].value
                self.raw = self.raw.replace(rawval, '', 1)
        self.raw = self.raw.lstrip()

    @staticmethod
    def boil_down_double_spaces(dubbel):
        return " ".join(dubbel.split())
