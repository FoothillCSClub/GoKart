from unittest import TestCase

import pyximport

pyximport.install()

from ..pm.cyfunc import slope_in_bounds


class TestFuncs(TestCase):
    # if maximum slope is changed, make sure these tests reflect that
    def test_func_slope_less_than_returns_false_when_appropriate1(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 2, 1], [0, 0, 2]))

    def test_func_slope_less_than_returns_false_when_appropriate2(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 2, 1], [2, 4, 0]))

    def test_func_slope_less_than_returns_true_when_appropriate1(self):
        # horizontal_distance == 1.4, vertical distance == 0.1
        self.assertTrue(slope_in_bounds([1, 2, 1], [0, 2.1, 2]))
