"""
Cython functions
"""

import math
import numpy as np
import itertools as itr
import typing as ty

from scipy.spatial.kdtree import KDTree


cdef:
    int SAMPLE_DISTANCE = 8
    int SENSOR_PIXEL_HEIGHT = 480
    int SENSOR_PIXEL_WIDTH = 640
    int HALF_SENSOR_PX_HEIGHT = SENSOR_PIXEL_HEIGHT / 2
    int HALF_SENSOR_PX_WIDTH = SENSOR_PIXEL_WIDTH / 2
    float SENSOR_ANGULAR_WIDTH = math.radians(58.5);
    float SENSOR_ANGULAR_HEIGHT = math.radians(46.6)
    float SENSOR_ANGULAR_ELEVATION = math.radians(0.)
    int CLOUD_WIDTH = math.ceil(SENSOR_PIXEL_WIDTH / SAMPLE_DISTANCE)
    int CLOUD_HEIGHT = math.ceil(SENSOR_PIXEL_HEIGHT / SAMPLE_DISTANCE)

    float MAX_SLOPE = math.radians(20.)
    float SLOPE_COMPARISON_VAL = np.tan(MAX_SLOPE) ** 2


cdef class CyPointCloud:

    def __init__(self, depth_arr):
        self.depth_arr = depth_arr
        self._point_arr = np.ndarray((self.arr_height, self.arr_width, 3))
        self._nearest_cloud = None

    def __getitem__(self, position: ty.Tuple[int, int]):
        """
        Gets position of point at point-cloud position x, y
        :param position: tuple[int x, int y]
        :return: numpy.ndarray[3]
        """
        x, y = position
        point = self._point_arr[y][x]
        if point[1] == 0:  # if distance is 0..
            # a y position of 0 should never occur in any calculated
            # position, because the sensor has a minimum
            # detection distance.
            point = self._point_arr[y][x] = \
                pos_from_depth_map_point(x, y, self.depth_arr[0][y][x])
        return point

    @property
    def point_arr(self):
        """
        Gets complete point array from PointCloud.
        This method will calculate the 3d position of every
        position in the point array.
        If only some points positions in the cloud are needed, it is
        likely faster to access those points specifically using
        __getitem__ (for example: point_cloud[x, y])
        :return: numpy.ndarray
        """
        if not self._point_arr:
            self._point_arr = self.fill_point_cloud()
        return self._point_arr

    @property
    def time_stamp(self) -> int:
        """
        Gets time at which depth map used to generate this PointCloud
        was captured.
        :param self:
        :return:
        """
        return self.depth_arr[1]

    @property
    def arr_width(self):
        """
        Gets width in sampled pixels of point cloud.
        This is the width of the PointCloud's point array.
        :return: int
        """
        return CLOUD_WIDTH

    @property
    def arr_height(self):
        """
        Gets height in sampled pixels of point cloud.
        This is the height of the PointCloud's point array.
        :return: int
        """
        return CLOUD_HEIGHT

    @property
    def nearest_non_traversable_points(self):
        """
        Gets quadmap of points that represent the nearest
        non-traversable point for each column of points in PointCloud
        :return: QuadMap
        """
        if not self._nearest_cloud:
            self._nearest_cloud = self._find_nearest_non_traversable_points()
        return self._nearest_cloud

    def _find_nearest_non_traversable_points(self):
        # while working from the bottom of the array up, once
        # a column has had a non-traversible point found within it, it will
        # be removed from active columns
        active_col_indices = set(x for x in range(0, CLOUD_WIDTH))
        points = np.ndarray((CLOUD_WIDTH, 3), np.float32)

        cdef:
            int x2
            int y2
            bool x_slope_in_bounds
            bool z_slope_in_bounds
        for y in range(0, CLOUD_HEIGHT, -1):  # iterate from bottom up
            for x in active_col_indices:
                # find whether slope along x dimension is in bounds
                p1 = self[x, y]
                x2 = x - 1 if x != 0 else 1
                x_p2 = self[x2, y]
                x_slope_in_bounds = slope_in_bounds(p1, x_p2)
                # find whether slope along z dimension is in bounds
                y2 = y - 1 if y != 0 else 1
                z_p2 = self[x, y2]
                z_slope_in_bounds = slope_in_bounds(p1, z_p2)
                if x_slope_in_bounds and z_slope_in_bounds:
                    continue
                # otherwise, if point is not traversable
                active_col_indices.remove(x)
                points[x] = np.array((p1[0], p1[2]))  # append x, z position
        return points

    cdef fill_point_cloud():
        """
        Fills all empty positions in point cloud
        """
        # for all combinations of x and y...
        x_range = range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE)
        y_range = range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE)
        cdef:
            int map_depth  # depth of map at each point
            int arr_x_index  # point array x position
            int arr_y_index  # point array y position
        for x, y in itr.product(x_range, y_range):
            # create a point in the newly formed point-cloud.
            # if point is already calculated, skip to next position
            if self._point_arr[y][x][1] != 0:
                continue
            map_depth = depth_array[y][x]
            arr_x_index = int(x / SAMPLE_DISTANCE)
            arr_y_index = int(y / SAMPLE_DISTANCE)
            if map_depth == 2047:
                # if depth is max value, set marker value and go on
                self._point_arr[arr_y_index][arr_x_index] = (0, 0, 0)
                continue
            self._point_arr[arr_y_index][arr_x_index] = \
                pos_from_depth_map_point(x, y, map_depth)


cpdef pos_from_depth_map_point(int x, int y, int map_depth):
    cdef float angular_x = float(x - HALF_SENSOR_PX_WIDTH) / SENSOR_PIXEL_WIDTH * \
        SENSOR_ANGULAR_WIDTH
    cdef float angular_y = float(y - HALF_SENSOR_PX_HEIGHT) / SENSOR_PIXEL_HEIGHT *\
            SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
    cdef float depth = math.tan(map_depth / 2842.5 + 1.1863)
    pos = np.array((
        math.sin(angular_x) * depth,
        depth,
        -math.sin(angular_y) * depth,
    ))
    return pos


cpdef bool slope_in_bounds(p1, p2):
    """
    Gets slope from p1 to p2 as a 2d vector based on height (z)
    position as radian
    :param p1: np.array len 3
    :param p2: np.array len 3
    :return: float (radians)
    """
    dif = np.subtract(p1, p2)
    cdef double flat_distance_sq, v_difference_sq, slope_sq
    flat_distance_sq = np.power(dif[0], 2), np.power(dif[2], 2)
    v_difference_sq = np.power(dif[1], 2)
    slope_sq = v_difference_sq / flat_distance_sq
    return slope_sq < SLOPE_COMPARISON_VAL
