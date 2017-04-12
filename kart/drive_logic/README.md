### Drive Logic
Package holding modules for producing target speeds and turn radii 
from input data.

#### Content:
* const.py: Module holding constants used only within this package.
* logic.py: Python Module holding DriveLogic classes which themselves 
    have target_speed and target_turn_radius properties which are
    intended to be accessed from the main kart module and used by
    the Actuator class.
* turn_table.py: Module holding a list of different turn arcs that are
    calculated at start-up, saving time at run-time.
