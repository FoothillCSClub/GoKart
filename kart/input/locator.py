"""
Module holding locator classes which return information about
kart position.
"""

from ..util import Point


class LocatorInput:
    """
    Class handling gathering of information about position of kart.
    """

    @property
    def location(self) -> Point:
        """
        Gets location of kart
        :return: Point
        """


class Locator:
    """
    Class handling a single source of location input
    """


class VirtualLocatorInput:
    """
    Class returning location data for testing
    """