"""
Module holding data objects for kart program.
"""
from collections import deque
from mathutils import Vector
from time import time  # used to track run time


class DriveData:
    """
    Holds all important data that should be able to be accessed across
    packages.
    """
    def __init__(self):
        self.start_time = time()
        self.col_avoid_pointmap = None  # set by input
        self.path = deque()

    @property
    def next_waypoint(self) -> Vector or None:
        if len(self.path) == 0:
            return None
        else:
            return self.path[0]

    @property
    def run_time(self) -> float:
        """
        Gets time since run began in seconds.

        Getter only. Can not be set.
        :return: float
        """
        return time() - self.start_time
