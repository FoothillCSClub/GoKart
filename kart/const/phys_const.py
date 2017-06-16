import math


WHEEL_BASE = 1.04  # length of cart measured from axle to axle
TRACK = 0.88  # width of cart measured from the center of wheels
# min wheel turn is the farthest left the wheels can be turned
MIN_WHEEL_TURN_ANGLE = math.radians(-30)  # todo: get more accurate value
# max wheel turn is the farthest right the wheels can be turned
MAX_WHEEL_TURN_ANGLE = math.radians(30)  # todo: get more accurate value

MAX_SPEED = 15  # currently used to determine main motor power setting.
# this ^ is not the same as limits.SPEED, as that is the maximum target
# speed that will be set, and should err low, while this value should
# err high.

DECELERATION_RATE = 1  # m/s^2  todo: measure this (placeholder value)
