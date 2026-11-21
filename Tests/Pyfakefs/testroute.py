"""
Created on Nov 21, 2026

@author: CyberiaResurrection
"""
import logging
import os
from unittest.mock import patch

from PyRoute.route import process
from Tests.Pyfakefs.baseTest import baseTest


class testroute(baseTest):

    def test_no_sectors_loaded(self):
        fullpath = self.unpack_filename('../../PyRoute/route.py')

        self.setUpPyfakefs()
        self.fs.add_real_file(fullpath, target_path='/PyRoute/route.py')
        self.fs.makedir('/data/')

        logger = logging.getLogger('PyRoute')
        logger.manager.disable = 0

        args = ['/PyRoute/route.py', '--input', '/data/', '--no-maps',
                '--no-subsector', '--log-level', 'DEBUG']

        with patch('sys.argv', args):
            with self.assertLogs(logger, 'INFO') as logs:
                process()
            found = False
            logs = logs.output
            for line in logs:
                if 'No sector files read in' in line:
                    found = True
                    break
            self.assertTrue(found, 'Should have logged \'No sector files read in\'')
