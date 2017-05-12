import freenect as fn
import time as t
import pyximport
import numpy as np

# build cython functions
pyximport.install()
from . import cyfunc

# grab PointCloud class from cyfunc so that it can be used here and
# elsewhere more conveniently, without importing a cython file
PointCloud = cyfunc.PointCloud


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
        # todo: set inclination to 0

    @property
    def t_since_last_frame(self) -> float:
        """
        Returns time since last depth frame was accessed from Kinect
        :return: float
        """
        return t.time() - self.last_access

    @property
    def access_hz(self) -> float:
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
    def depth_map(self) -> 'DepthMap':
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
    def point_cloud(self) -> 'PointCloud':
        """
        Gets point cloud of positions from depth map.
        Returns point cloud as three dimensional array of
        [column][row][point position]
        :return: PointCloud
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
    def point_cloud(self) -> 'PointCloud':
        if not self._point_cloud:
            self._point_cloud = PointCloud(self.arr)
        return self._point_cloud

    def dump(self, path: str) -> None:
        assert isinstance(self.arr, np.ndarray)
        self.arr.dump(path)

    @classmethod
    def load(cls, path: str) -> 'DepthMap':
        return cls(np.load(path))  # return new DepthMap with array from file
