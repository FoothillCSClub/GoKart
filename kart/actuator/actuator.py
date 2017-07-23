"""
This module holds motion controllers
"""

import math
# try to import pca module, but that might not be possible if we're
# just doing a unittest or testing in a simulated environment
try:
    from ..hardware import pca9685 as pca
except OSError as e:
    pca = None
    print('could not import pca9685 from hardware: ' + str(e))
from ..const.phys_const import MIN_WHEEL_TURN_ANGLE, MAX_WHEEL_TURN_ANGLE, \
    MAX_SPEED as PHYS_MAX_SPEED, WHEEL_BASE


# angle in radians within which the wheel turn rate is
# reduced as actual angle approaches target angle.
# prevents wheel 'stutter' by reducing speed as wheel angle
# approaches target.
WHEEL_TURN_DAMPER_ANGLE = 0.0174  # 0.0174 radians == 1 degrees

# todo: remove todo comments as they are completed
# todo: write wheel_angle getter
#


class Actuator(object):
    """
    Actuator class is responsible for taking
    """
    def __init__(self, drive_data, pwm=None):
        self.pwm = pwm if pwm else pca.PwmChip("/dev/i2c-1", 0x40)
        self.pwm.activate()
        self.data = drive_data
        self.dir_chan = self.pwm.get_channel(1)  # direction channel; 0 == left
        self.mag_chan = self.pwm.get_channel(2)  # turn rate channel
        self.speed_chan = self.pwm.get_channel(0)  # main motor power channel

        self._tgt_turn_radius = 0  # these should always begin zeroed
        self._tgt_speed = 0  # these should always begin zeroed
    def tic(self) -> None:
        """
        Called in a loop by the actuator thread.
        """
        tgt_angle = self._radius_to_wheel_angle(self.turn_radius)
        self.update_steering_servo(tgt_angle)

    def update_steering_servo(self, tgt_angle) -> None:
        """
        Updates instructions to steering servo based on current wheel
        position and passed target angle
        """
        # if angle is outside bounds, throw exception
        if not MIN_WHEEL_TURN_ANGLE < tgt_angle < MAX_WHEEL_TURN_ANGLE:
            raise ValueError(
                'Actuator.turn_wheels: Passed angle {} was outside bounds '
                '({} to {})'.format(
                    tgt_angle, MIN_WHEEL_TURN_ANGLE, MAX_WHEEL_TURN_ANGLE
                )
            )
        # find target wheel angle from passed turn radius
        difference = self.wheel_angle - tgt_angle
        # difference is positive if actual position is right of tgt
        # negative if actual position is left of target.
        rate = -difference / WHEEL_TURN_DAMPER_ANGLE
        self.turn_wheels(rate)

    def turn_wheels(self, rate) -> None:
        """
        Turns wheels left or right depending on the passed rate.
        If a negative number is passed, turns left, if positive,
        turns right.
        If a number greater than 1 or less than -1 is passed, it is
        treated as 1 or -1 respectively.
        Passing 0 stops all rotation.
        :param rate: float from -1 to 1.
        :return:
        """
        if rate > 1:
            rate = 1
        elif rate < -1:
            rate = -1
        self.dir_chan.duty_cycle = 1 if rate >= 0 else 0
        self.mag_chan.duty_cycle = abs(rate)

    def turn_wheels_left(self, rate=1) -> None:
        """
        Helper method, sets PWM channel so as to have the steering
        motor move turning wheels to the left at passed rate, with
        1 being max rate.
        :param rate: float 0 to 1
        :return None
        """
        self.dir_chan.duty_cycle = 0
        self.mag_chan.duty_cycle = rate

    def turn_wheels_right(self, rate=1) -> None:
        """
        Helper method, sets PWM channel so as to have the steering
        motor move turning wheels to the right at passed rate, with
        1 being max rate.
        :param rate: float 0 to 1
        :return None
        """
        self.dir_chan.duty_cycle = 1
        self.mag_chan.duty_cycle = rate

    def stop_wheel_turn(self) -> None:
        """
        Sets PWM channel so as to instruct steering motor to stop.
        :return: None
        """
        self.mag_chan.duty_cycle = 0

    @property
    def speed(self) -> float:
        """
        Gets the currently set speed in m/s
        :return: float (m/s)
        """
        return self._tgt_speed

    @speed.setter
    def speed(self, speed: float) -> None:
        """
        Takes a speed in m/s (for sake of keeping with SI units)
        and sets motor throttle so as to attempt to match cart speed
        to that passed.
        :param speed: float (m/s)
        :return: None
        """
        self._tgt_speed = speed
        self.speed_chan.set_duty_cycle(speed / PHYS_MAX_SPEED)
        # take into account our lack of a differential?
        # if a speed sensor is added in the future, this method should
        # be updated

    @property
    def turn_radius(self) -> float:
        """
        Gets the currently set turn radius in meters.
        :return: float (negative left, positive right, 0 == no turn)
        """
        return self._tgt_turn_radius

    @turn_radius.setter
    def turn_radius(self, turn_radius: float) -> None:
        """
        Sets the current turn radius in meters.
        negative for left, positive for right, 0 for no turn.
        :param turn_radius: float (m)
        :return: None
        """
        self._tgt_turn_radius = turn_radius

    @property
    def wheel_angle(self) -> float:
        """
        Gets the current angle of the steering wheels.
        :return: angle in radians.
        """
        return None  # todo: get value from appropriate clib wrapper

    @staticmethod  # doesn't need to be an Actuator member, but it makes sense.
    def _radius_to_wheel_angle(turn_radius: float) -> float:
        """
        Converts a passed turn radius into the corresponding wheel angle
        that would result in the passed turn radius
        :param: float of turn radius
        :return: float of wheel angle in radians
        """
        # if turn radius is 0, vehicle should move straight ahead, return 0
        if turn_radius == 0:
            return 0
        return math.atan(WHEEL_BASE / turn_radius)


class VirtualActuator(object):
    pass  # TODO
