"""
Created on Nov 26, 2025

@author: CyberiaResurrection
"""
import logging

from Tests.Pyfakefs.baseTest import baseTest

from PyRoute.WikiUploadPDF import set_logging


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
