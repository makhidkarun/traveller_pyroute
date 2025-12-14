from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Star import Star
from PyRoute.TradeBalance import TradeBalance
from Tests.baseTest import baseTest


class testTradeBalance(baseTest):

    def setUp(self) -> None:
        self.reset_logging()

    def test_trade_balance_bad_stat_field(self) -> None:
        msg = None

        try:
            TradeBalance()
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Stat_field must be a string', msg)

    def test_trade_balance_bad_galaxy(self) -> None:
        msg = None

        try:
            TradeBalance(stat_field='passengers')
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Region must be an Galaxy', msg)

    def test_trade_balance_bad_field(self) -> None:
        msg = None

        try:
            TradeBalance(stat_field='passengers', region=Galaxy(8), field=None)
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Target field must be a string', msg)

    def test_trade_balance_add_success(self) -> None:
        foo = TradeBalance(stat_field='passengers', region=Galaxy(8))
        self.assertEqual(0, len(foo), "Empty TradeBalance should have zero elements")
        key = ('foo', 'bar')
        foo[key] = 1
        self.assertEqual(1, len(foo), "TradeBalance should have 1 element")
        self.assertEqual(1, foo[key])

    def test_log_odd_trade_unit(self) -> None:
        core = Sector('# Core', '# 0, 0')
        dagu = Sector('# Dagudashaag', '# -1, 0')

        star1 = Star()
        star1.sector = core

        star2 = Star()
        star2.sector = dagu

        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))
        foo.log_odd_unit(star1, star2)
        self.assertEqual(1, len(foo), 'TradeBalance should have one element')
        self.assertEqual(1, sum(foo.values()), 'TradeBalance should have unit sum')
        self.assertEqual(0, core.stats.tradeExt, 'Core sector should have no external trade')
        self.assertEqual(0, dagu.stats.tradeExt, 'Dagudashaag sector should have no external trade')

        foo.log_odd_unit(star1, star2)
        self.assertEqual(1, len(foo), 'TradeBalance should have one element')
        self.assertEqual(0, sum(foo.values()), 'TradeBalance should have zero sum')
        self.assertEqual(1, core.stats.tradeExt, 'Core sector should have unit external trade')
        self.assertEqual(1, dagu.stats.tradeExt, 'Dagudashaag sector should have unit external trade')

    def test_single_unit_imbalance(self) -> None:
        core = Sector('# Core', '# 0, 0')
        dagu = Sector('# Dagudashaag', '# -1, 0')
        forn = Sector('# Fornast', '# 0, -1')

        star1 = Star()
        star1.sector = core

        star2 = Star()
        star2.sector = dagu

        star3 = Star()
        star3.sector = forn

        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        tuple1 = ('Core', 'Dagudashaag')
        tuple2 = ('Core', 'Fornast')
        tuple3 = ('Dagudashaag', 'Fornast')
        update_dict = {tuple1: 2, tuple2: 3, tuple3: 4}
        foo.update(update_dict)

        exp_imbal = {'Core': 5, 'Dagudashaag': 6, 'Fornast': 7}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

    def test_is_balanced_empty(self) -> None:
        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))
        foo.is_balanced()

    def test_is_balanced_un_compensated_multilateral(self) -> None:
        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))

        key = ('foo', 'bar')
        foo[key] = 1
        msg = None
        try:
            foo.is_balanced()
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Uncompensated multilateral passenger imbalance present in sectors', msg)

    def test_is_balanced_uncompensated_bilateral(self) -> None:
        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))

        key = ('foo', 'bar')
        foo[key] = 2

        msg = None
        try:
            foo.is_balanced()
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Uncompensated passenger imbalance present', msg)

    def test_multilateral_balance_empty(self) -> None:
        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

        foo.multilateral_balance()
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

    def test_multilateral_balance_not_imbalanced(self) -> None:
        foo = TradeBalance(stat_field='tradeExt', region=Galaxy(8))
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        key = ('foo', 'bar')
        foo[key] = 1

        foo.multilateral_balance()
        exp_imbal = {'bar': 1, 'foo': 1}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

    def test_multilateral_balance_imbalanced_1(self) -> None:
        core = Sector('# Core', '# 0, 0')
        dagu = Sector('# Dagudashaag', '# -1, 0')
        forn = Sector('# Fornast', '# 0, -1')
        mass = Sector('# Massilia', '# -1, -1')
        delp = Sector('# Delphi', '# -1, -2')

        star1 = Star()
        star1.sector = core

        star2 = Star()
        star2.sector = dagu

        star3 = Star()
        star3.sector = forn

        star4 = Star()
        star4.sector = mass

        star5 = Star()
        star5.sector = delp

        galaxy = Galaxy(8)
        galaxy.sectors['Core'] = core
        galaxy.sectors['Dagudashaag'] = dagu
        galaxy.sectors['Fornast'] = forn
        galaxy.sectors['Massilia'] = mass
        galaxy.sectors['Delphi'] = delp
        foo = TradeBalance(stat_field='tradeExt', region=galaxy)
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        tuple1 = ('Core', 'Dagudashaag')
        tuple2 = ('Core', 'Fornast')
        tuple3 = ('Massilia', 'Dagudashaag')
        tuple4 = ('Massilia', 'Fornast')
        tuple5 = ('Delphi', 'Massilia')
        update_dict = {tuple2: 1, tuple1: 1, tuple3: 1, tuple4: 2, tuple5: 1}
        foo.update(update_dict)
        exp_imbal = {'Core': 2, 'Dagudashaag': 2, 'Delphi': 1, 'Fornast': 3, 'Massilia': 4}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

        exp_logs = [
            "DEBUG:PyRoute.TradeBalance:Iteration 1, sector balance {'Core': 0, "
            "'Fornast': 1, 'Dagudashaag': 0, 'Massilia': 2, 'Delphi': 1}",
            "DEBUG:PyRoute.TradeBalance:Iteration 2, sector balance {'Core': 0, "
            "'Fornast': 0, 'Dagudashaag': 0, 'Massilia': 0, 'Delphi': 0}"
        ]
        logger = foo.logger
        logger.manager.disable = 0

        with self.assertLogs(logger, "DEBUG") as logs:
            foo.multilateral_balance()
            self.assertEqual(exp_logs, logs.output)
        exp_imbal = {'Core': 0, 'Dagudashaag': 0, 'Delphi': 0, 'Fornast': 0, 'Massilia': 0}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        self.assertEqual(1, core.stats.tradeExt)
        self.assertEqual(0, dagu.stats.tradeExt)
        self.assertEqual(0, forn.stats.tradeExt)
        self.assertEqual(2, mass.stats.tradeExt)
        self.assertEqual(0, delp.stats.tradeExt)

        foo.is_balanced()

        exp_dict = {('Core', 'Dagudashaag'): 0,
                    ('Core', 'Fornast'): 0,
                    ('Delphi', 'Massilia'): 0,
                    ('Massilia', 'Dagudashaag'): 0,
                    ('Massilia', 'Fornast'): 0}
        self.assertEqual(exp_dict, dict(foo))

    def test_multilateral_balance_imbalanced_2(self) -> None:
        core = Sector('# Core', '# 0, 0')
        dagu = Sector('# Dagudashaag', '# -1, 0')
        forn = Sector('# Fornast', '# 0, -1')
        mass = Sector('# Massilia', '# -1, -1')

        star1 = Star()
        star1.sector = core

        star2 = Star()
        star2.sector = dagu

        star3 = Star()
        star3.sector = forn

        star4 = Star()
        star4.sector = mass

        galaxy = Galaxy(8)
        galaxy.sectors['Core'] = core
        galaxy.sectors['Dagudashaag'] = dagu
        galaxy.sectors['Fornast'] = forn
        galaxy.sectors['Massilia'] = mass
        foo = TradeBalance(stat_field='tradeExt', region=galaxy)
        exp_imbal = {}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        tuple1 = ('Core', 'Dagudashaag')
        tuple2 = ('Core', 'Fornast')
        tuple3 = ('Massilia', 'Dagudashaag')
        tuple4 = ('Massilia', 'Fornast')
        update_dict = {tuple1: 1, tuple2: 1, tuple3: 1, tuple4: 1}
        foo.update(update_dict)
        exp_imbal = {'Core': 2, 'Dagudashaag': 2, 'Fornast': 2, 'Massilia': 2}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

        exp_logs = [
            'DEBUG:PyRoute.TradeBalance:Iteration 1, sector balance {\'Core\': 0, \'Dagudashaag\': 0, \'Fornast\': 0, \'Massilia\': 0}'
        ]
        logger = foo.logger
        logger.manager.disable = 0

        with self.assertLogs(logger, "DEBUG") as logs:
            foo.multilateral_balance()
            self.assertEqual(exp_logs, logs.output)
        exp_imbal = {'Core': 0, 'Dagudashaag': 0, 'Fornast': 0, 'Massilia': 0}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())
        self.assertEqual(1, core.stats.tradeExt)
        self.assertEqual(0, dagu.stats.tradeExt)
        self.assertEqual(0, forn.stats.tradeExt)
        self.assertEqual(1, mass.stats.tradeExt)

        foo.is_balanced()

        exp_dict = {('Core', 'Dagudashaag'): 0,
                    ('Core', 'Fornast'): 0,
                    ('Massilia', 'Dagudashaag'): 0,
                    ('Massilia', 'Fornast'): 0}
        self.assertEqual(exp_dict, dict(foo))

    def test_multilateral_balance_imbalanced_3(self) -> None:
        sec1 = Sector('# 8cVH', '# 0, 0')
        sec2 = Sector('# idhC2-TNs', '# 0, 0')
        sec3 = Sector('# hnjMin', '# 0, 0')

        galaxy = Galaxy(8)
        galaxy.sectors[sec1.name] = sec1
        galaxy.sectors[sec2.name] = sec2
        galaxy.sectors[sec3.name] = sec3

        foo = TradeBalance(stat_field='tradeExt', region=galaxy)
        update_dict = {('8cVH', 'idhC2-TNs'): 1312, ('hnjMin', 'idhC2-TNs'): 1397, ('idhC2-TNs', 'hnjMin'): 376}
        foo.update(update_dict)

        foo.multilateral_balance()
        exp_imbal = {'8cVH': 0, 'idhC2-TNs': 1, 'hnjMin': 1}
        self.assertEqual(exp_imbal, foo.single_unit_imbalance())

        self.assertEqual(655, sec1.stats.tradeExt)
        self.assertEqual(1541, sec2.stats.tradeExt)
        self.assertEqual(885, sec3.stats.tradeExt)

    def test_is_balanced_1(self) -> None:
        core = Sector('# Core', '# 0, 0')
        forn = Sector('# Fornast', '# 0, -1')
        delp = Sector('# Delphi', '# +1, -1')
        mass = Sector('# Massilia', '# +1, 0')
        olde = Sector('# Old Expanses', '# +2, -1')
        dias = Sector('# Diaspora', '# +2, 0')

        galaxy = Galaxy(8)
        galaxy.sectors['Core'] = core
        galaxy.sectors['Fornast'] = forn
        galaxy.sectors['Delphi'] = delp
        galaxy.sectors['Massilia'] = mass
        galaxy.sectors['Old Expanses'] = olde
        galaxy.sectors['Diaspora'] = dias

        update_dict = {('Core', 'Fornast'): 1, ('Delphi', 'Massilia'): 1, ('Old Expanses', 'Diaspora'): 1}
        foo = TradeBalance(stat_field='tradeExt', region=galaxy)
        foo.update(update_dict)

        foo.is_balanced()
