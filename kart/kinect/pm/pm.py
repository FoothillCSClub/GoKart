"""
Module holding classes for displaying point-cloud information
"""

import sys
import numpy as np
import vispy.scene as scene
import vispy.app as app
import PyQt5  # used by vispy.app, the import here is used as a marker.

from vispy.scene import visuals


class Display:
    """
    Class using VisPy to display visualization of data to user
    """

    def __init__(self, data_getter_func, live=False):
        """
        Initializes Display
        :param live: Whether data is live; determines whether data is
        updated for each draw frame.
        """
        # Make canvas and add view
        self.pos = None
        self.canvas = PointMapCanvas(keys='interactive', show=True)
        self._data_getter = data_getter_func
        self.view = self.canvas.central_widget.add_view()
        # visuals constructs visual classes at run-time.
        # Markers class is defined then.
        self.points = visuals.Markers(parent=self.view.scene)  # not an error
        self.update_data()
        self.view.add(self.points)
        self.view.camera = 'turntable'
        self.axis = visuals.XYZAxis(parent=self.view.scene)  # not an error

        if live:
            self.canvas.draw_func = self.update_data

    def run(self):
        if sys.flags.interactive != 1:
            app.run()

    def update_data(self):
        self.pos = self._data_getter()
        self.points.set_data(  # set points data to generated points
            self.pos, edge_color=None, face_color=(1, 1, 0.9, .5), size=5)

    @property
    def live_data_getter(self):
        """
        Gets data array to display
        :return: callable
        """
        return self._data_getter

    @live_data_getter.setter
    def live_data_getter(self, func):
        """
        Sets data getter function
        :return: None
        """
        self._data_getter = func


class PointMapCanvas(scene.SceneCanvas):
    """
    Extends SceneCanvas from VisPy library
    """
    _draw_func = None  # function called each time canvas is drawn

    @property
    def draw_func(self):
        """
        Function called at draw time, each frame
        :return: None
        """
        return self._draw_func

    @draw_func.setter
    def draw_func(self, func):
        self._draw_func = func

    def on_draw(self, event):
        super().on_draw(event)
        if self._draw_func:
            self._draw_func()


if __name__ == '__main__':
    display = Display(lambda: np.random.normal(size=(1000, 3)), False)
    display.run()
