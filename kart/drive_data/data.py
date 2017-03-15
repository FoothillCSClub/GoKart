"""
Module holding data objects for kart program.
"""

from time import time  # used to track run time


class DriveData:
    """
    Holds all important data that should be able to be accessed across
    packages.
    """
    def __init__(self):
        self.start_time = time()
        self.col_avoid_pointmap = None  # set by input

    @property
    def run_time(self) -> float:
        """
        Gets time since run began in seconds.

        Getter only. Can not be set.
        :return: float
        """
        return time() - self.start_time
