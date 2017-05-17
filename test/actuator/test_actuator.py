"""
Tests that actuator turn_radius and speed setters, and other methods
work appropriately.
"""

from unittest import TestCase
from unittest.mock import Mock

from kart.actuator.actuator import Actuator
from kart.const.phys_const import MAX_SPEED


class TestActuator(TestCase):

    def mock_channel_getter(self, chan_num: int):
        if chan_num == 0:
            return self.chan0
        if chan_num == 1:
            return self.chan1
        if chan_num == 2:
            return self.chan2

    def mock_duty_cycle_setter(self, pulse_width: float):
        self.pulse_width = pulse_width

    def setUp(self):
        self.chan0 = self.MockPwmChannel(name='speed_chan (0)')
        self.chan1 = self.MockPwmChannel(name='steer_dir_chan (1)')
        self.chan2 = self.MockPwmChannel(name='steer_mag_chan (2)')

    def test_that_setting_speed_0_results_in_speed_pulse_width_0(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.speed = 0
        self.chan0.set_duty_cycle.assert_called_with(0)

    def test_setting_max_speed_results_in_speed_pulse_width_1(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.speed = MAX_SPEED
        self.chan0.set_duty_cycle.assert_called_with(1)

    def test_calling_stop_wheel_turn_results_in_steer_mag_pw_of_0(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.stop_wheel_turn()
        self.chan2.set_duty_cycle.assert_called_with(0)

    def test_calling_turn_wheels_right_results_in_correct_direction_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels_right()
        self.chan1.set_duty_cycle.assert_called_with(1)

    def test_calling_turn_wheels_left_results_in_correct_direction_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels_left()
        self.chan1.set_duty_cycle.assert_called_with(0)

    class MockPwmChannel(Mock):
        @property
        def duty_cycle(self):
            return None

        @duty_cycle.setter
        def duty_cycle(self, duty_cycle):
            self.set_duty_cycle(duty_cycle)
