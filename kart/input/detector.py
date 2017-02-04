"""
Module holding classes for retrieving input from sensors whose
input is to be used to detect obstacles
"""
import typing as ty

from mathutils import Vector

from ..util import Detection


class DetectorInput:
    """
    Abstract class handing combined input from all detectors.
    """

    @property
    def detections(self) -> ty.List[Detection]:
        """
        Gets list of detections from all sensors
        :return: List[Detection]
        """
        # TODO


class Detector:
    """
    Abstract class handing input from a sensor, and when queried,
    returning information about detected objects.
    This class should be sub-classed by classes for each unique
    type of sensor used.
    """

    @property
    def fov(self) -> ty.Tuple[float, float]:
        """
        Gets field of view of sensor.
        :return: tuple[width (radians), height (radians)]
        """
        raise NotImplementedError  # overridden by subclasses

    @property
    def rel_ori(self) -> Vector:
        """
        Gets relative orientation of the sensor
        :return: Vector
        """
        raise NotImplementedError  # overridden by subclasses


class VirtualDetectorInput:
    """
    Virtual detector for testing purposes
    """