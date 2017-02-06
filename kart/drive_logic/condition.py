"""
module holding condition logic class
"""
import typing as ty


class Condition(object):
    """
    Class that holds a single test, and signals appropriate Actions
    depending on its state
    """

    def __init__(self, state_test: ty.Callable):
        self.test = state_test
        self.last_state = None
        self.on_true_funcs = []
        self.on_false_funcs = []
        self.while_true_funcs = []
        self.while_false_funcs = []
        
    def tic(self):
        """
        logic tic: updates condition and calls methods as appropriate
        :return: None
        """
        # why does this next line raise an ide warning??? (Pycharm) 
        # anyone? ;  "'Callable' object is not callable"
        new_state = self.test()  
        if new_state and not self.last_state:
            _run_all(self.on_true_funcs)  # run all on_true funcs
        if not new_state and (self.last_state or self.last_state is None):
            _run_all(self.on_false_funcs)  # run all on_false funcs
        if new_state:
            _run_all(self.while_true_funcs)
        if not new_state:
            _run_all(self.while_false_funcs)
        self.last_state = new_state

    def on_true(self, func: ty.Callable) -> None:
        """
        Adds func to be called when state changes from false to true.
        This func will not be called again until true is evaluated to
        false and then back again.
        :param func: Callable
        :return: None
        """
        self.on_true_funcs.append(func)

    def on_false(self, func: ty.Callable) -> None:
        """
        Adds func called when state changes from true to false
        :param func: Callable
        :return: None
        """
        self.on_false_funcs.append(func)

    def while_true(self, func: ty.Callable) -> None:
        """
        Adds func called as long as state remains true
        :param func: Callable
        :return: None
        """
        self.while_true_funcs.append(func)

    def while_false(self, func: ty.Callable) -> None:
        """
        Adds func called so long as state remains false
        :param func: Callable
        :return: None
        """
        self.while_false_funcs.append(func)


def _run_all(runnable_collection):
    [func() for func in runnable_collection]


###
# Additional subclasses extending condition can go here
