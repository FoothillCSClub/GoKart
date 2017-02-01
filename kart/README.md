# Source Documentation

## Subfolders:

* drive_data/: Package holding DriveData class and related classes.
    DriveData is updated with information by

* drive_logic/: Python Package storing DriveLogic and related
    classes. DriveLogic contains the methods that produce the target
    speeds and turn rates that are passed to MotionController.

* input/: Python package that holds classes for retrieving information
    about vehicle position and detected objects, which is to be stored
    in DriveData.

* motion_controller/: Python package that contains MotionController
    class and related.

* util/: Python package holding utility classes. These classes are
    those that are passed around between other packages, such as 
    Point, etc

* kart.py: Python module holding main GoKart class and main method.
    This class holds references to data, logic, input, and control
    classes and calls them as appropriate.