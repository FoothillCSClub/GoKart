"""
Tests functionality of classes and functions in kinect module
"""
import numpy as np

from tempfile import mkstemp
from unittest import TestCase

from kart.kinect.pm.kinect import KinGeo, DepthMap


class TestDepthMap(TestCase):
    def test_depth_map_can_be_dumped_to_file_path_and_reloaded(self):
        # Requires connected sensor
        depth_map = KinGeo().depth_map
        file_path = mkstemp()[1]  # func returns (file-like, abs-path)
        depth_map.dump(file_path)
        reloaded_dm = DepthMap.load(file_path)
        self.assertTrue(np.array_equal(depth_map.arr, reloaded_dm.arr))
