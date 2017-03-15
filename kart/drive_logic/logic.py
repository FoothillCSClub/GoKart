"""
Main logic class
"""
import math

from scipy.spatial.kdtree import KDTree
from mathutils import Vector

from ..drive_data.data import DriveData
from .turn_table import arcs as turn_arcs, Arc
from .const import SAFE_DISTANCE


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


class MainLogic(Logic):
    """
    Logic class that will attempt to use sensor and locator input
    to avoid obstacles and reach passed way-points (if implemented)
    """

    def __init__(self, data: 'DriveData') -> None:
        super().__init__(data)
        self.last_radius_index = int(len(turn_arcs) / 2)
        self._current_turn_radius = 0
        self._current_speed = 0

    def tic(self) -> None:
        best_radius = self._find_turn_radius()
        if best_radius is None:
            # if no path could be found..
            self._current_speed = 0
            self._current_turn_radius = 0
        else:
            self._current_turn_radius = best_radius

    def _find_turn_radius(self) -> float or None:
        """
        Find best turn radius.
        :return:
        """
        if isinstance(self._data.next_waypoint, Vector):
            assert False  # todo: score based on how close relative
            # position is to next waypoint
        else:
            def scoring_func(end_pos: Vector): return end_pos.magnitude
        best_arc = None
        top_score = 0
        for arc in turn_arcs:
            end = self.get_end_of_arc(arc)
            if end is None:
                continue
            score = scoring_func(end)
            if score > top_score:
                best_arc = arc
        if best_arc:
            return best_arc.radius
        else:
            return None

    def _find_speed(self) -> float:
        """
        Finds best speed depending on available data
        :return: float
        """

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
            yield i
        elif abs(i) > max(abs(lower_bound), abs(upper_bound)):
            break
        if i >= 0:
            i = i * -1 - 1
        else:
            i = i * -1 + 1
