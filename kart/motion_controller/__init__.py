"""
This package holds MotionController and related classes for
carrying out motions dictated by DriveLogic
"""


class MotionController(object):
    def __init__(self):
        pass  # TODO

    @property
    def speed(self) -> float:
        """
        Gets the currently set speed in m/s
        :return: float (m/s)
        """
        # TODO

    @speed.setter
    def speed(self, speed: float) -> None:
        """
        Takes a speed in m/s (for sake of keeping with SI units)
        and attempts to
        :param speed: float (m/s)
        :return: None
        """
        # TODO

    @property
    def turn_radius(self) -> float:
        """
        Gets the currently set turn radius in meters.
        :return: float (negative left, positive right, 0 == no turn)
        """
        # TODO

    @turn_radius.setter
    def turn_radius(self, turn_radius: float) -> None:
        """
        Sets the current turn radius in meters.
        negative for left, positive for right, 0 for no turn.
        :param turn_radius: float (m)
        :return: None
        """
        # TODO


class VirtualMotionController(object):
    pass  # TODO
