import os
import unittest

from Tests.baseTest import baseTest
from pytest_console_scripts import ScriptRunner


class testDeltaDebug(baseTest):

    def test_delta_debug_command_empty_args(self):
        fullpath = self.unpack_filename('../PyRoute/DeltaDebug/DeltaDebug.py')

        cwd = os.getcwd()
        runner = ScriptRunner(launch_mode="inprocess", rootdir=cwd)

        foo = runner.run(command=fullpath)

        self.assertEqual(0, foo.returncode, "DeltaDebug did not complete successfully: " + foo.stderr)
        expected = '0 sectors read\nReducing by sector\nReducing by subsector\nReducing by line\n'
        actual = foo.stderr
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
