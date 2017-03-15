"""
This module generates information about different turn radii
at start-up, minimizing calculations that will need to be done
during run-time
"""
import numpy as np

from ..const import limits
from . import const as logic_const


N_RADII = 21  # must be odd, for equal number of arcs per side + straight
N_PREDICTED_POSITIONS_PER_RADII = \
    logic_const.PREDICTION_DIST * logic_const.PREDICTED_POS_PER_METER

arcs = []


class Arc:
    """
    Class representing the path the vehicle could take, describing
    a segment of a circle with passed radius.
    Alternatively, if passed radius is 0, returns positions along
    a straight line.
    """
    # all these methods herein should only be called at startup,
    # and so performance is a non-priority
    def __init__(self, radius: float):
        self.radius = radius
        self.positions = self.find_positions()

    def find_positions(self) -> np.ndarray:
        positions = np.ndarray(
            (N_PREDICTED_POSITIONS_PER_RADII, 2),
            np.float64
        )
        for i in range(N_PREDICTED_POSITIONS_PER_RADII):
            positions[i] = self.find_pos_after_distance(
                (i + 1) * logic_const.PREDICTION_POS_SEP)
        return positions

    def find_pos_after_distance(self, distance: float):
        """
        Gets predicted position of kart after traveling passed distance
        with Arc's turn radius
        :param distance: float
        :return: x, y positions
        """
        if self.radius == 0:
            # if position is on a straight line..
            return 0, distance
        else:
            # if we're not finding a position on a straight line..
            # get fraction of a full circle being described
            circle_circumference = self.radius * np.pi
            fraction_described = distance / circle_circumference
            radians_travelled = fraction_described * np.pi
            z = abs(np.sin(radians_travelled)) * self.radius
            x = (1 - np.cos(radians_travelled)) * self.radius
            return x, z


def populate_arcs():
    center_index = int(N_RADII / 2)
    radii = [
        (1 / limits.MIN_LEFT_TURN_RADIUS) / i if i < center_index else
        (1 / limits.MIN_RIGHT_TURN_RADIUS) / i if i > center_index else
        0
        for i in range(N_RADII)
    ]
    for radius in radii:
        arcs.append(Arc(radius))

populate_arcs()
