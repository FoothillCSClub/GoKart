"""
holds methods used to safely end program in the event exceptions are
thrown and things go poorly elsewhere in the program.

Logic here should be minimized and assumptions about the state of the
rest of the program should be kept to an absolute minimum.
"""


def failsafe_stop():
    """
    Method called to stop vehicle as quickly as possible.
    This method is intended to be called only when exceptions have been
    raised, and so should not worry about exiting gracefully, simply
    with as much physical safety as possible.
    :return:
    """
