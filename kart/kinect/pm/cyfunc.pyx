import math
import numpy as np
import itertools as itr
import kart.kinect.pm.kinect as kinect


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


cpdef pos_from_depth_map_point(int x, int y, int map_depth):
    cdef float angular_x = float(x - HALF_SENSOR_PX_WIDTH) / SENSOR_PIXEL_WIDTH * \
        SENSOR_ANGULAR_WIDTH
    cdef float angular_y = float(y - HALF_SENSOR_PX_HEIGHT) / SENSOR_PIXEL_HEIGHT *\
            SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
    cdef float depth = math.tan(map_depth / 2842.5 + 1.1863)
    pos = (
        math.sin(angular_x) * depth,
        depth,
        -math.sin(angular_y) * depth,
    )
    return pos


def fill_point_cloud(depth_array, point_array=None):
    """
    Makes a point cloud array from passed depth array.
    If point_array is None, creates a new array.
    If passed a point_array, fills all empty positions.
    :param depth_array: np.ndarray
    :param point_array: np.ndarray
    :return: np.ndarray
    """
    if point_array is None:
        point_array = np.ndarray((CLOUD_WIDTH, CLOUD_HEIGHT, 3))
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
        if point_array[y][x][1] != 0:
            continue
        map_depth = depth_array[y][x]
        arr_x_index = int(x / SAMPLE_DISTANCE)
        arr_y_index = int(y / SAMPLE_DISTANCE)
        if map_depth == 2047:
            # if depth is max value, set marker value and go on
            points[arr_y_index][arr_x_index] = (0, 0, 0)
            continue
        point_array[arr_y_index][arr_x_index] = \
            pos_from_depth_map_point(x, y, map_depth)
    return point_array


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


def get_non_traversable_point_cloud(points_arr):
    # while working from the bottom of the array up, once
    # a column has had a non-traversible point found within it, it will
    # be removed from active columns
    active_col_indices = set(x for x in range(0, CLOUD_WIDTH))

    for y in range(0, CLOUD_HEIGHT, -1):

