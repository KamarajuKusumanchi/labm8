# Copyright (C) 2015 Chris Cummins.
#
# This file is part of labm8.
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
import itertools
import sys

import labm8 as lab


class Error(Exception):
    pass


class Harness(object):
    """
    Experimental test harness.
    """

    def __init__(self, testcases=[]):
        """
        Construct a harness with invars.
        """
        self.testcases = testcases

    def setup(self):
        """
        Pre-sampling setup hook.

        Ran before zero or more test case samples.
        """
        pass

    def teardown(self):
        """
        Post-sampling teardown hook.

        Ran after zero or more test case samples.
        """
        pass


class TestCase(object):
    """
    Experimental test case.
    """

    def __init__(self, invars=[]):
        """
        Create testcase with set invars.
        """
        self.invars = invars

    def setup(self):
        """
        Pre-sample setup hook.
        """
        pass

    def sample(self):
        """
        Sample hook. Set outvars.
        """
        pass

    def teardown(self):
        """
        Post-sample teardown hook.
        """
        pass


def permutations(description):
    """

    """
    keys, values = description.keys(), description.values()

    for key in keys:
        if not lab.is_seq(description[key]):
            description[key] = [description[key]]

    vals = itertools.product(*[value for value in values])

    return description


# def enumerate_testcases(description, type=TestCase):
#     """
#     Instantiate testcases.
#     """

#     def permutations(*args):
#         return list(itertools.product(*args))

#     invars = []
#     for key in description.keys():
#         pass

#     return invars
