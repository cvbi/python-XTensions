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

import os
import time
import ImarisLib
from tqdm import tqdm


import numpy as np
import pandas as pd
from cvbi.gui import *

# Template Extension description for function


def XTensions_template(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir  = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    print('''
    ##################################################################
    ###################     Extension started     ####################
    ##################################################################
    ''')
    time.sleep(5)

    # Put your code here

    for i in tqdm(range(1000000)):
        pass

    print('''
    ##################################################################
    ###############         Extension finished.              #########
    ###############   Wait for 5s to close automatically     #########
    ##################################################################
    ''')
    time.sleep(5)
