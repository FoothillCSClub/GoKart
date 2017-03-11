import math
import numpy as np
import itertools as itr
import kart.kinect.pm.kinect as kinect
cimport numpy as np


cdef:
    int SAMPLE_DISTANCE = 8
    int SENSOR_PIXEL_HEIGHT = 480
    int SENSOR_PIXEL_WIDTH = 640
    int HALF_SENSOR_PX_HEIGHT = SENSOR_PIXEL_HEIGHT / 2
    int HALF_SENSOR_PX_WIDTH = SENSOR_PIXEL_WIDTH / 2
    double SENSOR_ANGULAR_WIDTH = math.radians(58.5);
    double SENSOR_ANGULAR_HEIGHT = math.radians(46.6)
    double SENSOR_ANGULAR_ELEVATION = math.radians(0.)
    int CLOUD_HEIGHT = math.ceil(SENSOR_PIXEL_HEIGHT / SAMPLE_DISTANCE)
    int CLOUD_WIDTH = math.ceil(SENSOR_PIXEL_WIDTH / SAMPLE_DISTANCE)
    float MAX_SLOPE = math.radians(20.)
    float SLOPE_COMPARISON_VAL = np.tan(MAX_SLOPE) ** 2
    np.ndarray X_SAMPLE_POSITIONS = \
        np.arange(0, CLOUD_WIDTH, SAMPLE_DISTANCE, np.uint16)
    np.ndarray Y_SAMPLE_POSITIONS = \
        np.arange(0, CLOUD_HEIGHT, SAMPLE_DISTANCE, np.uint16)

cpdef pos_from_depth_map_point(int x, int y, int map_depth):
    cdef double angular_x = float(x - HALF_SENSOR_PX_WIDTH) / SENSOR_PIXEL_WIDTH * \
        SENSOR_ANGULAR_WIDTH
    cdef double angular_y = float(y - HALF_SENSOR_PX_HEIGHT) / SENSOR_PIXEL_HEIGHT *\
            SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
    cdef double depth = np.tan(map_depth / 2842.5 + 1.1863)
    pos = (
        np.sin(angular_x) * depth,
        depth,
        -np.sin(angular_y) * depth,
    )
    return pos


def point_arr_from_depth_arr(dm):
    # make array that point positions will be stored in
    points = np.ndarray((CLOUD_HEIGHT, CLOUD_WIDTH, 3), np.float32)
    # for all combinations of x and y...
    x_range = range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE)
    y_range = range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE)
    cdef:
        int map_depth  # depth of map at each point
        int arr_x_index  # point array x position
        int arr_y_index  # point array y position
    for x, y in itr.product(x_range, y_range):
        # create a point in the newly formed point-cloud.
        map_depth = dm[y][x]
        arr_x_index = int(x / SAMPLE_DISTANCE)
        arr_y_index = int(y / SAMPLE_DISTANCE)
        if map_depth == 2047:
            # if depth is max value, set marker value and go on
            points[arr_y_index][arr_x_index] = (0, 0, 0)
            continue
        points[arr_y_index][arr_x_index] = \
            pos_from_depth_map_point(x, y, map_depth)
    return points


cdef class PointCloud:

    cdef:
        np.ndarray depth_arr, _point_arr
        long time_stamp
        bint filled

    def __init__(self, depth_arr):
        self.depth_arr = depth_arr[0]
        self.time_stamp = depth_arr[1]
        self._point_arr = np.ndarray((CLOUD_HEIGHT, CLOUD_WIDTH, 3))
        self._point_arr.fill(-1)  # marker value for an un-calculated point
        self.filled = False

    @property
    def point_arr(self):
        """
        Gets array of points in point cloud.
        This method requires filling all un-filled points in
        point array.
        If only some points are needed, it is recommended to use
        __getitem__ (ex: point_cloud[x, y]) instead, as this will
        only calculate the points requested.
        :return np.ndarray
        """
        if not self.filled:
            self._point_arr = point_arr_from_depth_arr(self.depth_arr)
            self.filled = True
        return self._point_arr

    cdef void fill_point_arr(self):
        cdef:
            unsigned short map_depth  # depth of map at each point
            int arr_x_index  # point array x position
            int arr_y_index  # point array y position
        # for all combinations of x and y...
        for x, y in itr.product(X_SAMPLE_POSITIONS, Y_SAMPLE_POSITIONS):
            # get positions as they will appear in the point_arr
            arr_x_index = int(x / SAMPLE_DISTANCE)
            arr_y_index = int(y / SAMPLE_DISTANCE)
            # check if point at determined point_arr position holds
            # a marker value. If it does not, it has already been
            # filled. We can then skip ahead to the next position
            if self._point_arr[arr_y_index][arr_x_index][1] != -1:
                continue
            map_depth = self.depth_arr[y][x]
            if map_depth == 2047:
                # if depth is max value, set marker value and go on
                self._point_arr[arr_y_index][arr_x_index] = (0, 0, 0)
                continue
            self._point_arr[arr_y_index][arr_x_index] = \
                pos_from_depth_map_point(x, y, map_depth)


def slope_in_bounds(p1, p2):
    """
    Gets slope from p1 to p2 as a 2d vector based on height (z)
    position as radian
    :param p1: np.array len 3
    :param p2: np.array len 3
    :return: float (radians)
    """
    dif = np.subtract(p1, p2)
    flat_distance_sq = np.power(dif[0], 2), np.power(dif[2], 2)  # avoid sqrt
    v_difference_sq = np.power(dif[1], 2)
    slope_sq = v_difference_sq / flat_distance_sq
    return slope_sq < SLOPE_COMPARISON_VAL
