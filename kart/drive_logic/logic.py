"""
Main logic class
"""
import math

from scipy.spatial.kdtree import KDTree
from mathutils import Vector
from numpy import sqrt

from ..drive_data.data import DriveData
from .turn_table import arcs as turn_arcs, Arc
from .const import SAFE_DISTANCE, PREDICTION_DIST
from ..const.limits import SPEED
from ..const.phys_const import DECELERATION_RATE


class Logic(object):
    def __init__(self, data: DriveData):
        self._data = data

    def tic(self) -> None:
        """
        Runs one logic tic;
            Evaluates each condition once, and runs appropriate methods
        :return: None
        """
        raise NotImplementedError

    @property
    def target_speed(self) -> float:
        """
        Gets speed which kart should attempt to match.

        Can not be set.
        :return: float (m/s)
        """
        # at the moment, use of this class is not supported.
        # Use SimpleTestLogic, StaticWheelTurnLogic, or else
        raise NotImplementedError

    @property
    def target_turn_radius(self) -> float:
        """
        Gets turn radius in meters which
        :return:
        """
        raise NotImplementedError


class SimpleColAvoidLogic(Logic):
    """
    Logic class that will attempt to use sensor input
    to avoid obstacles. Does not pay attention to waypoints
    """

    def __init__(self, data: 'DriveData') -> None:
        super().__init__(data)
        self.last_radius_index = int(len(turn_arcs) / 2)
        self._current_turn_radius = 0
        self._current_speed = 0

    def tic(self) -> None:
        # find arc that allows kart to travel farthest
        best_arc = None
        best_distance = 0
        for arc in turn_arcs:
            end = self.get_end_of_arc(arc)
            if end is not None and end.y > best_distance:
                best_arc = arc
                best_distance = end.y
        if best_arc is None:
            self._current_turn_radius = 0
            self._current_speed = 0
            return
        # find speed based on distance to end of prediction
        free_space = best_distance - SAFE_DISTANCE
        self._current_speed = self.find_speed_from_distance(free_space)

    def find_speed_from_distance(self, distance: float) -> float:
        """
        Gets best speed given free distance before end of path
        :param distance: float
        :return: float
        """
        time = sqrt(distance * 2 / DECELERATION_RATE)
        speed = time * DECELERATION_RATE
        return speed

    def get_end_of_arc(self, arc: 'Arc') -> Vector:
        """
        Gets the last viable relative position from a passed Arc
        :param arc: Arc
        :return: Vector
        """
        col_avoid_cloud = self._data.col_avoid_pointmap
        assert isinstance(col_avoid_cloud, KDTree)
        last_safe_point = None
        for pos in arc.positions:
            impinging_points = col_avoid_cloud.query_ball_point(
                pos, SAFE_DISTANCE
            )
            if len(impinging_points) == 0:
                last_safe_point = pos
            else:
                break
        return last_safe_point

    @property
    def target_turn_radius(self) -> float:
        return self._current_turn_radius

    @property
    def target_speed(self) -> float:
        return self._current_speed


class SimpleTestLogic(Logic):
    """
    Simple logic class which can be used for testing.

    At time of this writing, should simply test that
    wheels are able to turn and kart can be moved
    forward for 5 seconds.

    Test should be completed within 15 seconds.
    """

    def tic(self) -> None:
        """
        Does nothing in this test
        :return: None
        """

    @property
    def target_speed(self) -> float:
        """
        If run time is less than 5, turns wheels left
        If run time is from 5-10, turns wheels right
        from 15-20 seconds run time, moves forward at low rate of speed
        :return: float
        """
        if 15 < self._data.run_time < 20:
            return 0.1
        else:
            return 0

    @property
    def target_turn_radius(self) -> float:
        """
        If run time is between 10 and 15, move forward -slowly-
        :return: float
        """
        if 0 < self._data.run_time < 5:
            return -5
        if 5 < self._data.run_time < 10:
            return 5
        else:
            return 0


class StaticWheelTurnLogic(Logic):
    """
    Simple test logic class that does not (assuming everything
    works correctly) move the kart, but simply test that the
    steering system is able to turn the wheels.

    Test Should be completed within 10 seconds, not including
    time taken to reset wheels to center position
    """

    @property
    def target_speed(self) -> float:
        return 0

    @property
    def target_turn_radius(self) -> float:
        """
        If run time is between 10 and 15, move forward -slowly-
        :return: float
        """
        if 0 < self._data.run_time < 5:
            return -5
        if 5 < self._data.run_time < 10:
            return 5
        else:
            return 0


def expanding_indices(start_index: int, lower_bound: int, upper_bound: int):
    """
    Yields indices expanding progressively away from passed starting
    index, continuing until bounds are reached.
    :return:
    """
    i = 0
    while True:
        if lower_bound <= i < upper_bound:
            yield i + start_index
        elif abs(i) > max(abs(lower_bound), abs(upper_bound)):
            break
        if i >= 0:
            i = i * -1 - 1
        else:
            i = i * -1 + 1
