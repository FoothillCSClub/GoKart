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

MAX_SLOPE = math.radians(20.)


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
        self._points_arr = None
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
        dm = self.depth_map  # get depth map (a 2d numpy array)
        cloud_height = int(SENSOR_PIXEL_HEIGHT / SAMPLE_DISTANCE) + 1
        cloud_width = int(SENSOR_PIXEL_WIDTH / SAMPLE_DISTANCE) + 1
        # make array that point positions will be stored in
        points = np.ndarray((cloud_height, cloud_width, 3), np.float32)
        half_px_width = SENSOR_PIXEL_WIDTH / 2
        half_px_height = SENSOR_PIXEL_HEIGHT / 2
        # for all combinations of x and y...
        x_range = range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE)
        y_range = range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE)
        for x, y in itr.product(x_range, y_range):
            # create a point in the newly formed point-cloud.
            depth = float(dm[y][x])
            if depth == 2047:
                # if depth is max value, set marker value and go on
                points[y/SAMPLE_DISTANCE][x/SAMPLE_DISTANCE] = (0, 0, 0)
                continue
            angular_x = (x - half_px_width) / SENSOR_PIXEL_WIDTH * \
                SENSOR_ANGULAR_WIDTH
            angular_y = (y - half_px_height) / SENSOR_PIXEL_HEIGHT * \
                SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
            depth_from_cam = depth + 819.
            # TODO: fix x, y, z coordinate algorithms
            # currently, x and z values are spurious
            pos = np.array((
                math.sin(angular_x) * depth_from_cam / 2048,
                0.1236 * math.tan(depth / 2842.5 + 1.1863),
                # invert y because y positions in depth map are ordered
                # top->bottom but spatially, height increases bottom->top
                - math.sin(angular_y) * depth_from_cam / 2048,
            )).astype(np.float32)
            points[y/SAMPLE_DISTANCE][x/SAMPLE_DISTANCE] = pos
        return points

    @property
    def traversable_points(self):
        """
        Returns array of booleans indicating whether the point at the
        same position in point_arr is able to be traversed
        At the moment, simply tests the angle of the slope between
        one point and the next in the column, and if the slope is
        greater than maximum value set in constant, sets that position
        to false in the array.
        Points in point_arr that are empty should not be accessed,
        and therefor do not have a value set.
        :return: np.array(boolean)
        """
        points = self.points_arr
        bools = np.ndarray(points.shape[0], points.shape[1])  # make bool array
        x_range = range(1, points.shape[1])
        y_range = range(1, points.shape[0])
        for x, y in itr.product(x_range, y_range):  # for each x, y combo
            if slope(points[y][x], points[y - 1][x]) > MAX_SLOPE or \
                    slope(points[y][x], points[y][x - 1]) > MAX_SLOPE:
                bools[x][y]


def slope(p1, p2):
    """
    Gets slope from p1 to p2 as a 2d vector based on height (z)
    position as radian
    :param p1: np.array len 3
    :param p2: np.array len 3
    :return: float (radians)
    """



if __name__ == '__main__':
    kin_geo = KinGeo()  # create kinect handler obj
    test_dm = kin_geo.depth_map
    print(len(test_dm))
    print(len(test_dm[0]))
    print(len(test_dm[0][0]))
    print(test_dm[1])
