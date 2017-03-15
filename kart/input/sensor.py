"""
Simple module handling accessing of information from kinect package,
and updating data with that information
"""
from scipy.spatial.kdtree import KDTree

from ..drive_data.data import DriveData
from ..kinect.pm.kinect import KinGeo


class KinectInput(object):
    def __init__(self, data: 'DriveData'):
        self.data = data
        self.kinect_handler = KinGeo()

    def update(self) -> None:
        """
        Method called each loop of the kinect thread to update data
        :return: None
        """
        # get np array of nearest points for each sampled column of pixels
        nearest_non_traversable_points = \
            self.kinect_handler.point_cloud.nearest_non_traversable_points
        col_avoid_point_map_tree = KDTree(nearest_non_traversable_points)
        self.data.col_avoid_pointmap = col_avoid_point_map_tree
