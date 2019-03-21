Index 
---
- [Setup](#setup)
- [List of XTensions](#list-of-extensions)


#### Setup

How to use this package :

```
0. Add Python 2.7 to your Imaris environment.

1. Clone this repository to a local folder : 

    git clone --recurse-submodules https://github.com/cvbi/python-XTensions.git

2. Clone the cvbi repository within this folder, if you didn't clone the above one recursively

3. Add this repository folder to your Imaris XTensions path

```

Dependency list ( to be kept updated as more XTensions are added) :

    1. Python2.7
    2. Numpy
    3. Scipy
    4. Pandas
    5. Scikit Learn
    6. Scikit Image
    7. tqdm

[Imaris](!http://www.bitplane.com/imaris) provides an inbuilt package `ImarisLib` to use for connecting and working with different structures within Imaris. Currently, Imaris does not support Python 3 (ugghh.....I know, right?).
 
Please use [Anaconda](!https://www.anaconda.com) to create a Python 2.7 environment and use the python executable in this environment folder as python executable for Imaris. As far as I can test, there are no choices specific to python2 in our extensions and when Bitplane starts supporting python3, all XTensions should be transferable with minimal changes.

#### List of Extensions

01. [XT_duplicate_channel](_posts/2019-03-21-xt-duplicate-channel.md)