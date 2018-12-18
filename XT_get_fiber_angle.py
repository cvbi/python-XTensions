# Template Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Channel Mods">
#        <Item name="Get Orientation at each voxel" icon="Python" tooltip="Description to be shown in tooltip">
#         <Command>PythonXT::XT_get_fiber_angle(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>

import time
import ImarisLib
from tqdm import tqdm


import numpy as np

from cvbi.gui import *
from cvbi.image.orientation import get_image_angles

# Template Extension description for function
import warnings

def XT_get_fiber_angle(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')

    time.sleep(5)

    nX = vDataSet.GetSizeX()
    nY = vDataSet.GetSizeY()
    nZ = vDataSet.GetSizeZ()
    nT = vDataSet.GetSizeT()
    nC = vDataSet.GetSizeC()

    # Select Channel

    channel_list = range(1, nC+1)
    channel_selected = create_window_from_list(channel_list, window_title='Select Channel')

    ch_in = np.int64(channel_selected)
    ch_in_name = vDataSet.GetChannelName(ch_in-1)
    print('Channel Selected : '+ch_in_name)
    time.sleep(5)

    # Create Output Channel
    ch_out = nC+1
    ch_out_name = 'Orientation calculated from Channel : '+ch_in_name
    vDataSet.SetSizeC(ch_out)
    vDataSet.SetChannelName(ch_out - 1, ch_out_name)
    print('Channel Created : '+ch_out_name)
    time.sleep(5)

    # Ask user if rotation is to be done

    rotate = 0
    rotation_list = ['Yes', 'No']
    answer = create_window_from_list(rotation_list, window_title='Are you calculating angle after rotation?')

    if answer =='yes':
        rotate = 1

    # Get other parameters

    window_size = 13
    window_overlap = 0.24
    print('Starting with default parameters : '
          'Window Size = {window_size}, '
          'Overlap = {window_overlap}'.format(window_size=window_size, window_overlap=window_overlap))
    time.sleep(5)

    warnings.simplefilter("ignore")

    for t in tqdm(np.arange(nT)):
        for z in np.arange(nZ):

            data_in = vDataSet.GetDataSliceFloats(aIndexZ=z, aIndexC=ch_in - 1, aIndexT=t)
            nearest_image = np.array(data_in).copy()
            cutoff = np.percentile(nearest_image, 90)

            # Create cutoff image

            nearest_image_cutoff = nearest_image.copy()
            if rotate:
                nearest_image_cutoff = np.rot90(nearest_image_cutoff)

            nearest_image_cutoff[nearest_image_cutoff <= cutoff] = 0.0
            angle_array, X, Y, U, V = get_image_angles(im=nearest_image_cutoff + 1e-6,
                                                       window_size=window_size,
                                                       window_overlap=window_overlap)
            angle_array = np.rad2deg(angle_array)
            angle_array[np.isnan(angle_array)] = 0
            data_out = angle_array.tolist()
            vDataSet.SetDataSliceFloats(aData=data_out, aIndexZ=z, aIndexC=ch_out - 1, aIndexT=t)
            time.sleep(2)


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
