"""
This module holds constants for the drive_logic package
"""

from ..const import phys_const

PREDICTION_DIST = 4  # distance within which curves are predicted
PREDICTED_POS_PER_METER = 2
PREDICTION_POS_SEP = 1 / PREDICTED_POS_PER_METER  # separation between points
MIN_POSSIBLE_PREDICTED_DIST_TO_OBSTACLE = \
    ((PREDICTION_POS_SEP / 2) ** 2 + phys_const.TRACK ** 2) ** 0.5
SAFE_DISTANCE_MOE = 1.5
SAFE_DISTANCE = SAFE_DISTANCE_MOE * MIN_POSSIBLE_PREDICTED_DIST_TO_OBSTACLE
