"""
Main logic class
"""

from ..drive_data.data import DriveData


class Logic(object):
    def __init__(self, data: DriveData):
        self.conditions = {}
        self._data = data

    def tic(self) -> None:
        """
        Runs one logic tic;
            Evaluates each condition once, and runs appropriate methods
        :return: None
        """
        [cond.tic() for cond in self.conditions.values()]

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
        if run time is less than 5
        :return:
        """

    @property
    def 


class StaticWheelTurnLogic(Logic):
    """
    Simple test logic class that does not (assuming everything
    works correctly) move the kart, but simply test that the
    steering system is able to turn the wheels.

    Test Should be completed within 10 seconds.
    """

    @property
    def target_speed(self) -> float:
        return 0.