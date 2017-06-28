"""
This module holds motion controllers
"""
try:
    from ..hardware import pca9685 as pca
except OSError as e:
    pca = None
    print('could not import pca9685 from hardware: ' + str(e))
from ..const.phys_const import MIN_WHEEL_TURN_ANGLE, MAX_WHEEL_TURN_ANGLE, \
    MAX_SPEED as PHYS_MAX_SPEED


ENCODER_RATIO = 500

# TODO: move method docs to the appropriate method in Actuator
""""
max angle range = 67 degrees (each way), but let's say 60 (each way) to be safe. These numbers are drawn from here: 
https://github.com/orrblue/GoKart/blob/master/autonomous_steering/autonomous_steering.ino
turning left is negative, turning right is positive
range should be (-maxLeftAngle, maxRightAngle)

pwm modulation time -> one value for turnLeft, one value for turnRight,
one value for don't turn at all
feedback loop -> continuously turns until reaches angle
We know it has reached angle based on encoder rotation/tick value

duty cycle (microseconds) -> sets an angular speed ->
encoder gear rotation -> modify duty cycle until numrotations
reached

mapping encoder ticks to angle: (ratio of [encoder ticks /
degrees turned from vertical]) * nextAngle

p-thread library
have separate threads that call turnLeft, turnRight,
check encoderTick value (offload to a fast c program)

linear potentiometer (sensor that tells us how the wheels have turned)

::: HYPOTHETICAL SAMPLE RUN :::
turnWheels(-40)
turnWheels(30)

instance variables
    current angle
        -> tells us what angle the wheel is at right now
        -> modified every time wheel turns
        -> number of encoder gear rotations

constants
    -> ENCODER_RATIO: ratio for encoder ticks -> angle
    -> DO_NOT_TURN: microseconds value for turning 0 degrees from parallel
    -> TURN_LEFT: microseconds value for turning left
    -> TURN_RIGHT: microseconds value for turning right
    -> MAX_TURN_ANGLE: max angle to turn
    -> MIN_TURN_ANGLE: min angle to turn

methods
    turnWheels(double angle)
        -> sets wheels to the angle from the vertical based on a given angle
        -> modifies current angle
        -> *** FOR NOW, ASSUME INITIAL POSITION IS VERTICAL ***
    turnLeft()
        -> turns left for some time period
    turnRight()
        -> turns right for some time period
    getCurrentAngle()
        -> returns current angle
    updateCurrentAngle()
        -> updates current angle based on rotations
    calculateTurnRadius(double angle)
        -> calculates and returns turnRadius based on a given angle
            adjustWheels()
        -> checks whether wheels are at correct position and adjusts
            them to their current angle
        -> gets the current wheel angle from a sensor?
            resetWheels()
        -> sets wheels to face vertically parallel
        -> can do this from any angle
        -> gets amount to turn to reset based on sensor value
    getEncoderRotations() - may need to expand more on actually
            accessing encoder rotations
        -> when called returns the current number of encoder ticks



turnWheels(double angle)
{
    if angle < 0 and greater than MIN_TURN_ANGLE
        while(getEncoderRotations != ENCODER_RATIO * angle) - use compareTo
            turnLeft() //set speed turnLeft
            updateCurrentAngle()

    if angle > 0 and less than MAX_TURN_ANGLE
        while(getEncoderRotations != ENCODER_RATIO * angle) - use compareTo
            turnRight()
            updateCurrentAngle()

}
"""""


class Actuator(object):
    def __init__(self, drive_data, pwm=None):
        self.pwm = pwm if pwm else pca.PwmChip("/dev/i2c-1", 0x40)
        self.pwm.activate()
        self.data = drive_data
        self.rotations = self.find_steering_start_position()
        self.dir_chan = pwm.get_channel(1)  # direction channel; 0 == left
        self.mag_chan = pwm.get_channel(2)  # turn rate channel
        self.speed_chan = pwm.get_channel(0)  # main motor power channel

        self._tgt_turn_radius = 0  # these should always begin zeroed
        self._tgt_speed = 0  # these should always begin zeroed

    def update_current_rotations(self):
        self.rotations = self.get_encoder_rotations()

    def find_steering_start_position(self) -> float:
        """
        Finds starting position in rotations
        :return: number
        """
        # todo

    def get_encoder_rotations(self):
        return 1

    # need to implement ^

    def turn_wheels(self, angle):
        # this method as currently implemented will likely never exit.
        # TODO: This method should be re-written that it can be be called
        # continuously and set wheel turn each time.
        # TODO: wheel turn rate should also be reduced as the target angle is
        # approached so that the wheels are not subject to stutter

        # if angle is outside bounds, throw exception
        if not MIN_WHEEL_TURN_ANGLE < angle < MAX_WHEEL_TURN_ANGLE:
            raise ValueError(
                'Actuator.turn_wheels: Passed angle {} was outside bounds '
                '({} to {})'.format(
                    angle, MIN_WHEEL_TURN_ANGLE, MAX_WHEEL_TURN_ANGLE
                )
            )
        encoder_ratio = ENCODER_RATIO * angle
        if angle > self.MIN_TURN_ANGLE and angle < 0:
            while self.get_encoder_rotations() != encoder_ratio:
                self.turn_wheels_left()
                self.update_current_rotations()
        elif angle < self.MAX_TURN_ANGLE and angle > 0:
            while self.get_encoder_rotations() != encoder_ratio:
                self.turn_wheels_right()
                self.update_current_rotations()

    def turn_wheels_left(self, rate=1):
        """
        Helper method, sets PWM channel so as to have the steering
        motor move turning wheels to the left at passed rate, with
        1 being max rate.
        :param rate: float 0 to 1
        :return None
        """
        self.dir_chan.duty_cycle = 0
        self.mag_chan.duty_cycle = rate

    def turn_wheels_right(self, rate=1):
        """
        Helper method, sets PWM channel so as to have the steering
        motor move turning wheels to the right at passed rate, with
        1 being max rate.
        :param rate: float 0 to 1
        :return None
        """
        self.dir_chan.duty_cycle = 1
        self.mag_chan.duty_cycle = rate

    def stop_wheel_turn(self):
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
        # TODO

    @turn_radius.setter
    def turn_radius(self, turn_radius: float) -> None:
        """
        Sets the current turn radius in meters.
        negative for left, positive for right, 0 for no turn.
        :param turn_radius: float (m)
        :return: None
        """
        # TODO

    ###################################################################

    def _get_steering_link_move_distance(self, wheel_rotation: float) -> float:
        """
        Gets distance required of
        :return:
        """

    def _get_steering_column_rot(self, steering_link_motion: float) -> float:
        """
        Gets rotation required of steering column
        :return:
        """


class VirtualActuator(object):
    pass  # TODO
