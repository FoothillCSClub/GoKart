

""""
max angle range = ***(needs to be determined experimentally)***
turning left is negative, turning right is positive
range should be (-maxLeftAngle, maxRightAngle)

pwm modulation time -> one value for turnLeft, one value for turnRight, one value for don't turn at all
feedback loop -> continuously turns until reaches angle
We know it has reached angle based on encoder rotation/tick value

duty cycle (microseconds) -> sets an angular speed -> encoder gear rotation -> modify duty cycle until numrotations
reached

mapping encoder ticks to angle: (ratio of [encoder ticks / degrees turned from vertical]) * nextAngle

p-thread library
have separate threads that call turnLeft, turnRight, check encoderTick value (offload to a fast c program)

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
        -> checks whether wheels are at correct position and adjusts them to their current angle
        -> gets the current wheel angle from a sensor?
    resetWheels()
        -> sets wheels to face vertically parallel
        -> can do this from any angle
        -> gets amount to turn to reset based on sensor value
    getEncoderRotations() - may need to expand more on actually accessing encoder rotations
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

pwm = pca.PwmChip("/dev/i2c-1", 0x40)


def activate_pwm(dutycycle, channel):
    pwm.activate()
    chan = pwm.get_channel(channel)
    chan.duty_cycle = dutycycle


class Driver:
    MIN_TURN_ANGLE = -45
    MAX_TURN_ANGLE = 45
    ENCODER_RATIO = 500
    MAX_SPEED = 25

    def __init__(self, rotations):
        self.rotations = rotations

    def update_current_rotations(self):
        self.rotations = self.get_encoder_rotations()

    def get_encoder_rotations(self):
        return 1
    #need to implement ^

    def turnwheels(self, angle):
        encoder_ratio = self.ENCODER_RATIO * angle
        if angle > self.MIN_TURN_ANGLE and angle < 0:
            while self.get_encoder_rotations() != encoder_ratio:
                self.turn_left()
                self.update_current_rotations()
        elif angle < self.MAX_TURN_ANGLE and angle > 0:
            while self.get_encoder_rotations() != encoder_ratio:
                self.turn_right()
                self.update_current_rotations()

    def turn_left(self):
        self.activate_pwm(0, 1)
        self.activate_pwm(0.5, 2)

    def turn_right(self):
        self.activate_pwm(0, 0)
        self.activate_pwm(0.5, 2)

    def set_speed(self, speed):
        self.activate_pwm(speed/self.MAX_SPEED, 0)





















