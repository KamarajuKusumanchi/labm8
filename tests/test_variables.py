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
from labm8 import variables

class TestVariables(TestCase):

    def _test_variable_constructor(self, var_type):
        self._test("foo", var_type("foo").name)
        self._test(None, var_type("foo").val)
        self._test(1, var_type("foo", 1).val)

    def _test_variable_str(self, var_type):
        self._test("foo: None", str(var_type("foo")))
        self._test("foo: 1", str(var_type("foo", 1)))

    def _test_variable_eq(self, var_type):
        var1 = var_type("foo", 1)
        var2 = var_type("foo", 1)
        self._test(True, var1 == var2)

    def _test_variable_neq(self, var_type):
        var1 = var_type("foo", 1)
        var2 = var_type("foo", 2)
        self._test(False, var1 == var2)

    def _test_variable_gt(self, var_type):
        var1 = var_type("foo", 10)
        var2 = var_type("foo", 2)
        self._test(True, var1 > var2)

        var1.val = 2
        self._test(True, var1 >= var2)

        self._test(False, var1 < var2)
        self._test(False, var1 > var1)

        var1.name = "a"
        self._test(False, var1 > var2)

    def _test_variable_hash(self, var_type):
        var1 = var_type("foo", 10)
        var2 = var_type("foo", 2)
        self._test(False, hash(var1) == hash(var2))

        var2.val = 10
        self._test(True, hash(var1) == hash(var2))

    def _test_variable_encode(self, var_type):
        self._test(("foo", 1), var_type("foo", 1).encode())
        self.assertRaises(variables.EncodeError, var_type("foo", None).encode)
        self.assertRaises(variables.EncodeError, var_type(None, 1).encode)
        self.assertRaises(variables.EncodeError, var_type("", 1).encode)

    # Variable()
    def test_variable_constructor(self):
        self._test_variable_constructor(variables.Variable)

    def test_variable_str(self):
        self._test_variable_str(variables.Variable)

    def test_variable_eq(self):
        self._test_variable_eq(variables.Variable)

    def test_variable_neq(self):
        self._test_variable_neq(variables.Variable)

    def test_variable_gt(self):
        self._test_variable_gt(variables.Variable)

    def test_variable_hash(self):
        self._test_variable_hash(variables.Variable)

    def test_variable_encode(self):
        self._test_variable_encode(variables.Variable)

    # Independent()
    def test_independent_constructor(self):
        self._test_variable_constructor(variables.Independent)

    def test_independent_str(self):
        self._test_variable_str(variables.Independent)

    def test_independent_eq(self):
        self._test_variable_eq(variables.Independent)

    def test_independent_neq(self):
        self._test_variable_neq(variables.Independent)

    def test_independent_gt(self):
        self._test_variable_gt(variables.Independent)

    def test_independent_hash(self):
        self._test_variable_hash(variables.Independent)

    def test_independent_encode(self):
        self._test_variable_encode(variables.Independent)

    # Dependent()
    def test_dependent_constructor(self):
        self._test_variable_constructor(variables.Dependent)

    def test_dependent_str(self):
        self._test_variable_str(variables.Dependent)

    def test_dependent_eq(self):
        self._test_variable_eq(variables.Dependent)

    def test_dependent_neq(self):
        self._test_variable_neq(variables.Dependent)

    def test_dependent_gt(self):
        self._test_variable_gt(variables.Dependent)

    def test_dependent_hash(self):
        self._test_variable_hash(variables.Dependent)

    def test_dependent_encode(self):
        self._test_variable_encode(variables.Dependent)
        self.assertRaises(variables.EncodeError, variables.Derived(None, 1).encode)
        self.assertRaises(variables.EncodeError, variables.Derived("", 1).encode)

    # Derived()
    def test_derived_constructor(self):
        self._test_variable_constructor(variables.Derived)

    def test_derived_str(self):
        self._test_variable_str(variables.Derived)

    def test_derived_eq(self):
        self._test_variable_eq(variables.Derived)

    def test_derived_neq(self):
        self._test_variable_neq(variables.Derived)

    def test_derived_gt(self):
        self._test_variable_gt(variables.Derived)

    def test_derived_hash(self):
        self._test_variable_hash(variables.Derived)

    def test_derived_encode(self):
        self._test("foo", variables.Derived("foo", 1).encode())

    # Result()
    def test_result_constructor_defaults(self):
        self._test([], variables.Result().invars)
        self._test([], variables.Result().samples)
        self._test(set(), variables.Result().couts)
        self._test(False, variables.Result().bad)

    def test_result_constructor_keywords(self):
        self._test([1], variables.Result(invars=[1]).invars)
        self._test([1], variables.Result(samples=[1]).samples)
        self._test(set([1]), variables.Result(couts=set([1])).couts)
        self._test(True, variables.Result(bad=True).bad)

    def test_result_str(self):
        result = variables.Result([1, 2, 3])
        self._test("1\n2\n3", str(result))

    def test_result_encode(self):
        pass # TODO:

if __name__ == '__main__':
    main()
