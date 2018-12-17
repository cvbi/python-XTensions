# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Clustering">
#        <Item name="Cluster and Copy voxels" icon="Python" tooltip="Cluster voxels and assign labels">
#         <Command>PythonXT::XT_cluster_and_copy_voxels(%i)</Command>
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


def XT_cluster_and_copy_voxels(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

    nC = vDataSet.GetSizeC()
    nT = vDataSet.GetSizeT()

    channel_list = range(1, nC+1)
    channel_selected = create_window_from_list(channel_list,window_title='Select Channel')
    time.sleep(5)

    ch_in = np.int64(channel_selected)
    ch_in_name = vDataSet.GetChannelName(ch_in-1)

    cluster_list = range(1, 11)
    n_clusters = create_window_from_list(cluster_list, window_title='Select Clusters')
    n_clusters = np.int64(n_clusters)

    print('Clustering Based on Channel : ' + str(ch_in) + '\n\n')

    for cluster_channel in range(n_clusters):

        ch_out = nC+cluster_channel+1
        ch_out_name = 'Cluster '+str(cluster_channel)+' from channel : '+ch_in_name
        ch_out_description = 'Cluster '+str(cluster_channel)+' from channel : '+ch_in_name

        vDataSet.SetSizeC(ch_out)
        vDataSet.SetChannelName(ch_out-1, ch_out_name)
        vDataSet.SetChannelDescription(ch_out-1, ch_out_description)

        print('Channel :'+str(ch_out)+' added to contain cluster label :'+str(cluster_channel) + '\n')
        print('5s Cool Down.\n\n')
        time.sleep(5)

    print('Dynamic Clustering Task Status : \n\n')

    for ti in tqdm(range(nT)):

        data_channel_list = vDataSet.GetDataVolumeFloats(aIndexC=ch_in-1, aIndexT=ti)
        data_channel = np.array(data_channel_list)
        data_in = data_channel.astype(np.float64)
        X = data_in.reshape((-1, 1))

        time.sleep(5)

        if ti == 0:
            clusterer = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
            labels = clusterer.labels_
        else:
            labels = clusterer.predict(X)

        segmented = labels.reshape(data_in.shape)

        for cluster_channel in range(n_clusters):

            ch_out = nC + cluster_channel + 1
            data_out = data_in.copy()
            data_out[segmented != cluster_channel] = 0
            data_out_list = data_out.tolist()
            vDataSet.SetDataVolumeFloats(aData=data_out_list, aIndexC=ch_out-1, aIndexT=ti)


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
