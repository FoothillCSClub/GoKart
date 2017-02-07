"""
Main logic class
"""

from ..drive_data import DriveData


class Logic(object):
    def __init__(self, data: DriveData):
        self.conditions = {}
        self.data = data

    def tic(self) -> None:
        """
        Runs one logic tic;
            Evaluates each condition once, and runs appropriate methods
        :return: None
        """
        [cond.tic() for cond in self.conditions.values()]

    # todo
