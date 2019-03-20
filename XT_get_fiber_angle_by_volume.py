# Template Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Channel Mods">
#        <Item name="Get Orientation at each voxel for stack" icon="Python" tooltip="Description to be shown in tooltip">
#         <Command>PythonXT::XT_get_fiber_angle(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>

import time
# Template Extension description for function
import warnings

import numpy as np
from tqdm import tqdm

import ImarisLib
from cvbi.gui import *
from cvbi.image.orientation import get_image_angles


def XT_get_fiber_angle(aImarisId):
    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')

    time.sleep(2)

    nX = vDataSet.GetSizeX()
    nY = vDataSet.GetSizeY()
    nZ = vDataSet.GetSizeZ()
    nT = vDataSet.GetSizeT()
    nC = vDataSet.GetSizeC()

    # Select Channel

    channel_list = range(1 , nC + 1)
    channel_selected = create_window_from_list(channel_list , window_title = 'Select Channel')

    ch_in = np.int64(channel_selected)
    ch_in_name = vDataSet.GetChannelName(ch_in - 1)
    print('Channel Selected : ' + ch_in_name)
    time.sleep(2)

    # Create Output Channel
    ch_out = nC + 1
    ch_out_name = 'Orientation calculated from Channel : ' + ch_in_name
    vDataSet.SetSizeC(ch_out)
    vDataSet.SetChannelName(ch_out - 1 , ch_out_name)
    print('Channel Created : ' + ch_out_name)
    time.sleep(3)

    # Get other parameters

    window_size = 13
    window_overlap = 0.24
    print('Starting with default parameters : '
          'Window Size = {window_size}, '
          'Overlap = {window_overlap}'.format(window_size = window_size , window_overlap = window_overlap))
    time.sleep(2)

    warnings.simplefilter("ignore")

    for t in tqdm(np.arange(nT)):

        data_in_volume = vDataSet.GetDataVolumeFloats(aIndexC = ch_in - 1 , aIndexT = t)
        data_in_volume = np.array(data_in_volume)
        data_out_volume = np.zeros_like(data_in_volume)

        for z in np.arange(nZ):
            data_in = data_in_volume[... , z]
            nearest_image = np.array(data_in).copy()
            cutoff_single = np.percentile(nearest_image , 90)

            ## Create cutoff image

            nearest_image_cutoff = nearest_image.copy()
            nearest_image_cutoff[nearest_image_cutoff <= cutoff_single] = 0.0
            angle_array , X , Y , U , V = get_image_angles(im = nearest_image_cutoff + 1e-6 ,
                                                           window_size = window_size ,
                                                           window_overlap = window_overlap)
            angle_array = np.rad2deg(angle_array)
            angle_array[np.isnan(angle_array)] = 0
            data_out = angle_array.copy()

            data_out_volume[... , z] = data_out.copy()

        data_out_volume = data_out_volume.tolist()
        vDataSet.SetDataVolumeFloats(aData = data_out_volume , aIndexC = channel_add - 1 , aIndexT = t)
        time.sleep(1)

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
