"""
Demo module, showing points that will be used to define
navigable space.
"""
import numpy as np

from kart.kinect.pm.kinect import KinGeo
from kart.kinect.pm.pm import Display


if __name__ == '__main__':
    kin = KinGeo()
    display = Display(
        data_getter_func=lambda: np.resize(
            kin.point_cloud.nearest_non_traversable_points, (-1, 3)
        ),
        live=True
    )
    display.run()
