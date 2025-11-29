"""
Created on Nov 26, 2025

@author: CyberiaResurrection
"""
import contextlib
import logging
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import MagicMock, call, patch
from wikitools3.page import Page
from wikitools3.wiki import Wiki

from PyRoute.WikiUploadPDF import set_logging, uploadSummaryText, uploadSec, build_parser, process
from PyRoute.WikiReview import WikiReview
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

    def test_build_parser_1(self) -> None:
        fullpath = self.unpack_filename('../PyRoute/WikiUploadPDF.py')

        with patch('sys.argv', [fullpath]):
            args = build_parser()
            self.assertEqual('../maps', args.input)
            self.assertTrue(args.maps)
            self.assertTrue(args.secs)
            self.assertTrue(args.summary)
            self.assertTrue(args.subsector)
            self.assertIsNotNone(args.worlds)
            self.assertFalse(args.worlds)
            self.assertEqual('Milieu 1116', args.era)
            self.assertEqual('INFO', args.log_level)
            self.assertEqual('https://wiki.travellerrpg.com/api.php', args.site)
            self.assertEqual('AB-101', args.user)

    def test_build_parser_2(self) -> None:
        fullpath = self.unpack_filename('../PyRoute/WikiUploadPDF.py')

        with patch('sys.argv', [fullpath, '--no-maps', '--no-secs', '--no-summary', '--no-subsector', '--worlds']):
            args = build_parser()
            self.assertEqual('../maps', args.input)
            self.assertIsNotNone(args.maps)
            self.assertFalse(args.maps)
            self.assertIsNotNone(args.secs)
            self.assertFalse(args.secs)
            self.assertIsNotNone(args.summary)
            self.assertFalse(args.summary)
            self.assertIsNotNone(args.subsector)
            self.assertFalse(args.subsector)
            self.assertIsNotNone(args.worlds)
            self.assertTrue(args.worlds)
            self.assertEqual('Milieu 1116', args.era)
            self.assertEqual('INFO', args.log_level)
            self.assertEqual('https://wiki.travellerrpg.com/api.php', args.site)
            self.assertEqual('AB-101', args.user)

    def test_build_parser_3(self) -> None:
        fullpath = self.unpack_filename('../../PyRoute/WikiUploadPDF.py')

        with patch('sys.argv', [fullpath, '-h']), redirect_stdout(StringIO()) as buffer:
            with contextlib.suppress(SystemExit):
                process()
            buf = buffer.getvalue()
            self.assertIn('usage: WikiUploadPDF.py [-h] [--input INPUT] [--no-maps] [--no-secs]\n', buf)
            self.assertIn('                        [--no-summary] [--no-subsector] [--worlds] [--era ERA]\n', buf)
            self.assertIn('                        [--log-level LOG_LEVEL] [--site SITE] [--user USER]\n\n', buf)
            self.assertIn('Trade map generator wiki upload.\n\n', buf)
            self.assertIn('optional arguments:\n', buf)
            self.assertIn('  -h, --help            show this help message and exit\n', buf)
            self.assertIn('  --input INPUT         output directory for maps, statistics\n', buf)
            self.assertIn('  --no-maps             Don\'t upload the sector PDF maps, default is upload\n', buf)
            self.assertIn('                        the maps\n', buf)
            self.assertIn('  --no-secs             Don\'t upload the sector table pages, default is to\n', buf)
            self.assertIn('                        upload the sector table pages\n', buf)
            self.assertIn('  --no-summary          Don\'t upload the sector summary pages, default is to\n', buf)
            self.assertIn('                        upload the sector summary pages\n', buf)
            self.assertIn('  --no-subsector        Don\'t upload the subsector summary pages, default is\n', buf)
            self.assertIn('                        to upload the subsector summary pages\n', buf)
            self.assertIn('  --worlds              Upload the data for individual worlds, default is to\n', buf)
            self.assertIn('                        not upload world data\n', buf)
            self.assertIn('  --era ERA             Set the era for the world upload data, default [Milieu\n', buf)
            self.assertIn('                        1116]\n', buf)
            self.assertIn('  --log-level LOG_LEVEL\n', buf)
            self.assertIn('  --site SITE\n', buf)
            self.assertIn('  --user USER           (Bot) user to connect to the wiki and perform the\n', buf)
            self.assertIn('                        uploads, default [AB-101]\n', buf)

    def test_process_1(self) -> None:
        fullpath = self.unpack_filename('../../PyRoute/WikiUploadPDF.py')

        ecopath = self.unpack_filename('../../Tests/DeltaFiles/wiki upload/Reft Sector.economic.wiki')
        secpath = self.unpack_filename('../../Tests/DeltaFiles/wiki upload/Reft Sector.sector.wiki')

        self.setUpPyfakefs()
        self.fs.add_real_file(fullpath, target_path='/PyRoute/WikiUploadPDF.py')
        self.fs.add_real_file(ecopath, target_path='/data/Reft Sector.economic.wiki')
        self.fs.add_real_file(secpath, target_path='/data/Reft Sector.sector.wiki')
        with open('/data/sectors.wiki', 'w', encoding='utf-8') as f:
            f.writelines(['Foo'])
        with open('/data/subsectors.wiki', 'w', encoding='utf-8') as f:
            f.writelines(['Bar'])
        with open('/data/Reft Sector.pdf', 'w', encoding='utf-8') as f:
            f.writelines(['Baz'])

        args = ['/PyRoute/WikiUploadPDF.py', '--input', '/data/']

        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        exp_logs = ['DEBUG:WikiUpload:Dummy message']

        site = MagicMock(autospec=Wiki)
        review = MagicMock(autospec=WikiReview)

        with self.assertLogs(logger, 'DEBUG') as logs,\
                patch('PyRoute.WikiUploadPDF.WikiReview.get_site', return_value=site) as mock_site,\
                patch('PyRoute.WikiUploadPDF.WikiReview', return_value=review) as mock_review,\
                patch('PyRoute.WikiUploadPDF.uploadSec') as mock_sec, \
                patch('PyRoute.WikiUploadPDF.uploadSummaryText') as mock_summary, \
                patch('sys.argv', args):
            logger.debug('Dummy message')
            process()
            self.assertEqual(exp_logs, logs.output)
            mock_site.assert_not_called()
            mock_review.assert_called_once()
            calls = mock_review.call_args
            self.assertIsNone(calls.args[1])
            self.assertIsNotNone(calls.args[2])
            self.assertFalse(calls.args[2])
            self.assertIsNone(calls.args[3])
            mock_sec.assert_called()
            self.assertEqual(2, len(mock_sec.call_args_list))
            self.assertEqual(call(review, '/data/Reft Sector.economic.wiki', '/economic', 'Milieu 1116'),
                             mock_sec.call_args_list[0])
            self.assertEqual(call(review, '/data/Reft Sector.sector.wiki', '/sector', 'Milieu 1116'),
                             mock_sec.call_args_list[1])
            mock_summary.assert_called()
            self.assertEqual(2, len(mock_summary.call_args_list))
            self.assertEqual(call(review, '/data/sectors.wiki', 'Milieu 1116', 'Sector'),
                             mock_summary.call_args_list[0])
            self.assertEqual(call(review, '/data/subsectors.wiki', 'Milieu 1116', 'Subsector'),
                             mock_summary.call_args_list[1])
            self.assertEqual(call.upload_file('/data/Reft Sector.pdf'), mock_review.return_value.method_calls[0])

    def test_process_2(self) -> None:
        fullpath = self.unpack_filename('../../PyRoute/WikiUploadPDF.py')

        ecopath = self.unpack_filename('../../Tests/DeltaFiles/wiki upload/Reft Sector.economic.wiki')
        secpath = self.unpack_filename('../../Tests/DeltaFiles/wiki upload/Reft Sector.sector.wiki')

        self.setUpPyfakefs()
        self.fs.add_real_file(fullpath, target_path='/PyRoute/WikiUploadPDF.py')
        self.fs.add_real_file(ecopath, target_path='/data/Dagudashaag Sector.economic.wiki')
        self.fs.add_real_file(secpath, target_path='/data/Dagudashaag Sector.sector.wiki')
        self.fs.add_real_file(ecopath, target_path='/data/Core Sector.economic.wiki')
        self.fs.add_real_file(secpath, target_path='/data/Core Sector.sector.wiki')

        args = ['/PyRoute/WikiUploadPDF.py', '--input', '/data/', '--no-maps', '--no-secs', '--no-summary',
                '--no-subsector', '--worlds', '--site', 'http://foo.travellerrpg.com/api.php', '--user', 'CD-202',
                '--log-level', 'DEBUG']

        logger = logging.getLogger('WikiUpload')
        logger.manager.disable = 0
        logger.setLevel('DEBUG')
        exp_logs = ['DEBUG:WikiUpload:Checking Path /data/* Sector.economic.wiki -> '
                    "['/data/Dagudashaag Sector.economic.wiki', '/data/Core Sector.economic.wiki']"]

        with self.assertLogs(logger, 'DEBUG') as logs,\
                patch('PyRoute.WikiUploadPDF.WikiReview') as mock_review,\
                patch('PyRoute.WikiUploadPDF.uploadWorlds') as mock_worlds, \
                patch('sys.argv', args):
            process()
            self.assertEqual(exp_logs, logs.output)
            mock_worlds.assert_called_once()
            mock_review.assert_called_once_with(mock_review.get_site.return_value, None, False, None)
            self.assertEqual(1, mock_worlds.call_count)
            self.assertEqual(
                call(
                    mock_review.return_value,
                    '/data/Dagudashaag Sector.sector.wiki',
                    '/data/Dagudashaag Sector.economic.wiki',
                    'Milieu 1116'
                ),
                mock_worlds.call_args_list[0]
            )
            self.assertEqual(1, mock_review.get_site.call_count)
            calls = mock_review.get_site.call_args_list
            self.assertEqual(call('CD-202', 'http://foo.travellerrpg.com/api.php'), calls[0])
