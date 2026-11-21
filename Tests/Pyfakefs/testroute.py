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

    def test_sector_file_with_no_data(self):
        fullpath = self.unpack_filename('../../PyRoute/route.py')

        self.setUpPyfakefs()
        self.fs.add_real_file(fullpath, target_path='/PyRoute/route.py')
        self.fs.makedir('/data/')
        self.fs.create_file('sectors.txt', encoding='utf-8', contents='Reft Sector\n')
        self.fs.create_file('/data/Reft Sector.sec', encoding='utf-8', contents='\n\n\n# Reft\n# -3,0\n')

        logger = logging.getLogger('PyRoute')
        logger.manager.disable = 0
        galaxy_logger = logging.getLogger('PyRoute.Galaxy')
        galaxy_logger.manager.disable = 0

        args = ['/PyRoute/route.py', '--input', '/data/', '--no-maps',
                '--no-subsector', '--log-level', 'DEBUG', '--sectors', 'sectors.txt']

        with patch('sys.argv', args):
            with self.assertLogs(logger, 'INFO') as logs, self.assertLogs(galaxy_logger, 'INFO') as galaxy_logs:
                process()
            found = False
            logs = logs.output
            galaxy_logs = galaxy_logs.output
            for line in logs:
                if '1 sectors read' in line:
                    found = True
                    break
            self.assertTrue(found, 'Should have logged \`1 sectors read\'')
            found = False
            for line in galaxy_logs:
                if 'Total number of worlds: 0' in line:
                    found = True
                    break
            self.assertTrue(found, 'Should have logged \'Total number of worlds: 0\'')
