from unittest import TestCase

import pyximport

pyximport.install()

from ..pm.cyfunc import slope_in_bounds


class TestFuncs(TestCase):
    # if maximum slope is changed, make sure these tests reflect that
    def test_func_slope_less_than_returns_false_when_appropriate1(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 1, 2], [0, 2, 0]))

    def test_func_slope_less_than_returns_false_when_appropriate2(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 1, 2], [2, 0, 4]))

    def test_func_slope_less_than_returns_true_when_appropriate1(self):
        # horizontal_distance == 1.4, vertical distance == 0.1
        self.assertTrue(slope_in_bounds([1, 1, 2], [0, 2, 2.1]))

    def test_func_slope_less_than_returns_true_when_slope_is_flat(self):
        # horizontal_distance == 1, vertical distance == 0
        self.assertTrue(slope_in_bounds([0, 1, 0], [0, 0, 0]))

