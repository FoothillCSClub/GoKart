"""
This module runs a visualization of sensor input, the pointcloud
generated from the passed sensor input, the detected border of
navigable space, and the path selected by the Logic class.
"""

import sys
import numpy as np
import vispy.scene as scene
import vispy.app as app
import PyQt5  # used by vispy.app, the import here is used as a marker.

from scipy.spatial.kdtree import KDTree
from vispy.scene import visuals

from kart.kinect.pm.kinect import KinGeo
from kart.drive_data.data import DriveData
from kart.drive_logic.logic import SimpleColAvoidLogic
from kart.drive_logic.turn_table import Arc

# display_scale =


class ComboDemoCanvas(scene.SceneCanvas):
    """
    Extends SceneCanvas from VisPy library
    """

    def __init__(self):
        """
        Initializes Display
        """
        # Make canvas and add view
        self.pos = None
        self.kin = KinGeo()
        self.drive_data = DriveData()
        self.logic = SimpleColAvoidLogic(self.drive_data)
        self.bound_point_data = None
        super().__init__(keys='interactive', show=True)
        self.view = self.central_widget.add_view()
        # visuals constructs visual classes at run-time.
        # Markers class is defined then.
        self.sampled_points = self.SamplePoints(parent=self.view.scene)
        self.view.add(self.sampled_points)
        self.bound_points = self.BoundPoints(parent=self.view.scene)
        self.view.add(self.bound_points)
        self.path_points = self.PathPoints(parent=self.view.scene)
        self.view.add(self.path_points)

        self._update_data()
        self.view.camera = 'turntable'
        self.axis = visuals.XYZAxis(parent=self.view.scene)  # not an error

    @staticmethod
    def run():
        if sys.flags.interactive != 1:
            app.run()

    def on_draw(self, event):
        super().on_draw(event)
        self._update_data()

    def _update_data(self):
        self._update_sampled_positions()
        self._update_boundary_positions()
        self._update_path_positions()

    def _update_sampled_positions(self):
        sampled_point_data = np.resize(self.kin.points_arr, (-1, 3))
        self.sampled_points.set_data(  # set points data to generated points
            sampled_point_data,
            edge_color=None,
            face_color=(1, 1, 0.9, .5),  # white
            size=5)

    def _update_boundary_positions(self):
        self.bound_point_data = \
            self.kin.point_cloud.nearest_non_traversable_points
        self.bound_points.set_data(  # set points data to generated points
            self.bound_point_data,
            edge_color=None,
            face_color=(1, 0.2, 0.24, .5),  # red
            size=9)

    def _update_path_positions(self):
        flat_points = []
        for x, pos in enumerate(self.bound_point_data):
            if pos[1] > 0:
                flat_points.append((pos[0], pos[1]))
        self.drive_data.col_avoid_pointmap = KDTree(flat_points)
        self.logic.tic()
        arc = Arc(self.logic.target_turn_radius)
        arc_positions = \
            np.array([(pos[0], pos[1], 0) for pos in arc.positions])
        self.path_points.set_data(  # set points data to generated points
            arc_positions,
            edge_color=None,
            face_color=(0.2, 0.9, 0.24, .5),  # green
            size=15)

    class SamplePoints(visuals.Markers):
        pass

    class BoundPoints(visuals.Markers):
        pass

    class PathPoints(visuals.Markers):
        pass

if __name__ == '__main__':
    canvas = ComboDemoCanvas()
    canvas.run()
