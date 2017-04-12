"""
Tests that functions + classes in turn_table module operate correctly.
"""

from unittest import TestCase

import kart.drive_logic.turn_table as tt


class TestCreatedArcs(TestCase):
    """
    Class testing properties of generated arcs.
    """
    median_index = int(tt.N_RADII / 2)

    def test_that_an_odd_number_of_arcs_exist(self):
        """
        Test that there is an odd number of arcs.
        This is necessary because it is assumed in logic classes
        that there are an equal number of left and right arcs
        that have been calculated, plus one non-curved, straight arc.
        :return: None
        """
        self.assertTrue(tt.N_RADII % 2)

    def test_arcs_list_contains_only_arcs(self):
        self.assertTrue(all([isinstance(arc, tt.Arc) for arc in tt.arcs]))

    def test_median_arc_has_no_curvature(self):
        median_arc = tt.arcs[self.median_index]
        assert isinstance(median_arc, tt.Arc)
        self.assertEqual(0, median_arc.radius)

    def test_leftmost_arc_has_lower_radius_than_median(self):
        self.assertLess(tt.arcs[0].radius, tt.arcs[self.median_index].radius)

    def test_rightmost_arc_has_higher_radius_than_median(self):
        self.assertLess(tt.arcs[self.median_index].radius, tt.arcs[-1].radius)

    def test_that_left_arcs_decrease_from_first_onwards(self):
        self.assertLess(
            tt.arcs[self.median_index - 1].radius,
            tt.arcs[0].radius)
        self.assertTrue(all(
            tt.arcs[i].radius > tt.arcs[i + 1].radius for
            i in range(0, self.median_index - 2)
        ))

    def test_that_right_arcs_decrease_from_first_onwards(self):
        self.assertGreater(
            tt.arcs[self.median_index + 1].radius,
            tt.arcs[-1].radius)
        self.assertTrue(all(
            tt.arcs[-i].radius > tt.arcs[-i + 1].radius for
            i in range(1, self.median_index)
        ))
