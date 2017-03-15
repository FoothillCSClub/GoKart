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
import time

from .drive_data.data import DriveData

# Main function call frequencies.
# Can be used to limit the amount of cpu time a thread uses
# to prevent fast running threads from hogging system resources.
# 0 is unlimited
# These should be edited as needed.
SENSOR_TH_FRQ = 60  # Hz
LOGIC_FRQ = 60      # Hz
ACTUATOR_FRQ = 60   # Hz


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
        # convenience iterable
        self.main_threads = self.sensor_th, self.actuator_th, self.logic_th

    def main(self) -> None:
        """
        Continuously updates drive_data with information from sensors,
        gets commands from drive_logic and calls motion_controller
        methods.
        :return: None
        """
        try:
            self.sensor_th.start()
            self.logic_th.start()
            self.actuator_th.start()
        except Exception:
            # catch any exception that would end program execution so
            # that we can prevent disaster
            pass  # TODO
        # TODO: exit conditions, error handling, etc

    @loop(SENSOR_TH_FRQ)
    def sensor_main(self) -> None:
        """
        Main method for sensor handling thread.
        Responsible for collecting sensor information and updating
        DriveData
        :return: None
        """
        # TODO

    @loop(LOGIC_FRQ)
    def logic_main(self) -> None:
        """
        Main method for logic handling thread.
        Responsible for analyzing information in DriveData and
        setting target speed / turn radius / any other values
        :return: None
        """
        # TODO

    @loop(ACTUATOR_FRQ)
    def actuator_main(self) -> None:
        """
        Main method that controls output based on set target speed
        and turn radius (and any other values that may become important)
        :return: None
        """
        # TODO

    @property
    def all_threads_running(self) -> bool:
        """
        Returns bool of whether all threads are running normally.
        This returns false if any thread has exited, died due to an
        exception, or any other cause.
        :return: bool
        """
        return all(thread.is_alive() for thread in self.main_threads)


def loop(frq: float=0., exit_test: ty.Callable[[], bool]=None):
    """
    Returns a decorator that loops function at specified frq (in Hz)
    for as long as program runs or until a passed exit_test
    returns True.

    This decorator is intended to be placed on a method, since it
    passes a 'self' arg. If it in the future needs to be applied to
    functions not belonging to a class, the implementation can be
    updated for the wider scope.

    :param frq: frequency at which function is looped
    :param exit_test: Callable[[] bool]
    :return: decorator
    """
    loop_t = 1/frq if frq > 0 else 0

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            while exit_test() if exit_test else True:
                # is there a better way to handle frequent sleeping?
                start_time = time.time()
                func(self, *args, **kwargs)  # call decorated method
                elapsed_t = time.time() - start_time
                if loop_t > elapsed_t:
                    time.sleep(loop_t - elapsed_t)  # sleeps current thread
        return wrapper
    return decorator


if __name__ == '__main__':
    print('began main')
    kart = GoKart()
    kart.main()
    print('ended main')
