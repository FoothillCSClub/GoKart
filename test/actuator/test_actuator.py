"""
Tests that actuator turn_radius and speed setters, and other methods
work appropriately.
"""

from unittest import TestCase
from unittest.mock import Mock

from kart.actuator.actuator import Actuator
from kart.const.phys_const import MAX_SPEED, WHEEL_BASE


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
        self.chan1 = self.MockPwmChannel(name='steer_dir_chan (1)')  # 0 = left
        self.chan2 = self.MockPwmChannel(name='steer_mag_chan (2)')

    # SPEED PWM TESTS

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

    # WHEEL TURN PWM TESTS

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

    def test_calling_turn_wheels_with_0_radius_results_in_correct_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(0)
        self.chan2.set_duty_cycle.assert_called_with(0)

    def test_calling_turn_wheels_with_left_value_results_in_correct_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(-1)
        self.chan1.set_duty_cycle.assert_called_with(0)
        self.chan2.set_duty_cycle.assert_called_with(1)

    def test_calling_turn_wheels_with_right_value_results_in_correct_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(1)
        self.chan1.set_duty_cycle.assert_called_with(1)
        self.chan2.set_duty_cycle.assert_called_with(1)

    def test_calling_turn_wheels_w_right_fraction_results_in_correct_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(0.5)
        self.chan1.set_duty_cycle.assert_called_with(1)
        self.chan2.set_duty_cycle.assert_called_with(0.5)

    def test_calling_turn_wheels_w_left_fraction_results_in_correct_pw(self):
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(-0.75)
        self.chan1.set_duty_cycle.assert_called_with(0)
        self.chan2.set_duty_cycle.assert_called_with(0.75)

    def test_calling_turn_wheels_with_val_gt_1_results_in_correct_pw(self):
        """
        Test that calling the turn_wheels method with a value greater
        than 1 results in magnitude channel only being passed a
        value of 1.
        """
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(1.89)
        self.chan1.set_duty_cycle.assert_called_with(1)
        self.chan2.set_duty_cycle.assert_called_with(1)

    def test_calling_turn_wheels_with_val_lt_neg_1_results_in_correct_pw(self):
        """
        Test that calling the turn_wheels method with a value less than
        -1 results in magnitude channel only being passed a
        value of -1.
        """
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        a.turn_wheels(-15.7)
        self.chan1.set_duty_cycle.assert_called_with(0)
        self.chan2.set_duty_cycle.assert_called_with(1)

    # RADIUS TO WHEEL ANGLE TESTS

    def test_radius_to_wheel_angle_returns_correctly_at_10m_right_radius(self):
        # check that physical constants have not changed. If they
        # have, point out that this test is no longer accurate
        assert WHEEL_BASE == 1.04, \
            'Wheel base has changed, this test should be refactored'
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        # assert floats are equal to 7 places
        self.assertAlmostEquals(0.103627459997, a._radius_to_wheel_angle(10))

    def test_radius_to_wheel_angle_returns_correctly_at_5m_right_radius(self):
        # check that physical constants have not changed. If they
        # have, point out that this test is no longer accurate
        assert WHEEL_BASE == 1.04, \
            'Wheel base has changed, this test should be refactored'
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        # assert floats are equal to 7 places
        self.assertAlmostEquals(0.205075900383, a._radius_to_wheel_angle(5))

    def test_radius_to_wheel_angle_returns_correctly_at_0_radius(self):
        # check that physical constants have not changed. If they
        # have, point out that this test is no longer accurate
        assert WHEEL_BASE == 1.04, \
            'Wheel base has changed, this test should be refactored'
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        # assert floats are equal to 7 places
        self.assertAlmostEquals(0, a._radius_to_wheel_angle(0))

    def test_radius_to_wheel_angle_returns_correctly_at_5m_left_radius(self):
        # check that physical constants have not changed. If they
        # have, point out that this test is no longer accurate
        assert WHEEL_BASE == 1.04, \
            'Wheel base has changed, this test should be refactored'
        mock_pwm = Mock(name='mock_pwm')
        mock_pwm.get_channel = self.mock_channel_getter
        a = Actuator(None, mock_pwm)  # data instance will not be used
        # assert floats are equal to 7 places
        self.assertAlmostEquals(-0.205075900383, a._radius_to_wheel_angle(-5))

    # HELPER CLASSES

    class MockPwmChannel(Mock):
        @property
        def duty_cycle(self):
            return None

        @duty_cycle.setter
        def duty_cycle(self, duty_cycle):
            self.set_duty_cycle(duty_cycle)
