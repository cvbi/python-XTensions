# Imaris XTensions package

This package is a collection of Imaris related tools at CVBI.

How to use this package :

```
0. Add Python 2.7 to your Imaris environment.
1. Clone this repository to a local folder
2. Clone the cvbi repository within this folder, if you didn't clone the above one recursively
3. Add this repository folder to your Imaris XTensions path
```

Dependency list ( to be kept updated as more XTensions are added) :

    1. Python2.7
    2. Numpy
    3. Scipy
    4. Scikit Learn
    5. Pandas
    6. Scikit Image
    7. tqdm

[Imaris](!http://www.bitplane.com/imaris) provides an inbuilt package `ImarisLib` to use for connecting and working with different structures within Imaris. Currently, Imaris does not support python3 (ugghh.....I know, right?).
 
Please use [anaconda](!https://www.anaconda.com) to create a Python 2.7 environment and use the python executable in this environment folder as python executable for Imaris. As far as I can test, there are no choices specific to python2 in our extensions and when Bitplane starts supporting python3, all XTensions should be transferable with minimal changes. 