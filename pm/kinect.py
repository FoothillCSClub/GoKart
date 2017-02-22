import freenect as fn
import time as t
import math
import itertools as itr
import numpy as np

SAMPLE_DISTANCE = 10

SENSOR_MAX_DEPTH = 4.
SENSOR_PIXEL_HEIGHT = 480
SENSOR_PIXEL_WIDTH = 640
SENSOR_ANGULAR_WIDTH = math.radians(58.5) * 2;
SENSOR_ANGULAR_HEIGHT = math.radians(46.6) * 2
SENSOR_ANGULAR_ELEVATION = math.radians(0.)


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
        self._depth_arr = None  # holds numpy array of
        self._pc_timestamp = 0.

        # fn.set_depth_mode(self.device, 0, 5)

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
        Gets depth map as numpy array.
        :return: np.Array
        """
        # If elapsed time since last frame is greater than frame
        # rate, update depth map.
        if self.t_since_last_frame > self._frame_time:
            # get depth map from first Kinect found
            self._depth_arr = fn.sync_get_depth()
            if not self._depth_arr:
                raise OSError('Could not connect to Kinect')
        # Return the depth-map portion of the depth map array.
        # The second part of the array is the timestamp.
        return self._depth_arr[0]

    @property
    def points_arr(self):
        """
        Gets point cloud of positions from depth map.
        Returns point cloud as three dimensional array of
        [column][row][point position]
        :return: np.Array
        """
        # TODO: make this method more efficient
        # This should be looked at once the coordinates are
        # accurately generated.
        dm = self.depth_map
        cloud_height, cloud_width = (int(dim_size / SAMPLE_DISTANCE) + 1
            for dim_size in (SENSOR_PIXEL_HEIGHT, SENSOR_PIXEL_WIDTH))
        # make array that point positions will be stored in
        points = np.ndarray((cloud_height, cloud_width, 3), np.float32)
        half_px_width = SENSOR_PIXEL_WIDTH / 2
        half_px_height = SENSOR_PIXEL_HEIGHT / 2
        # for each all combinations of x and y...
        x_range = range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE)
        y_range = range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE)
        for x, y in itr.product(x_range, y_range):
            # create a point in the newly formed point-cloud.
            depth = float(dm[y][x])
            if depth == 2047:
                # if depth is max value, set marker value and go on
                points[y][x] = (0, 0, 0)
                continue
            angularX = (x - half_px_width) / SENSOR_PIXEL_WIDTH * \
                SENSOR_ANGULAR_WIDTH
            angularY = (y - half_px_height) / SENSOR_PIXEL_HEIGHT * \
                SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
            depth_from_cam = depth + 819.
            # TODO: fix x, y, z coordinate algorithms
            # currently, x and z values are spurious
            pos = np.array((
                math.sin(angularX) * depth_from_cam / 2048,
                # angularX,
                # math.cos(angularXs) * math.cos(angularY) * depth,
                0.1236 * math.tan(depth / 2842.5 + 1.1863),
                # 393216
                # 524288
                - math.sin(angularY) * depth_from_cam / 2048,
                # -angularY
            )).astype(np.float32)
            points[y][x] = pos
        return points

if __name__ == '__main__':
    kin_geo = KinGeo()  # create kinect handler obj
    test_dm = kin_geo.depth_map
    print(len(test_dm))
    print(len(test_dm[0]))
    print(len(test_dm[0][0]))
    print(test_dm[1])
