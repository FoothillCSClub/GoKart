"""
Main logic class
"""

from ..drive_data.data import DriveData
from .turn_table import arcs as turn_arcs


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

    def tic(self) -> None:
        pass

    @property
    def target_turn_radius(self) -> float:
        pass

    @property
    def target_speed(self) -> float:
        pass


class SimpleTestLogic(Logic):
    """
    Simple logic class which can be used for testing.

    At time of this writing, should simply test that
    wheels are able to turn and kart can be moved
    forward for 5 seconds.

    Test should be completed within 15 seconds.
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
