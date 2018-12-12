# Template Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Submenu">
#        <Item name="Name in menu" icon="Python" tooltip="Description to be shown in tooltip">
#         <Command>PythonXT::XTensions_template(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>

import time
import ImarisLib
import BridgeLib
from tqdm import tqdm


import numpy as np
from cvbi.gui import *

# Template Extension description for function


def XTensions_template(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

    # Put your code here

    for i in tqdm(range(1000000)):
        pass


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
