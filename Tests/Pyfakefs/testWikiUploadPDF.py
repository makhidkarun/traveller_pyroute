"""
Created on Nov 26, 2025

@author: CyberiaResurrection
"""
import logging
from unittest.mock import MagicMock, call
from wikitools3.page import Page
from wikitools3.wiki import Wiki

from PyRoute.WikiUploadPDF import set_logging, uploadSummaryText, uploadSec
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
