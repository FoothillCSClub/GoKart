# Go-Kart AI
###### AI for self-driving go-kart.
The goal of this project is to create a program which can navigate in a
meaningful way while avoiding obstacles in its path.

__[Google Drive (UPDATED) ](https://drive.google.com/open?id=0B0jf70Ozjo61Y29xN1paZFhmM1k)__

__[Design doc (Old)](https://docs.google.com/document/d/1E0Wp-5Nq-G63zqMJN1eicz02d2_IHPn2qQ_b_EkzGG0/edit?usp=sharing)__


## Dependencies:

* numpy
* Cython
* freenect
* vispy (for visualization of data)
* PyQt5 (for visualization: used by VisPy)

## Folders & Packages

* kart/: Package holding source code for project (analogous to 'src' 
    folder in Java or C)
    
* test/: Package containing test classes and methods for testing
    classes/methods in the kart package.

* lib/: Directory containing compiled C for use by project.
