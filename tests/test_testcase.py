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
from labm8 import testcase


class TestTestcase(TestCase):

    # sqrt() tests
    def test_testcase(self):
        testcases = []
        self._test(testcases, testcase.Harness(testcases).testcases)
        testcases = ["a", "b", 1]
        self._test(testcases, testcase.Harness(testcases).testcases)

    def test_permutations(self):
        invars = {"bar": 1}
        self._test({"bar": 1}, testcase.permutations(invars))
        invars = {"bar": 1, "foo": [2]}
        self._test({"bar": 1, "foo": 2}, testcase.permutations(invars))
        invars = {"bar": [1, 2]}
        self._test([{"bar": 1}, {"bar": 2}], testcase.permutations(invars))


if __name__ == '__main__':
    main()
