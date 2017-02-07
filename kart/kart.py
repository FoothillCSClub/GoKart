"""
Main Module, holds GoKart class
"""
# tentative structure. There may be a better way to do this.
# Someone please say something if this is a terrible idea
#
# My thinking is that it is better to have each of these
# following methods separated into separate threads so that delays
# or hiccups do not bring down the whole program.
#
# Other thoughts:
# It may be better to use a multiprocessing implementation
# rather than a multi-threaded one for performance reasons,
# however my first impression is that that would be more
# inconvenience then benefit.

import threading as th
import typing as ty

from .drive_data import DriveData

FAIL_SAFE_FRQ = 4  # Hz


class GoKart:
    """
    Main class, holds references to data, logic, input, and control
    classes and calls them as appropriate.
    """
    def __init__(self):
        """
        Instantiates GoKart class and creates instance of
        logic instances at start of run.
        """
        self.drive_data = DriveData()
        self.sensor_th = th.Thread(
            target=self.sensor_main,
            name='Sensor Thread')
        self.logic_th = th.Thread(
            target=self.logic_main,
            name='Logic Thread')
        self.actuator_th = th.Thread(
            target=self.actuator_main,
            name='Actuator Thread')
        self.fail_safe_th = th.Thread(
            target=self.fail_safe_main,
            name='Fail-Safe Thread')
        # convenience iterable
        self.main_threads = self.sensor_th, self.actuator_th, self.logic_th

    def main(self) -> None:
        """
        Continuously updates drive_data with information from sensors,
        gets commands from drive_logic and calls motion_controller
        methods.
        :return: None
        """
        self.sensor_th.start()
        self.logic_th.start()
        self.actuator_th.start()
        self.fail_safe_th.start()
        # TODO: exit conditions, error handling, etc

    def sensor_main(self) -> None:
        """
        Main method for sensor handling thread.
        Responsible for collecting sensor information and updating
        DriveData
        :return: None
        """
        # TODO

    def logic_main(self) -> None:
        """
        Main method for logic handling thread.
        Responsible for analyzing information in DriveData and
        setting target speed / turn radius / any other values
        :return: None
        """
        # TODO

    def actuator_main(self) -> None:
        """
        Main method that controls output based on set target speed
        and turn radius (and any other values that may become important)
        :return: None
        """
        # TODO

    def fail_safe_main(self) -> None:
        """
        Method that looks for fatal errors in any of the other threads
        and is responsible for preventing bad things from happening.
        This thread should bring everything to a halt and not be
        worried about any kind of graceful error recovery or whatnot

        Things this thread should look for are;
            non-responsive main threads

        :return: None
        """
        while True:
            if not self.all_threads_running:
                print('MAIN THREAD HAS DIED')
                # todo: prevent disaster
            th.current_thread().sleep(1/FAIL_SAFE_FRQ)
            # is there a better way to handle frequent sleeping?

    @property
    def all_threads_running(self) -> bool:
        """
        Returns bool of whether all threads are running normally.
        This returns false if any thread has exited, died due to an
        exception, or any other cause.
        :return: bool
        """
        return all(thread.is_alive() for thread in self.main_threads)


if __name__ == '__main__':
    print('began main')
    kart = GoKart()
    kart.main()
    print('ended main')