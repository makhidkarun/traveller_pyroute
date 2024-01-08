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

    def starline(self, args):
        if 3 <= len(args[2]) and 1 == len(args[3]) and '' == args[3][0].value.strip():  # Square up overspilled trade codes
            if '' == args[4][0].value and '' != args[5][0].value and '' == args[6][0].value:
                last = args[2][-1]
                mid = args[2][-2]
                args[6][0].value = args[5][0].value
                args[5][0].value = last
                args[4][0].value = mid
                args[2] = args[2][:-2]
        if '*' != args[5][0].value:
            if '' == args[4][0].value and '' != args[5][0].value:
                args[4][0].value = args[5][0].value
                args[5][0].value = args[6][0].value
            elif '' == args[6][0].value and '' != args[5][0].value:
                args[6][0].value = args[5][0].value
                args[5][0].value = args[4][0].value
                args[4][0].value = ''
        if 8 == len(args):  # If there's no residual argument
            tailend = args[7][2][0].value
            lenlast = min(4, len(tailend))
            counter = 0
            while counter < lenlast and (tailend[counter].isalnum() or '-' == tailend[counter]):
                if counter < lenlast:
                    counter += 1
            if counter < min(4, lenlast):  # if the allegiance overspills, move the overspill into the residual
                overrun = tailend[counter:]
                tailend = tailend[:counter]
                args[7][2][0].value = tailend
                newbie = Token('__ANON_14', overrun)
                args.append([newbie])
        return args

    def position(self, args):
        args[0].value = args[0].value.strip()
        return args

    def starname(self, args):
        args[0].value = args[0].value.strip()
        return args

    def trade(self, args):
        trimmed = []
        for item in args:
            trimmed.append(item.value.strip())
        return trimmed

    def extensions(self, args):
        if 1 == len(args):
            return args
        return args

    def nobles(self, args):
        args[0].value = args[0].value.strip()
        return args

    def base(self, args):
        args[0].value = args[0].value.strip()
        return args

    def zone(self, args):
        args[0].value = args[0].value.strip()
        return args

    def pbg(self, args):
        args[0].value = args[0].value.strip()
        return args

    def worlds(self, args):
        raw = args[0].value
        if 1 < len(raw):
            raw = raw.strip()
        args[0].value = raw
        return args

    def allegiance(self, args):
        args[0].value = args[0].value.strip()
        return args

    def world_alg(self, args):
        return args

    def residual(self, args):
        args[0].value = args[0].value.strip()
        return args

    def starname_transform(self, starname):
        bitz = [item for item in starname.split(' ') if 0 < len(item)]
        uwp = bitz[-1]
        bitz = bitz[:-1]
        return ' '.join(bitz), uwp

    def trade_transform(self, trade):
        codes = []

        for kid in trade:
            codes.append(kid)

        return ' '.join(codes)

    def extensions_transform(self, extensions):
        if 1 == len(extensions):  # Fallback no-extensions
            return None, None, None
        data = {}
        for kid in extensions:
            val = str(kid.data)
            data[val] = kid.children[0].value
            data[val] = self.boil_down_double_spaces(data[val])

        return data['ix'], data['ex'], data['cx']

    def world_alg_transform(self, world_alg):
        return world_alg[0][0].value, world_alg[1][0].value, world_alg[2][0].value

    def transform(self, tree):
        tree = self._transform_tree(tree)
        parsed = {'ix': None, 'ex': None, 'cx': None, 'residual': ''}

        parsed['position'] = tree[0][0].value
        parsed['name'], parsed['uwp'] = self.starname_transform(tree[1][0].value)
        parsed['trade'] = self.trade_transform(tree[2])
        parsed['ix'], parsed['ex'], parsed['cx'] = self.extensions_transform(tree[3])
        parsed['nobles'] = tree[4][0].value
        parsed['base'] = tree[5][0].value
        parsed['zone'] = tree[6][0].value
        parsed['pbg'], parsed['worlds'], parsed['allegiance'] = self.world_alg_transform(tree[7])
        if 9 == len(tree):
            parsed['residual'] = tree[8][0].value

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
