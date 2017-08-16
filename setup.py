from distutils.core import setup, Extension
from Cython.Build import cythonize

import numpy

setup(
    name='gokart',
    ext_modules=cythonize(Extension(
        name='kart.kinect.pm.cyfunc',
        sources=['kart/kinect/pm/cyfunc.pyx'],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-ffast-math"]  # rmv if inexplicable errors occur
    )),
    install_requires=[
        'pip>=8.1.1',  # setup of req. in lower versions have led to errors
        'setuptools>=20.7.0',
        'Cython',
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.3'
    ]
)
