# Subtracting Channels
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Channel Mods">
#        <Item name="Combine Channels" icon="Python" tooltip="Combine channels by a mathematical operation">
#         <Command>PythonXT::XT_combine_channel(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib


import numpy as np
from cvbi.gui import *

from tqdm import tqdm

# Get Clusters at every time point


def XT_combine_channel(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(2)

    nC = vDataSet.GetSizeC()
    nT = vDataSet.GetSizeT()

    channel_list = range(1, nC+1)

    channel_selected_01 = create_window_from_list(object_list=channel_list,
                                                  w=400, h=len(channel_list)*45,
                                                  window_title='Select channel A')
    ch_in_01 = np.int64(channel_selected_01)
    ch_in_01_name = vDataSet.GetChannelName(ch_in_01-1)
    print('Input acquired for channel : '+str(ch_in_01_name))
    time.sleep(2)

    channel_selected_02 = create_window_from_list(object_list=channel_list,
                                                  w=400, h=len(channel_list)*45,
                                                  window_title='Select channel B')
    ch_in_02 = np.int64(channel_selected_02)
    ch_in_02_name = vDataSet.GetChannelName(ch_in_02-1)
    print('Input acquired for channel : '+str(ch_in_02_name))
    time.sleep(2)

    operation_list = ['add', 'subtract', 'multiply']
    operation_selected = create_window_from_list(object_list=operation_list,
                                                 w=400, h=len(operation_list)*45,
                                                 window_title='Select Operation')
    print('Selected operation : '+operation_selected)
    time.sleep(2)

    ch_out = nC+1
    ch_out_name = 'Channel '+str(ch_in_01) + '-' + ' Channel '+str(ch_in_02)
    vDataSet.SetSizeC(ch_out)
    vDataSet.SetChannelName(ch_out - 1, ch_out_name)
    print('Selected Channels are : '+str(ch_in_01_name)+' and '+str(ch_in_02_name))
    time.sleep(5)

    print('\n\n Calculating difference between channels : \n\n')

    for ti in tqdm(range(nT)):

        data_channel_list_01 = vDataSet.GetDataVolumeFloats(aIndexC=ch_in_01-1, aIndexT=ti)
        data_channel_01 = np.array(data_channel_list_01)

        data_channel_list_02 = vDataSet.GetDataVolumeFloats(aIndexC=ch_in_02-1, aIndexT=ti)
        data_channel_02 = np.array(data_channel_list_02)

        if operation_selected == 'add':
            data_out = data_channel_01 + data_channel_02
        if operation_selected == 'subtract':
            data_out = data_channel_01 - data_channel_02
        if operation_selected == 'multiply':
            data_out = data_channel_01 * data_channel_02

        data_out_list = data_out.tolist()
        vDataSet.SetDataVolumeFloats(aData=data_out_list, aIndexC=ch_out-1, aIndexT=ti)
        time.sleep(3)


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
