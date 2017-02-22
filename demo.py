"""
Demo module
"""
import os
import numpy as np

from pm.kinect import KinGeo
from pm.pm import Display


class Demo:
    def __init__(self):
        self.kin = KinGeo()
        self.display = Display(
            data_getter_func=lambda: np.resize(self.kin.points_arr, (-1, 3)),
            live=True
        )
        self.display.run()


if __name__ == '__main__':
    demo = Demo()
