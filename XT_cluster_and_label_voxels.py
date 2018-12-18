# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Clustering">
#        <Item name="Cluster and label voxels" icon="Python" tooltip="Cluster voxels and assign labels">
#         <Command>PythonXT::XT_cluster_and_label_voxels(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import BridgeLib


import numpy as np
from cvbi.gui import create_window_from_list

from tqdm import tqdm
from sklearn.cluster import KMeans

# Get Clusters at every time point


def XT_cluster_and_label_voxels(aImarisId):

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
    channel_selected = create_window_from_list(channel_list, window_title='select channel')
    time.sleep(2)

    ch_in = np.int64(channel_selected)
    ch_in_name = vDataSet.GetChannelName(ch_in-1)

    n_clusters = 2

    ch_out = nC+1
    ch_out_name = 'Binary Cluster from channel : '+ch_in_name
    ch_out_description = 'Binary Cluster from channel : '+ch_in_name

    vDataSet.SetSizeC(ch_out)
    vDataSet.SetChannelName(ch_out - 1, ch_out_name)
    vDataSet.SetChannelDescription(ch_out - 1, ch_out_description)

    print('Clustering Based on Channel : '+str(ch_in) + '\n\n')
    time.sleep(5)

    print('Static Clustering Task Status : \n\n')

    for ti in tqdm(range(nT)):

        data_channel_list = vDataSet.GetDataVolumeFloats(aIndexC=ch_in-1, aIndexT=ti)
        data_channel = np.array(data_channel_list)
        data_in = data_channel.astype(np.float64)
        X = data_in.reshape((-1, 1))

        time.sleep(5)

        if ti == 0:
            print(' \n Clustering First time point. \n ')
            time.sleep(2)
            clusterer = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
            labels = clusterer.labels_
        else:
            labels = clusterer.predict(X)

        time.sleep(2)

        segmented = labels.reshape(data_in.shape)
        data_out = 1000*segmented.copy()
        data_out_list = data_out.tolist()
        vDataSet.SetDataVolumeFloats(aData=data_out_list, aIndexC=ch_out-1, aIndexT=ti)


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
