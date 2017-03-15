import math
import numpy as np
import itertools as itr
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
    # generate sampled positions in advance
    np.ndarray X_SAMPLE_POSITIONS = \
        np.arange(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE, np.uint16)
    np.ndarray Y_SAMPLE_POSITIONS = \
        np.arange(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE, np.uint16)
    np.ndarray SAMPLE_POSITIONS = \
        np.array([(x, y) for (x, y) in itr.product(
            X_SAMPLE_POSITIONS,
            Y_SAMPLE_POSITIONS
        )], np.uint16)


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
        np.ndarray depth_arr, _point_arr, _nearest_non_traversable
        long time_stamp
        bint filled

    def __init__(self, depth_arr):
        self.depth_arr = depth_arr[0]
        self.time_stamp = depth_arr[1]
        self._point_arr = np.ndarray((CLOUD_HEIGHT, CLOUD_WIDTH, 3))
        self._point_arr.fill(-1)  # marker value for an un-calculated point
        self._nearest_non_traversable = None
        self.filled = False

    def __getitem__(self, position):
        cdef unsigned short x, y
        x, y = position
        if not (0 <= x < CLOUD_WIDTH and 0 <= y < CLOUD_HEIGHT):
            raise ValueError(
                'PointCloud.getitem: Passed position {} was outside bounds'
                ' of PointCloud array. size: ({}, {})'
                    .format(position, CLOUD_WIDTH, CLOUD_HEIGHT)
            )
        x, y = position
        return self.get_point(x, y)

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
            self.fill_point_arr()
            self.filled = True
        return self._point_arr

    @property
    def nearest_non_traversable_points(self):
        """
        Gets nearest point that is non-traversable in each
        point-cloud column.
        :return: np.ndarray
        """
        if self._nearest_non_traversable is None:
            # if array has not been made, make it now.
            self._nearest_non_traversable = \
                self.find_nearest_non_traversable_points()
        return self._nearest_non_traversable

    @property
    def width(self):
        return CLOUD_WIDTH

    @property
    def height(self):
        return CLOUD_HEIGHT

    # this is implemented here, outside __getitem__ because magic
    # methods must be python-defined, and this slows things down.
    cdef get_point(self, unsigned short x, unsigned short y):
        cdef np.ndarray point
        # get point as stored in point array.
        point = self._point_arr[y][x]
        # if point depth value is -1,
        # its position has not yet been calculated.
        if point[1] != -1:
            return point
        cdef unsigned short depth_map_x, depth_map_y
        depth_map_x, depth_map_y = x * SAMPLE_DISTANCE, y * SAMPLE_DISTANCE
        point = self._point_arr[y][x] = \
            pos_from_depth_map_point(
                depth_map_x,
                depth_map_y,
                self.depth_arr[depth_map_y, depth_map_x]
            )
        return point

    cdef void fill_point_arr(self):
        cdef:
            unsigned short map_depth  # depth of map at each point
            int arr_x_index  # point array x position
            int arr_y_index  # point array y position
            unsigned short x, y  # depth map indices
        # for all combinations of x and y...
        for x, y in SAMPLE_POSITIONS:
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

    cdef np.ndarray find_nearest_non_traversable_points(self):
        # note: this method is largely un-optimized
        active_x_positions = set(x for x in range(0, CLOUD_WIDTH))
        removed_x_positions = set()
        cdef np.ndarray points, p1, p2
        cdef unsigned short x, y
        points = np.zeros((CLOUD_WIDTH, 3), np.float64)

        for y from CLOUD_HEIGHT > y >= 0:
            # iterate from bottom of point cloud upwards
            for x in active_x_positions:
                if self._point_is_traversable(x, y):
                    continue  # if point is traversable, go on to next
                # if point is not traversable...
                points[x] = self.get_point(x, y)  # add this point to array
                # the nearest in this column has now been found,
                # remove this column index from those checked
                removed_x_positions.add(x)
            # remove columns from active x positions that have been
            # marked for removal
            active_x_positions -= removed_x_positions
            removed_x_positions.clear()
        return points

    cdef bint _point_is_traversable(self, unsigned short x, unsigned short y):
        cdef np.ndarray points, p1, p2
        cdef unsigned short x2
        p1 = self[x, y]
        x2 = x -1 if x != 0 else 1
        p2 = self[x2, y]
        if not slope_in_bounds(p1, p2):
            return False
        cdef unsigned short y2
        y2 = y -1 if y != 0 else 1
        p2 = self[x, y2]
        return slope_in_bounds(p1, p2)

# providing this function in both python and c to permit testing
# from a python module. May be a better way to do this?
cpdef bint slope_in_bounds(p1, p2):
    """
    Gets slope from p1 to p2 as a 2d vector based on height (z)
    position as radian
    :param p1: np.array len 3
    :param p2: np.array len 3
    :return: float (radians)
    """
    cdef:
        np.ndarray dif
        double flat_distance_sq, v_difference_sq, slope_sq
    dif = np.subtract(p1, p2)
    flat_distance_sq = np.power(dif[0], 2) + np.power(dif[2], 2)  # avoid sqrt
    v_difference_sq = np.power(dif[1], 2)
    slope_sq = v_difference_sq / flat_distance_sq
    return slope_sq < SLOPE_COMPARISON_VAL


cpdef np.ndarray pos_from_depth_map_point(int x, int y, int map_depth):
    cdef double angular_x = float(x - HALF_SENSOR_PX_WIDTH) / SENSOR_PIXEL_WIDTH * \
        SENSOR_ANGULAR_WIDTH
    cdef double angular_y = float(y - HALF_SENSOR_PX_HEIGHT) / SENSOR_PIXEL_HEIGHT *\
            SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
    cdef double depth = np.tan(map_depth / 2842.5 + 1.1863)
    pos = np.array((
        np.sin(angular_x) * depth,
        depth,
        -np.sin(angular_y) * depth,
    ))
    return pos
