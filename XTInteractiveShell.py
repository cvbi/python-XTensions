#
#
#  Python Interactive Shell XTension
#
#  Copyright (c) 2013 Egor Zindy (egor.zindy@manchester.ac.uk), BSD-style copyright and disclaimer apply
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#      <Submenu name = "Code">
#       <Item name="Interactive Shell" icon="Python" tooltip="Opens an interactive shell.">
#         <Command>PythonXT::XTInteractiveShell(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>

import ImarisLib
import time

import code
#import numpy

import BridgeLib

def XTInteractiveShell(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()

    # Get an imaris object with id aImarisId
    vImaris = vImarisLib.GetApplication(aImarisId)

    # Check if the object is valid
    if vImaris is None:
        print "Could not connect to Imaris!"
        time.sleep(5)
        return

    # Get the dataset
    vDataSet = vImaris.GetDataSet()

    # Check if the object is valid
    if vDataSet is None:
        print "Warning: No dataset!\n"
        time.sleep(5)

    vars = globals().copy()
    vars.update(locals())

    shell = code.InteractiveConsole(vars)
    shell.interact()
