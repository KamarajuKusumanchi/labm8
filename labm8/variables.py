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

# variables - Serialisable representation of experimental values.
#
# These classes represent experimental variables, and are designed for
# persistent storage through serialising/deserialising to and from
# JSON.
import labm8 as lab
import labm8.crypto
import labm8.time

import inspect
import time

class EncodeError(Exception):
    """
    Error thrown if JSON encoding fails.
    """
    pass

#
class Variable(object):
    def __init__(self, name, val=None):
        """
        Create a new Variable instance.
        """
        self.name = name
        self.val = val

    def encode(self):
        """
        Encode a variable to JSON.
        """
        if not lab.is_str(self.name) or not self.name:
            raise EncodeError("Variable has invalid name: " + str(self))
        elif self.val == None:
            raise EncodeError("Variable has no value: " + str(self))

        return (self.name, self.val)

    def __repr__(self):
        return "{name}: {val}".format(name=self.name, val=self.val)

    def __key(x):
        return (x.name, x.val)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __lt__(x, y):
        if x.name == y.name:
            return x.val < y.val
        else:
            return x.name < y.name

    def __gt__(x, y):
        return not x == y and not x < y

    def __le__(x, y):
        return x < y or x == y

    def __ge__(x, y):
        return x > y or x == y

    def __hash__(x):
        return hash(x.__key())

class Independent(Variable):
    """
    An independent, or control variable.
    """
    def __init__(self, *args, **kwargs):
        super(Independent, self).__init__(*args, **kwargs)

class Dependent(Variable):
    """
    A dependent, or measured variable.
    """
    def __init__(self, *args, **kwargs):
        super(Dependent, self).__init__(*args, **kwargs)

    def pre(self, **kwargs):
        """
        Pre-sample hook.
        """
        pass
    def post(self, **kwargs):
        """
        Post-sample hook.
        """
        pass

class Derived(Dependent):
    """
    A derived variable, i.e. one that is not directly measured, but
    inferred form one or more dependent variables.
    """
    def __init__(self, *args, **kwargs):
        super(Derived, self).__init__(*args, **kwargs)

    def encode(self):
        """
        Encode a derived variable. Note that only the name is encoded, not
        the value itself.
        """
        if not lab.is_str(self.name) or not self.name:
            raise EncodeError("Derived variable has invalid name: " + str(self))

        return self.name

class Result:
    """
    A result consists of a set of independent variables, and one or
    more sets of dependent, or "output", variables.
    """
    def __init__(self, invars=[], samples=[], couts=set(), bad=False):
        """
        Initialise result given the set of invars, outvars, constant outs,
        and bad fag.
        """
        self.invars = invars
        self.samples = samples
        self.couts = couts
        self.bad = bad

    def __repr__(self):
        invar_strings  = [str(x) for x in self.invars]
        cout_strings   = [str(x) for x in self.couts]
        sample_strings = []
        for sample in self.samples:
            sample_strings.append(["    " + str(x) for x in sample])

        return "\n".join(invar_strings + cout_strings + sample_strings)

    def encode(self):
        """
        Encode a result for JSON serialization.
        """
        derived = []
        encoded_samples = []

        if len(self.samples):
            # Build a list of derived variables from the last sample.
            derived = [x for x in self.samples[-1] if isinstance(x, Derived)]
            encoded_samples = []

            for sample in self.samples:
                dependent = [x for x in sample if isinstance(x, Dependent)]
                encoded_samples.append([var.encode() for var in sample])

        return [
            [var.encode() for var in self.invars], # invars
            [var.encode() for var in self.couts],  # couts
            [var.encode() for var in derived],
            encoded_samples,
            self.bad
        ]

    @staticmethod
    def decode(d, invars):
        """
        Decode a serialesd JSON result.
        """
        samples = [[Dependent(x, y[x]) for x in y] for y in d['out']] if 'out' in d else []
        couts = set([Dependent(x, d['cout'][x]) for x in d['cout']]) if 'cout' in d else set()
        bad = d['bad'] if 'bad' in d else False

        # FIXME: Pass module(s) to search.
        import skelcl
        dsamples = [getattr(skelcl, str(x)) for x in d['dout']] if 'dout' in d else []
        benchmark = lookup1(invars, "Benchmark").val

        if len(dsamples):
            for sample in samples:
                kwargs = {
                    'benchmark': benchmark,
                    'exitstatus': lookup1(sample, "Exit status").val,
                    'output': lookup1(sample, "Output").val
                }

                # Instantiate derived variables.
                douts = [var() for var in dsamples]
                # Set variables of derived variables.
                [var.post(**kwargs) for var in douts]
                # Add derived variables to sample.
                sample += douts

        return Result(invars, samples=samples, couts=couts, bad=bad)


#########################
# Independent Variables #
#########################

#
class Hostname(Independent):
    def __init__(self, name):
        Independent.__init__(self, "Hostname", name)

#
class BenchmarkName(Independent):
    def __init__(self, name):
        Independent.__init__(self, "Benchmark", name)

# Runtime argument.
class Argument(Independent):
    pass

# Represents a tunable knob.
class Knob(Independent):
    # Set the value of the knob.
    def set(self): pass


#######################
# Dependent Variables #
#######################

# A built-in runtime variable.
class StartTime(Dependent):
    def __init__(self):
        Dependent.__init__(self, "Start time")

    def pre(self, **kwargs):
        self.val = lab.time.nowstr()

# A built-in runtime variable.
class EndTime(Dependent):
    def __init__(self):
        Dependent.__init__(self, "End time")

    def post(self, **kwargs):
        self.val = lab.time.nowstr()

# A built-in runtime variable.
class RunTime(Dependent):
    def __init__(self, val=None):
        Dependent.__init__(self, "Run time")
        self.val = val

    def pre(self, **kwargs):
        self.start = time.time()

    def post(self, **kwargs):
        end = time.time()
        elapsed = end - self.start
        self.val = elapsed

# A built-in runtime variable.
class Checksum(Dependent):
    def __init__(self):
        Dependent.__init__(self, "Checksum")

    def post(self, **kwargs):
         self.val = checksum(kwargs['benchmark'].bin.path)

# A built-in runtime variable.
class ExitStatus(Dependent):
    def __init__(self):
        Dependent.__init__(self, "Exit status")

    def post(self, **kwargs):
        self.val = kwargs['exitstatus']

# A built-in runtime variable.
class Output(Dependent):
    def __init__(self):
        Dependent.__init__(self, "Output")

    def post(self, **kwargs):
        self.val = kwargs['output']

######################
# Derived Variables. #
######################

class Speedup(Derived):
    def __init__(self, val):
        Derived.__init__(self, "Speedup")
        self.val = val

###########
# Filters #
###########

#
class LookupError(Exception):
    pass

#
def lookup(vars, type):
    if inspect.isclass(type):
        f = filter(lambda x: isinstance(x, type), vars)
    else:
        f = filter(lambda x: x.name == type, vars)
    # Evaluate filter into a list of results:
    return list(f)

#
def lookup1(*args):
    var = list(lookup(*args))
    if len(var) != 1:
        raise LookupError(*args)
    return var[0]

def lookupvals(vars, type):
    # Filter by type.
    vars = lookup(vars, type)
    # Create a set of all values.
    allvals = set()
    [allvals.add(x.val) for x in vars]
    # Return values as a list.
    return list(allvals)

#
class HashableInvars:
    def __init__(self, invars, exclude=["Hostname", "Benchmark"]):
        invars = copy.copy(invars)

        # Filter out excluded variables.
        for key in exclude:
            try:
                var = lookup1(invars, key)
                invars.remove(var)
            except LookupError: # Ignore lookup errors
                pass

        self._invars = sorted(list(invars))
        self._key = lib.crypto.sha1(str(self))

    def key(self):
        return self._key

    def __key(x):
        return tuple(x._invars)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __repr__(x):
        return str(x.__key()).encode('utf-8')
