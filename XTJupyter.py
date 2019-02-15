#  Launch Jupyter for Imaris
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#      <Submenu name = "Code">
#       <Item name="Jupyter-notebook-testing" icon="Python" tooltip="Run iPython">
#         <Command>PythonXT::Run(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>
#
#
# Distributed under the terms of the BSD License. This software was derived
# from components of IPython; the full license is in
# the file COPYING, distributed as part of that software.
#

"""
Launch Jupyter Notebook
"""

from __future__ import print_function
import os
import sys
import time
from ImarisLib import ImarisLib


def Run(aImarisId):

    vImarisLib = ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)

    # Check if the object is valid
    if vImaris is None:
        print("Could not connect to Imaris!")
        exit(1)

    global ImarisId
    ImarisId = aImarisId

    os.environ["IMARISID"] = str(aImarisId)
    path_old = os.environ["PYTHONPATH"].replace('/', '\\').rstrip()
    os.environ["PYTHONPATH"] = os.getcwd()+os.path.pathsep+path_old
    sys.argv = [sys.argv[0]]

    print(os.environ["PYTHONPATH"])
    time.sleep(5)

    os.system('jupyter notebook --notebook-dir=~')
