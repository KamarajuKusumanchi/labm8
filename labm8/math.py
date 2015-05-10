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
import math
import scipy
from scipy import stats

# Return the square root of a number.
def sqrt(number):
    return math.sqrt(number)

# Return the mean value of a list of divisible numbers.
def mean(array):
    if len(array) < 1:
        return 0
    return sum([float(x) for x in array]) / float(len(array))

# Return the range between min and max values.
def range(array):
    if len(array) < 1:
        return 0
    return max(array) - min(array)

# Return the variance of a list of divisible numbers.
def variance(array):
    if len(array) < 2:
        return 0
    u = mean(array)
    return sum([(x - u) ** 2 for x in array]) / (len(array) - 1)

# Return the standard deviation of a list of divisible numbers.
def stdev(array):
    return sqrt(variance(array))

# Return the confidence interval of a list for a given confidence.
def confinterval(array, conf=0.95, normal_threshold=30):
    n = len(array)

    if n < 1:
        # We have no data.
        return (0, 0)
    elif n == 1:
        # We have only a single datapoint, so return that value.
        return (array[0], array[0])

    scale = stdev(array) / sqrt(n)
    # Check if all values are the same.
    values_all_same = all(x == array[0] for x in array[1:])

    if values_all_same:
        # If values are all the same, return that value.
        return (array[0], array[0])
    if n < normal_threshold:
        # We have a "small" number of datapoints, so use a t-distribution.
        return scipy.stats.t.interval(conf, n - 1, loc=mean(array), scale=scale)
    else:
        # We have a "large" number of datapoints, so use a normal distribution.
        return scipy.stats.norm.interval(conf, loc=mean(array), scale=scale)