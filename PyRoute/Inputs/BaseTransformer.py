"""
Created on Nov 07, 2024

@author: CyberiaResurrection
"""
import re
from typing import Optional

from lark import Transformer, Token, Tree


class BaseTransformer(Transformer):

    strip_list = [
        'pbg',
        'nobles',
        'zone',
        'allegiance',
        'base',
        'residual'
    ]

    star_classes = ['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI', 'D']
    zone_codes = 'ARUFGB- '
    zone_active = 'ARUFGB'

    def __init__(self, visit_tokens: bool = True, raw=None):
        super().__init__(visit_tokens)
        self.raw = raw.strip('\n')
        self.crankshaft = False

    def starline(self, args) -> list[list]:
        # These are the as-parsed values, and we're confirming the values as needed
        trade = args[2]
        extensions = args[3]
        nobles = args[4].children[0][0]
        base = args[4].children[1][0]
        zone = args[4].children[2][0]

        tradelen = sum([len(item) for item in trade]) + len(trade) - 1
        # Square up overspilled trade codes
        if 16 < tradelen and 3 <= len(trade) and 1 == len(extensions) and '' == extensions[0].value.strip() and \
                '-' == nobles.value and 3 == len(base.value) and '-' == zone.value:
            move_fwd = base.value.isdigit()  # Will base code still make sense as PBG?
            if move_fwd:
                last = trade[-1]
                mid = trade[-2]
                args[4].children[2][0].value = base.value
                args[4].children[1][0].value = last
                args[4].children[0][0].value = mid
                args[2] = trade[:-2]

        args[5] = args[5][:3]
        return args

    def position(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def starname(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def trade(self, args) -> list[str]:
        trimmed = []
        for item in args:
            rawval = BaseTransformer.boil_down_double_spaces(item.value.strip())
            trimmed.append(rawval)
        return trimmed

    def extensions(self, args) -> list[list]:
        return args

    def nobles(self, args) -> list[list]:
        return self._nbz_core(args)

    def base(self, args) -> list[list]:
        return self._nbz_core(args)

    def zone(self, args) -> list[list]:
        return self._nbz_core(args)

    def _nbz_core(self, args) -> list[list]:
        args[0].value = args[0].value.strip()
        if '' == args[0].value:
            args[0].value = '-'
        return args

    def pbg(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def worlds(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def allegiance(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def world_alg(self, args) -> list[list]:
        return args

    def residual(self, args) -> list[list]:
        return self._strip_arg_0_value(args)

    def _strip_arg_0_value(self, args) -> list[list]:
        args[0].value = args[0].value.strip()
        return args

    def starname_transform(self, starname: str) -> tuple[str, str]:
        bitz = [item for item in starname.split(' ')]  # pragma: no mutate
        bitz = [item for item in bitz if 0 < len(item)]
        uwp = bitz[-1]
        bitz = bitz[:-1]
        return ' '.join(bitz), uwp

    def trade_transform(self, trade) -> str:
        codes = []

        for kid in trade:
            codes.append(kid)

        return ' '.join(codes)

    def extensions_transform(self, extensions) -> tuple[Optional[str], Optional[str], Optional[str]]:
        data: dict[str, Optional[str]] = {'ix': None, 'ex': None, 'cx': None}
        if not isinstance(extensions, str):
            for kid in extensions:
                if isinstance(kid, Token):
                    val = str(kid.type)
                    data[val] = kid.value
                else:
                    val = str(kid.data)
                    data[val] = kid.children[0].value
                if isinstance(data[val], str):
                    data[val] = self.boil_down_double_spaces(data[val])  # type:ignore[arg-type]

        return data['ix'], data['ex'], data['cx']

    def world_alg_transform(self, world_alg) -> tuple[str, str, str]:
        if 1 == len(world_alg):
            return world_alg[0][0], world_alg[0][1], world_alg[0][2]
        if '' == world_alg[1][0].value.strip():
            world_alg[1][0].value = '0'
        return world_alg[0][0].value, world_alg[1][0].value, world_alg[2][0].value

    def transform(self, tree) -> list[Optional[str]]:
        self.crankshaft = '' == tree.children[4].children[0].children[0].value.strip() and '-' == tree.children[4].children[
            1].children[0].value.strip() and '' == tree.children[4].children[2].children[0].value.strip()
        self.crankshaft = self.crankshaft and 1 == self.raw.count(' -') and 1 == self.raw.count('-   ')
        tree = self.preprocess_trade_and_extensions(tree)
        tree = self.preprocess_tree_suspect_empty_trade_code(tree)
        tree = self._transform_tree(tree)
        parsed: dict[str, Optional[str]] = {'residual': ''}

        parsed['position'] = tree[0][0].value
        parsed['name'], parsed['uwp'] = self.starname_transform(tree[1][0].value)
        parsed['trade'] = self.trade_transform(tree[2])
        parsed['ix'], parsed['ex'], parsed['cx'] = self.extensions_transform(tree[3])
        parsed['nobles'] = tree[4].children[0][0].value
        parsed['base'] = tree[4].children[1][0].value
        parsed['zone'] = tree[4].children[2][0].value
        parsed['pbg'], parsed['worlds'], parsed['allegiance'] = self.world_alg_transform(tree[5])
        if 7 == len(tree):
            parsed['residual'] = tree[6][0].value

        self.trim_raw_string(parsed)
        rawbitz = self.trim_raw_bitz(parsed)
        parsed = self.square_up_parsed_zero(rawbitz[0], parsed)
        parsed = self.square_up_allegiance_overflow(parsed)

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
        data = [parsed['position'], parsed['name'], parsed['uwp'], parsed['trade'], extensions, parsed['ix'],
                parsed['ex'], parsed['cx'], spacer, spacer, spacer, parsed['nobles'], parsed['base'],
                parsed['zone'].upper() if parsed['zone'] is not None else '', parsed['pbg'], parsed['worlds'], parsed['allegiance'], parsed['residual']]

        return data

    def preprocess_trade_and_extensions(self, tree) -> Tree:
        trade = tree.children[2]
        extensions = tree.children[3]
        ix_reg = r'\{ *[+-]?[0-6] ?\}$'
        soc_reg = r'[ ]\[[0-9A-Za-z]{4}\][ ]'

        # if extensions are single blank child, look to trade for spillover
        if 1 == len(extensions.children) and '' == extensions.children[0].value.strip() and 1 == len(trade.children):
            tradeval = trade.children[0].value.strip() + ' '
            soc_match = re.search(soc_reg, tradeval)
            if soc_match is not None:
                posn = soc_match.regs[0]
                nu_social = Tree(Token('RULE', 'cx'), [Token('__ANON_3', tradeval[posn[0] + 1:posn[1] - 1])])
                tradeval = tradeval[0:posn[0]] + tradeval[posn[1]:]
                trade.children[0].value = tradeval
                tree.children[3].children[0] = nu_social

        # If trade has importance-extension child, we need to fix it
        counter = -1
        ix_found = False
        for kid in trade.children:
            counter += 1
            ix_match = re.match(ix_reg, kid.value)
            if ix_match is not None:
                ix_found = True
                break

        if not ix_found:
            return tree

        bitz = trade.children[counter:]
        bitz[0].type = 'ix'
        if 1 < len(bitz):
            bitz[1].type = 'ex'
        if 2 < len(bitz):
            bitz[2].type = 'cx'
        trade.children = trade.children[:counter]
        extensions.children.extend(bitz)

        return tree

    def _is_noble(self, noble_string):
        noble = "BCcDEeFfGH"
        return all(char in noble for char in noble_string)

    def is_zone(self, zone_string) -> bool:
        if 1 != len(zone_string):
            return False
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        return zone_string[0] in ParseStarInput.valid_zone

    def preprocess_tree_suspect_empty_trade_code(self, tree) -> Tree:
        if 1 != len(tree.children[2].children):
            return tree
        if 1 != len(tree.children[3].children):
            return tree
        if 5 < len(tree.children[2].children[0]):
            return tree
        if 5 != len(tree.children[3].children[0]):
            return tree
        all_noble = self._is_noble(tree.children[2].children[0])
        if not all_noble:
            return tree
        if self.is_zone(tree.children[4].children[2].children[0].value.strip()):
            return tree
        tree.children[4].children[2].children[0].value = tree.children[4].children[1].children[0].value
        tree.children[4].children[1].children[0].value = tree.children[4].children[0].children[0].value
        tree.children[4].children[0].children[0].value = tree.children[2].children[0].value
        tree.children[2].children[0].value = ""

        return tree

    @staticmethod
    def _calc_trade_overrun(children, raw):
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        trade_ext = ''
        overrun = 0
        # first check whether trade codes are straight up aligned
        for item in children:
            trade_ext += item.value + ' '
        if trade_ext in raw:
            return 0
        num_child = len(children) - 1
        gubbinz = [item.value for item in children]
        nobles = [item for item in gubbinz if ParseStarInput.can_be_nobles(item)]
        if 0 == len(nobles):
            return 0
        if 1 < len(gubbinz) and ParseStarInput.can_be_nobles(gubbinz[-2]) and ParseStarInput.can_be_base(gubbinz[-1]):
            return 2

        for k in range(num_child, 1, -1):
            trade_bar = " ".join(gubbinz[:k])
            if trade_bar in raw:
                overrun = len(children) - k
                for j in range(k, len(children)):
                    if not ParseStarInput.can_be_nobles(gubbinz[j]):
                        overrun -= 1
                return overrun
        trade_ext = ' '
        i = 0
        for item in children:  # Dig out the largest left-subset of trade children that are in the raw string
            trade_ext += item.value + ' '
            if trade_ext in raw:  # if it worked with one space appended, try a second space
                substr = False
                if i < num_child:
                    substr = children[i + 1].value.rfind(item.value) == (len(children[i + 1].value) - len(item.value))

                if not substr:
                    trade_ext += ' '
                    if trade_ext not in raw:  # if it didn't, drop the second space
                        trade_ext = trade_ext[:-1]
            else:  # if appending the space didn't work, try without it
                trade_ext = trade_ext[:-1]
            # after all that, if we've overrun (such as a nobles code getting transplanted), throw hands up and move on
            if trade_ext not in raw:
                overrun += 1
            i += 1
        return overrun

    def trim_raw_string(self, tree) -> None:
        assert self.raw is not None, "Raw string not supplied before trimming"
        strip_list = ['position', 'name', 'uwp', 'trade', 'ix', 'ex', 'cx']  # pragma: no mutate

        for dataval in strip_list:
            if dataval not in tree:
                continue
            rawval = tree[dataval]
            if rawval is not None:
                counter = 0
                if rawval.startswith('{ '):
                    while counter < 4:
                        oldlen = len(self.raw)  # pragma: no mutate
                        self.raw = self.raw.replace('{  ', '{ ')
                        self.raw = self.raw.replace('  }', ' }')
                        if oldlen == len(self.raw):
                            break
                        counter += 1

                index = self.raw.find(rawval)
                self.raw = self.raw.replace(rawval, '', 1)
                if -1 != index:
                    self.raw = self.raw[index:]
                    continue
                elif 'trade' != dataval:
                    continue
                # special-case trade-code removal
                else:
                    bitz = rawval.split()
                    for valbit in bitz:
                        index = self.raw.find(valbit)
                        self.raw = self.raw.replace(valbit, '', 1)
                        if -1 != index:
                            self.raw = self.raw[index:]

    def square_up_parsed_zero(self, rawstring, parsed) -> dict:
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        bitz = [item for item in rawstring.split(' ') if '' != item]
        if 3 == len(bitz) and bitz[0] == parsed['nobles'] and bitz[1] == parsed['base'] and bitz[2] == parsed['zone']:
            return parsed
        if 2 == len(bitz) and "" == parsed['zone']:
            if 2 < len(bitz[0]):  # bitz[0] can only possibly be nobles, so return
                return parsed
            if 1 < len(bitz[1]):  # if bitz[1] is more than one char, it can't be a trade zone, so return
                return parsed
            non_noble = [item for item in bitz[0] if item not in ParseStarInput.valid_nobles]
            if 0 < len(non_noble):  # If one or more chars in bitz[0] is not a valid noble call, then we have a base code and trade zone
                parsed['zone'] = parsed['base']
                parsed['base'] = parsed['nobles']
                parsed['nobles'] = ''
                return parsed
        if 3 == len(bitz):
            parsed['nobles'] = bitz[0]
            parsed['base'] = bitz[1]
            parsed['zone'] = bitz[2]
            return parsed
        if 2 == len(bitz) and '*' != parsed['base']:
            bit_one_zone_code = bitz[1].upper() in self.zone_codes
            # bit_zero_empty = '-' == bitz[0] or '' == bitz[0]
            bit_zero_forced_noble = bitz[0].isalpha() and not bitz[0].isupper()
            if 1 < len(bitz[1]) or not bit_one_zone_code:  # if second bit won't fit as a trade zone, then we have nobles and base
                parsed['nobles'] = bitz[0]
                parsed['base'] = bitz[1]
                parsed['zone'] = ''
                return parsed
            if bit_zero_forced_noble:  # if bitz[0] doesn't fit as a base code, have nobles and base
                parsed['nobles'] = bitz[0]
                parsed['base'] = bitz[1]
                parsed['zone'] = ''
                return parsed
            if not rawstring.endswith('   ') and 4 > len(bitz[0]):
                parsed['nobles'] = ''
                parsed['base'] = bitz[0]
                parsed['zone'] = bitz[1]
                return parsed
            if rawstring.startswith('   '):
                if 4 > len(bitz[0]):
                    parsed['nobles'] = ''
                    parsed['base'] = bitz[0]
                    parsed['zone'] = bitz[1]
                    return parsed
            else:
                parsed['nobles'] = bitz[0]
                parsed['base'] = bitz[1]
                parsed['zone'] = ''
        return parsed

    def _square_up_star_codes(self, rawbitz):
        foobitz = [item for item in rawbitz if '' != item]
        trimbitz = []
        num_bitz = len(foobitz)
        for i in range(0, num_bitz):
            item = foobitz[i]
            if '' == item:
                continue
            if 0 < i < num_bitz - 1:
                next_item = foobitz[i + 1]
                if next_item in self.star_classes:
                    item += ' ' + next_item
                    foobitz[i + 1] = ''
            trimbitz.append(item)

        return trimbitz

    def square_up_allegiance_overflow(self, parsed) -> dict:
        alleg = parsed['allegiance']

        if alleg.startswith('----') and 4 <= len(alleg):
            parsed['allegiance'] = '----'
            parsed['residual'] = alleg[4:] + parsed['residual']
        elif alleg.startswith('--') and 4 <= len(alleg):
            parsed['allegiance'] = '--'
            parsed['residual'] = alleg[2:] + ' ' + parsed['residual']
        else:
            counter = 0
            while counter < len(alleg) and (alleg[counter].isalnum() or '-' == alleg[counter] or '?' == alleg[counter]) and 4 > counter:
                counter += 1  # pragma: no mutate
            if counter < len(alleg):
                spacer = ' ' if parsed['residual'] != '' else ''
                parsed['allegiance'] = alleg[:counter]
                parsed['residual'] = alleg[counter:] + spacer + parsed['residual']
        return parsed

    def trim_raw_bitz(self, parsed) -> str:
        pbg = ' ' + parsed['pbg'] + ' '
        rawbitz = self.raw.split(pbg)
        oldlen = len(rawbitz)
        if 1 == oldlen:
            rawbitz.append('')
        if 2 < oldlen:
            collide = self._check_raw_collision(parsed)
            first = pbg.join(rawbitz[:-1]) if not collide else pbg.join(rawbitz[:-2])
            second = rawbitz[-1] if not collide else pbg.join(rawbitz[-2:])
            repack = []
            repack.append(first)
            repack.append(second)
            rawbitz = repack
        rawbitz[0] += ' '
        rawbitz[1] = ' ' + rawbitz[1]

        return rawbitz

    def _check_raw_collision(self, parsed):
        if parsed['pbg'] == parsed['worlds']:
            return True
        if parsed['pbg'] == parsed['allegiance']:
            return True
        return parsed['pbg'] == parsed['residual']

    @staticmethod
    def boil_down_double_spaces(dubbel: str) -> str:
        return " ".join(dubbel.split())
