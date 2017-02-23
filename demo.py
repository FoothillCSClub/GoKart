"""
Demo module
"""
import os

from pm.kinect import KinGeo
from pm.pm import Display


class Demo:
    def __init__(self):
        self.kin = KinGeo()
        self.display = Display(
            data_getter_func=lambda: self.kin.points_arr,
            live=True
        )
        self.display.run()


if __name__ == '__main__':
    demo = Demo()
