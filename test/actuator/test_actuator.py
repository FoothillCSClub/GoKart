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

    def setUp(self):
        self.chan0 = Mock(name='speed_chan (0)')
        self.chan1 = Mock(name='steer_dir_chan (1)')
        self.chan2 = Mock(name='steer_mag_chan (2)')

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
