from unittest import TestCase

from pm.kinect import slope_in_bounds, blurred_depth


class TestFuncs(TestCase):
    # if maximum slope is changed, make sure these tests reflect that
    def test_func_slope_less_than_returns_false_when_appropriate1(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 2, 1], [0, 0, 2]))

    def test_func_slope_less_than_returns_false_when_appropriate2(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 2, 1], [2, 4, 0]))

    def test_func_slope_less_than_returns_true_when_appropriate1(self):
        # horizontal_distance == 1.4
        self.assertFalse(slope_in_bounds([1, 2, 1], [0, 2.1, 2]))

    def test_func_blurred_depth_returns_mean(self):
        depth_map = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12)
        )

        self.assertEqual(6, blurred_depth(depth_map, x=1, y=1))

    def test_func_blurred_depth_returns_mean_at_corner(self):
        depth_map = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12)
        )

        self.assertEqual(3.5, blurred_depth(depth_map, x=0, y=0))

    def test_func_blurred_depth_returns_mean_at_side(self):
        depth_map = (
            (1, 2, 3, 4),
            (5, 6, 7, 8),
            (9, 10, 11, 12)
        )

        self.assertEqual(5.5, blurred_depth(depth_map, x=0, y=1))