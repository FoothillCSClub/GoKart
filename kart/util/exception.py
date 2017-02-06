"""
Holds exceptions to be used across packages
"""


class DriveException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


# TODO: this may be an unneeded exception class,
        # or it may need to be expanded
