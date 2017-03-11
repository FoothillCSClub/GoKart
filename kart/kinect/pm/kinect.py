import freenect as fn
import time as t
import math
import mathutils as mu
import numpy as np
import pyximport
import typing as ty

# build cython functions
pyximport.install()
from . import cyfunc

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
        self._point_arr = np.ndarray((self.arr_height, self.arr_width, 3))

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
                cyfunc.pos_from_depth_map_point(x, y, self.depth_arr[0][y][x])
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
            self._point_arr = cyfunc.fill_point_cloud(  # todo
                    depth_array=self.depth_arr[0],
                    point_array=self._point_arr if self._point_arr else None
                )
        return self._point_arr

    @property
    def time_stamp(self) -> int:
        """
        gets time at which depth map used to generate this PointCloud
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
        return cyfunc.CLOUD_WIDTH

    @property
    def arr_height(self):
        """
        Gets height in sampled pixels of point cloud.
        This is the height of the PointCloud's point array.
        :return: int
        """
        return cyfunc.CLOUD_HEIGHT

    @property
    def nearest_non_traversable_geometry_quadmap(self):
        """
        Gets quadmap of points that represent the nearest
        non-traversable point for each column of points in PointCloud
        :return: QuadMap
        """
        return cyfunc.get_nearest_non_traversible_points()