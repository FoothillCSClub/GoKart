import kart.drive_data.limits as limits
import kart.drive_data.constants as constants

from .map import Map


class DriveData(object):
    """
    Holds all important data that should be able to be accessed across
    packages.
    """
    def __init__(self):
        self.map = Map()
        # todo

    # probably a better way to do this.
    @property
    def limits(self) -> object:
        return limits

    @property
    def constants(self):
        return constants
