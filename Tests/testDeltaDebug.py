import subprocess
import sys
import unittest
from Tests.baseTest import baseTest


class testDeltaDebug(baseTest):
    def test_delta_debug_command_empty_args(self):
        fullpath = self.unpack_filename('../PyRoute/DeltaDebug/DeltaDebug.py')

        args = [
            sys.executable,
            fullpath
        ]

        foo = subprocess.run(args=args, capture_output=True, text=True)

        self.assertEqual(0, foo.returncode, "DeltaDebug did not complete successfully")
        expected = '0 sectors read\nReducing by sector\nReducing by subsector\nReducing by line\n'
        actual = foo.stderr
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
