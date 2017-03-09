import freenect as fn
import time as t
import math
import itertools as itr
import numpy as np

SAMPLE_DISTANCE = 10

SENSOR_MAX_DEPTH = 4.
SENSOR_PIXEL_HEIGHT = 480
SENSOR_PIXEL_WIDTH = 640
HALF_SENSOR_PX_HEIGHT = SENSOR_PIXEL_HEIGHT / 2
HALF_SENSOR_PX_WIDTH = SENSOR_PIXEL_WIDTH / 2
SENSOR_ANGULAR_WIDTH = math.radians(58.5);
SENSOR_ANGULAR_HEIGHT = math.radians(46.6)
SENSOR_ANGULAR_ELEVATION = math.radians(0.)
POINT_CLOUD_UNITS_TO_METERS = 8.09
BLUR_RADIUS = 2

MAX_SLOPE = math.radians(20.)
SLOPE_COMPARISON_VAL = np.tan(MAX_SLOPE) ** 2


class KinGeo:
    """
    Class handling usage of Kinect input and data processing
    to produce point cloud and geometry

    Supports a single Kinect in use
    """
    ctx = False
    default_max_frq = 30  # max frq at which frames will be retrieved

    def __init__(self):
        """
        Initializes Kinect handler
        """

        if not KinGeo.ctx:
            KinGeo.ctx = fn.init()

        self.ctx = fn.init()
        # self.device = fn.open_device(KinGeo.ctx, 1)
        # assert self.device is not None
        self.last_access = 0.  # time of last kinect depth map access
        self._frame_time = 1./KinGeo.default_max_frq  # min time in s per frame
        self._depth_map = None  # holds numpy array of
        self._pc_timestamp = 0.
        self._points_arr_timestamp = 0.

    @property
    def t_since_last_frame(self):
        """
        Returns time since last depth frame was accessed from Kinect
        :return: float
        """
        return t.time() - self.last_access

    @property
    def access_hz(self):
        """
        Gets access Hz of kinect. Will not ask the Kinect for depth
        data more often than this.
        :return: float
        """
        return 1. / self._frame_time

    @access_hz.setter
    def access_hz(self, hz):
        """
        Sets maximum rate at which KinGeo will ask Kinect for depth info
        :return: None
        """
        self._frame_time = 1. / float(hz)

    @property
    def depth_map(self):
        """
        Gets DepthMap for current sensor frame
        :return: DepthMap
        """
        # If elapsed time since last frame is greater than frame
        # rate, update depth map.
        if self.t_since_last_frame > self._frame_time:
            # get depth map from first Kinect found
            self._depth_map = fn.sync_get_depth()
            if not self._depth_map:
                raise OSError('Could not connect to Kinect')
            self.last_access = t.time()
        # Return the depth-map portion of the depth map array.
        # The second part of the array is the timestamp.
        return DepthMap(self._depth_map)

    @property
    def point_cloud(self):
        """
        Gets point cloud of positions from depth map.
        Returns point cloud as three dimensional array of
        [column][row][point position]
        :return: np.Array
        """
        # build point cloud from current depth map
        return self.depth_map.point_cloud

    @property
    def points_arr(self):
        return self.point_cloud.point_arr


class DepthMap:
    def __init__(self, arr):
        self.arr = arr
        self._point_cloud = None

    @property
    def time_stamp(self):
        return self.arr[1]

    @property
    def point_cloud(self) -> 'Point':
        if not self._point_cloud:
            self._point_cloud = PointCloud(self.arr)
        return self._point_cloud


class PointCloud:
    def __init__(self, depth_arr):
        self.depth_arr = depth_arr
        self._point_arr = None

    @property
    def point_arr(self):
        if not self._point_arr:
            self._point_arr = point_arr_from_depth_arr(self.depth_arr[0])
        return self._point_arr

    @property
    def time_stamp(self) -> int:
        return self.depth_arr[1]


def point_arr_from_depth_arr(dm):
    cloud_height = math.ceil(SENSOR_PIXEL_HEIGHT / SAMPLE_DISTANCE)
    cloud_width = math.ceil(SENSOR_PIXEL_WIDTH / SAMPLE_DISTANCE)
    # make array that point positions will be stored in
    points = np.ndarray((cloud_height, cloud_width, 3), np.float32)
    # for all combinations of x and y...
    x_range = range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE)
    y_range = range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE)
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


def pos_from_depth_map_point(x, y, map_depth):
    angular_x = (x - HALF_SENSOR_PX_WIDTH) / SENSOR_PIXEL_WIDTH * \
        SENSOR_ANGULAR_WIDTH
    angular_y = (y - HALF_SENSOR_PX_HEIGHT) / SENSOR_PIXEL_HEIGHT * \
        SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
    # 0.1236
    depth = np.tan(map_depth / 2842.5 + 1.1863)
    pos = (
        math.sin(angular_x) * depth,
        depth,
        -math.sin(angular_y) * depth,
    )
    return pos


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
