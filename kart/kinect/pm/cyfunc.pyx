import math
import numpy as np
import itertools as itr
import cmath
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


def point_arr_from_depth_arr(dm):
    cdef int cloud_height = math.ceil(SENSOR_PIXEL_HEIGHT / SAMPLE_DISTANCE)
    cdef int cloud_width = math.ceil(SENSOR_PIXEL_WIDTH / SAMPLE_DISTANCE)
    # make array that point positions will be stored in
    points = np.ndarray((cloud_height, cloud_width, 3), np.float32)
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
