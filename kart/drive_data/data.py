"""
Module holding data objects for kart program.
"""

from time import time

import kart.drive_data.limits as limits
import kart.drive_data.constants as constants

from .map import Map


class DriveData:
    """
    Holds all important data that should be able to be accessed across
    packages.
    """
    def __init__(self):
        self.map = Map()
        self.start_time = time()
        # todo

    # probably a better way to do this.
    @property
    def limits(self) -> object:
        return limits

    @property
    def constants(self):
        return constants
