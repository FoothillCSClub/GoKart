"""
Convenience script for saving a single depth map to a file specified
by the user.
"""
import os

from kart.kinect.demo import KinGeo
from test.settings import TEST_RESOURCES_ROOT

name = input('enter name for file: ')

tgt_path = os.path.join(TEST_RESOURCES_ROOT, 'depth_maps', name)
KinGeo().depth_map.dump(tgt_path)
