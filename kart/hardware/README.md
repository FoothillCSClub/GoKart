## Hardware

Python Package holding classes & functions for utilizing 
hardware components

At current time, this package contains python only, and wrapped C or
other code is stored separately.

* libpca9685: Module for making use of pca9685 chip.
    Contains Python class which wraps C code.
    Controls pulse width, frequency, and duty cycle for
    each channel.
    
* quadrature_encoder.py: Module holding classes/methods for getting
    information from the quadrature encoder, used to determine
    steering wheels position.
