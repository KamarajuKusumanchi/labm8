# Copyright (C) 2015 Chris Cummins.
#
# Labm8 is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Labm8 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with labm8.  If not, see <http://www.gnu.org/licenses/>.
from unittest import main
from tests import TestCase

import labm8 as lab
from labm8 import system

import os
import socket

class TestSystem(TestCase):

    def test_name(self):
        hostname = socket.gethostname()
        self._test(hostname, system.HOSTNAME)
        self._test(hostname, system.HOSTNAME)

    def test_pid(self):
        pid = os.getpid()
        self._test(pid, system.PID)
        self._test(pid, system.PID)

    def test_run(self):
        self._test(0, system.run(["true"]))
        self._test(1, system.run(["false"], exit_on_error=False))

    def test_check_output(self):
        self._test("", system.check_output(["true"]))
        self.assertRaises(system.SubprocessError,
                          system.check_output, ["false"], exit_on_error=False)
        self._test("hello\n", system.check_output(["echo", "hello"]))

if __name__ == '__main__':
    main()