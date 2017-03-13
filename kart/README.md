# Source Documentation

This is the package that by convention stores source code for the 
python-based project, analogous to the 'src' directory for C or 
Java projects. 
Source code for C and other languages is also stored
herein in their own packages.

## Subfolders:

* kinect/: Sub-project; contains classes for getting 
    information from and manipulating Kinect sensor.

* hardware/: Contains classes for making use of hardware.

* drive_data/: Package holding DriveData class and related classes.
    DriveData is updated with information by Input class at runtime

* drive_logic/: Python Package storing DriveLogic and related
    classes. DriveLogic contains the methods that produce the target
    speeds and turn rates that are passed to MotionController.

* input/: Python package that holds classes for retrieving information
    about vehicle position and detected objects, which is to be stored
    in DriveData.

* motion_controller/: Python package that contains MotionController
    class and related.
    
* const/: Python package storing constants for use throughout 
    the program. Constants which will need to be used across 
    packages should be placed inside one of the modules 
    contained herein.

* util/: Python package holding utility classes. These classes are
    those that are passed around between other packages
    
* const/: Package holding constants used throughout the program.

* kart.py: Python module holding main GoKart class and main method.
    This class holds references to data, logic, input, and control
    classes and calls them as appropriate.
