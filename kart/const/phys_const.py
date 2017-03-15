import math


WHEEL_BASE = 2  # todo: measure this (placeholder value)
TRACK = 1  # todo: measure this (placeholder value)
# min wheel turn is the farthest left the wheels can be turned
MIN_WHEEL_TURN_ANGLE = math.radians(-45)  # todo: replace placeholder
# max wheel turn is the farthest right the wheels can be turned
MAX_WHEEL_TURN_ANGLE = math.radians(45)  # todo: replace placeholder

MAX_SPEED = 25  # currently used to determine main motor power setting.
# this ^ is not the same as limits.SPEED, as that is the maximum target
# speed that will be set, and should err low, while this value should
# err high.

DECELERATION_RATE = 1  # m/s^2  todo: measure this (placeholder value)
