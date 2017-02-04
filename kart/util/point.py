"""
This module contains Point extended classes storing position
information that will be passed between other packages
"""
# todo: decide what format to store positions as

import typing as ty

from mathutils import Vector


class Point(object):
    """
    Abstract class representing a single stored position.
    """
    # this class might benefit from extending Mathutils.Vector

    def __init__(self, abs_pos: ty.Tuple[float, float]):
        self.abs_pos = Vector(abs_pos)


class Detection(Point):
    """
    Point class holding additional information about the detection;
    when it was detected, size (if known or estimated) .. etc
    """

    def __init__(
            self,
            abs_pos: ty.Tuple[float, float],
            detection_time: float,  # abs time in seconds
            radius: float=None,  # radius of detection obj
    ):
        super().__init__(abs_pos)
        self.detection_time = detection_time
        self.r = radius
