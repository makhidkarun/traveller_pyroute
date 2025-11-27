"""
Created on Nov 26, 2025

@author: CyberiaResurrection
"""
import logging
import os
from unittest.mock import MagicMock, call, patch
from wikitools3.page import Page
from wikitools3.wiki import Wiki

from PyRoute import StatCalculation
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.WikiUploadPDF import set_logging, uploadSummaryText, uploadSec, uploadWorlds
from Tests.Pyfakefs.baseTest import baseTest


class testWikiUploadPDF(baseTest):

    def test_set_logging_1(self) -> None:
        logger = logging.getLogger('WikiUpload')
        logger.handlers = []

        set_logging('WARNING')
        self.assertEqual(1, len(logger.handlers))
        handler = logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(logger.level, handler.level)
        formatter = handler.formatter
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(None, formatter.datefmt)
        self.assertEqual('%s,%03d', formatter.default_msec_format)
        self.assertEqual('%Y-%m-%d %H:%M:%S', formatter.default_time_format)
        self.assertEqual('%(asctime)s - %(levelname)s - %(message)s', formatter._fmt)

    def test_upload_summary_text_1(self) -> None:
        logger = logging.getLogger('WikiUpload')
        exp_logs = ['INFO:WikiUpload:uploading summary articles: initial table baz  == foobar']

        self.setUpPyfakefs()
        with open('/summaryfile', 'w', encoding='utf-8') as f:
            f.writelines(['baz statistics == foobar\n'])
            f.writelines(['rhubarb'])

        site = MagicMock()
        page = MagicMock(autospec=Page)
        site.get_page = MagicMock(side_effect=[None, page])

        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadSummaryText(site, '/summaryfile', 'M1105', 'Woop Woop')
            calls = site.method_calls
            self.assertEqual(call.get_page('initial table Woop Woop/summary'), calls[0])
            self.assertEqual(call.get_page('baz  == foobar Woop Woop/summary'), calls[1])
            self.assertEqual(call.save_page(page, 'rhubarb', 'Trade Map update summary'), calls[2])
            self.assertEqual(exp_logs, logs.output)

    def test_upload_summary_text_2(self) -> None:
        logger = logging.getLogger('WikiUpload')
        exp_logs = ['INFO:WikiUpload:uploading summary articles: initial table foobar baz']

        self.setUpPyfakefs()
        with open('/summaryfile', 'wt', encoding='utf-8') as f:
            f.writelines(['foobar baz statistics == \n'])
            f.writelines(['rhubarb\n'])
            f.writelines(['bar'])

        site = MagicMock(autospec=Wiki)
        page = MagicMock(autospec=Page)
        page.getCategories = MagicMock(return_value=['Category:Meta'])
        site.get_page = MagicMock(side_effect=[None, page, page])

        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadSummaryText(site, '/summaryfile', 'M1105', 'Woop Woop')
            calls = site.method_calls
            self.assertEqual(4, len(calls))
            self.assertEqual(call.get_page('initial table Woop Woop/summary'), calls[0])
            self.assertEqual(call.get_page('foobar baz Woop Woop/summary'), calls[1])
            self.assertEqual(call.get_page('foobar baz Woop Woop/summary/M1105'), calls[2])
            self.assertEqual(call.save_page(page, 'rhubarb\nbar', 'Trade Map update summary'), calls[3])
            self.assertEqual(exp_logs, logs.output)
            page.getCategories.assert_called_once_with(True)

    def test_upload_sec_1(self) -> None:
        self.setUpPyfakefs()

        with open('/Core.sec', 'wt', encoding='utf-8') as f:
            f.writelines(['bar'])

        site = MagicMock(autospec=Wiki)
        site.get_page = MagicMock(return_value=None)
        site.save_page = MagicMock()

        uploadSec(site, '/Core.sec', 'Woop Woop', 'M1200')
        site.get_page.assert_called_once_with('CoreWoop Woop')
        site.save_page.assert_not_called()

    def test_upload_sec_2(self) -> None:
        self.setUpPyfakefs()

        with open('/Core.sec', 'wt', encoding='utf-8') as f:
            f.writelines(['bar'])

        site = MagicMock(autospec=Wiki)
        page = MagicMock(autospec=Page)
        page.getCategories = MagicMock(return_value=['Category:Meta'])
        site.get_page = MagicMock(return_value=page)
        site.save_page = MagicMock()

        uploadSec(site, '/Core.sec', 'Woop Woop', 'M1200')
        calls = site.method_calls
        self.assertEqual(3, len(calls))
        self.assertEqual(call.get_page('CoreWoop Woop'), calls[0])
        self.assertEqual(call.get_page('CoreWoop Woop/M1200'), calls[1])
        self.assertEqual(call.save_page(page, 'bar', 'Trade Map update sector data'), calls[2])

        page.getCategories.assert_called_once_with(True)

    def test_upload_worlds_1(self) -> None:
        return
        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        exp_logs = ['ERROR:WikiUpload:Sector file not found: ./foo']
        self.setUpPyfakefs()

        site = MagicMock(autospec=Wiki)
        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadWorlds(site, './foo', './bar', 'M1200')
            self.assertEqual(exp_logs, logs.output)

    def test_upload_worlds_2(self) -> None:
        return
        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        exp_logs = ['ERROR:WikiUpload:Economic file not found: ./bar']
        self.setUpPyfakefs()

        with open('./foo', 'wt', encoding='utf-8') as f:
            f.writelines('blah')

        site = MagicMock(autospec=Wiki)
        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadWorlds(site, './foo', './bar', 'M1200')
            self.assertEqual(exp_logs, logs.output)

    def test_upload_worlds_3(self) -> None:
        return
        sourcefile = [
            self.unpack_filename('DeltaFiles/Dagudashaag-Bolivar.sec'),
        ]

        args = self._make_args()
        args.routes = 'trade'
        args.output = '/output/'
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=True, fix_pop=True,
                                      deep_space=None, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = '/output'

        self.setUpPyfakefs()
        self.fs.add_real_directory('../../PyRoute/templates', read_only=True, target_path='/templates')
        self.assertTrue(os.path.isfile('/templates/summary.wiki'))
        os.mkdir('/maps')
        os.mkdir('/output')
        galaxy.set_borders('range', args.ally_match)
        galaxy.generate_routes()
        galaxy.trade.calculate_routes()
        galaxy.set_borders(args.borders, args.ally_match)

        stats = StatCalculation(galaxy)
        stats.calculate_statistics(args.ally_match)
        with patch('os.path.dirname', return_value=''):
            stats.write_statistics(args.ally_count, args.ally_match, args.json_data)

        secfile = '/output/Dagudashaag Sector.sector.wiki'
        ecofile = '/output/Dagudashaag Sector.economic.wiki'
        self.assertTrue(os.path.isfile(secfile))
        self.assertTrue(os.path.isfile(ecofile))

        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        exp_logs = [
            'INFO:WikiUpload:Uploading Dagudashaag',
            'ERROR:WikiUpload:| 0137\n'
            ' is not equal to !Trade Goods!!Subsector <section end="header"/><section '
            'begin="Mimu" /><section end="Mimu" /><section begin="Old Suns" /><section '
            'end="Old Suns" /><section begin="Arnakhish" /><section end="Arnakhish" '
            '/><section begin="Iiradu" /><section end="Iiradu" /><section '
            'begin="Shallows" /><section end="Shallows" /><section begin="Ushra" '
            '/><section end="Ushra" /><section begin="Khandi" /><section end="Khandi" '
            '/><section begin="Kuriishe" /><section end="Kuriishe" /><section '
            'begin="Zeda" /><section end="Zeda" /><section begin="Remnants" /><section '
            'end="Remnants" /><section begin="Pact" /><section end="Pact" /><section '
            'begin="Gadde" /><section end="Gadde" /><section begin="Bolivar" />\n',
        ]

        site = MagicMock(autospec=Wiki)
        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadWorlds(site, secfile, ecofile, 'M1200')
            self.assertEqual(exp_logs, logs.output)

    def test_upload_worlds_4(self) -> None:
        return
        self.setUpPyfakefs()
        self.fs.add_real_directory('../DeltaFiles/wiki upload', read_only=True, target_path='/')

        secfile = '/Reft Sector.sector.wiki'
        ecofile = '/Reft Sector.economic.wiki'
        self.assertTrue(os.path.isfile(secfile))
        self.assertTrue(os.path.isfile(ecofile))

        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        exp_logs = []

        site = MagicMock(autospec=Wiki)
        with self.assertLogs(logger, 'DEBUG') as logs:
            uploadWorlds(site, secfile, ecofile, 'M1105')
            self.assertEqual(exp_logs, logs.output)
