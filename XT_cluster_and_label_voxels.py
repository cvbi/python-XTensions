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


import numpy as np
from cvbi.gui import create_window_from_list, create_window_for_input

from tqdm import tqdm
from sklearn.cluster import KMeans

# Get Clusters at every time point


def XT_cluster_and_label_voxels(aImarisId):

    current_time = time.localtime()
    time_description = 'Created on :{YY}-{MM}-{DD} {hh}-{mm}-{ss}'.format(YY=current_time.tm_year,
                                                                          MM=current_time.tm_mon,
                                                                          DD=current_time.tm_mday,
                                                                          hh=current_time.tm_hour,
                                                                          mm=current_time.tm_min,
                                                                          ss=current_time.tm_sec)

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

    # Select Channel

    channel_list = range(1, nC+1)
    channel_selected = create_window_from_list(channel_list,
                                               w=300,
                                               h=len(channel_list)*50,
                                               window_title='Select Channel')
    ch_in = np.int64(channel_selected)

    # Get Input Channel Metadata

    ch_in_name = vDataSet.GetChannelName(ch_in-1)
    channel_color_table = vDataSet.GetChannelColorTable(ch_in-1)
    channel_color = channel_color_table.mColorRGB
    channel_alpha = channel_color_table.mAlpha
    time.sleep(2)

    # Select Number of clusters

    n_clusters = 2
    n_clusters = create_window_for_input(default=n_clusters,
                                         w=300,
                                         h=500,
                                         window_title='Clusters',
                                         window_text='Provide number of clusters to segment into',
                                         valid_range=[2, 25])
    n_clusters = np.int64(n_clusters)
    time.sleep(2)

    # Select time point to cluster

    t_cluster = 1
    if nT > 1:
        t_cluster = create_window_for_input(default=t_cluster,
                                            w=400,
                                            h=500,
                                            window_title='Time',
                                            window_text='Provide an integer time point for determining voxel clusters.'
                                                    'For others, this intensity distribution is used as reference.',
                                            valid_range=[1, nT])
    t_cluster = np.int64(t_cluster)-1

    print('Clustering Channel : '+str(ch_in_name))
    print('Number of clusters : '+str(n_clusters))
    print('Time               : '+str(t_cluster+1))
    time.sleep(2)

    for cluster_channel in range(n_clusters):

        ch_out = nC+cluster_channel+1
        ch_out_name = 'Cluster voxels for label {l} from : {n}'.format(l=cluster_channel, n=ch_in_name)
        ch_out_description = 'Cluster voxels for label {l} from : {n}'.format(l=cluster_channel, n=ch_in_name)
        ch_out_description += '\n'+time_description

        vDataSet.SetSizeC(ch_out)
        vDataSet.SetChannelName(ch_out-1, ch_out_name)
        vDataSet.SetChannelDescription(ch_out-1, ch_out_description)
        #vDataSet.SetChannelColorTable(aIndexC=ch_out-1, aColorRGB=channel_color, aAlpha=channel_alpha)

        print('Channel :'+str(ch_out)+' added to contain cluster label :'+str(cluster_channel) + '\n')
        time.sleep(2)

    data_channel_list = vDataSet.GetDataVolumeFloats(aIndexC=ch_in - 1, aIndexT=t_cluster)
    print('Clustering data acquired. \n')
    time.sleep(2)
    data_channel = np.array(data_channel_list)
    data_in = data_channel.astype(np.float64)
    X = data_in.reshape((-1, 1))

    print('Clustering Started. \n')
    time.sleep(2)
    clusterer = KMeans(n_clusters=n_clusters, random_state=0)
    clusterer.fit(X)
    print('Clustering Finished. \n')
    time.sleep(2)

    print('Clustering Task Status : \n\n')
    for ti in tqdm(range(nT)):
        data_channel_list = vDataSet.GetDataVolumeFloats(aIndexC=ch_in-1, aIndexT=ti)
        data_channel = np.array(data_channel_list)
        data_in = data_channel.astype(np.float64)
        X = data_in.reshape((-1, 1))
        labels = clusterer.predict(X)
        segmented = labels.reshape(data_in.shape)

        for cluster_channel in range(n_clusters):
            ch_out = nC + cluster_channel + 1
            data_out = (segmented == cluster_channel).astype(np.float64)
            data_out_list = data_out.tolist()
            vDataSet.SetDataVolumeFloats(aData=data_out_list, aIndexC=ch_out-1, aIndexT=ti)

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
