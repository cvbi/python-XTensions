# Clustering Cells Extension
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Clustering">
#        <Item name="Cluster Cells based on density" icon="Python" tooltip="Cluster Cells and assign labels to each cell at each time point">
#         <Command>PythonXT::XT_cluster_cells(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import os

from cvbi.stats.track import get_track_angles
from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.gui import *

import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.cluster import DBSCAN


def dbscan_predict(model, X):
    """
    Predict using dbscan

    :param model: trained dbscan object model from scikit learn
    :param X: New dataset to predict for, the shape should be the same as training data
    :return: numpy vector of predicted class
    """
    nr_samples = X.shape[0]

    y_new = np.ones(shape=nr_samples, dtype=int) * -1

    for i in range(nr_samples):
        diff = model.components_ - X[i, :]  # NumPy broadcasting

        dist = np.linalg.norm(diff, axis=1)  # Euclidean distance

        shortest_dist_idx = np.argmin(dist)

        if dist[shortest_dist_idx] < model.eps:
            y_new[i] = model.labels_[model.core_sample_indices_[shortest_dist_idx]]

    return(y_new)

def XT_cluster_cells(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################
    ##########     Extension started     ###############
    ####################################################
     ''')
    time.sleep(2)

    nX = vDataSet.GetSizeX()
    nY = vDataSet.GetSizeY()
    nZ = vDataSet.GetSizeZ()
    nT = vDataSet.GetSizeT()
    nC = vDataSet.GetSizeC()

    # Select Object Type

    object_type_list = ["surfaces", "cells", "spots"]
    object_type = create_window_from_list(object_list=object_type_list,
                                          w=500, h=len(object_type_list)*50,
                                          window_title='Select one object')
    print('\nObject type Selected : ' + object_type)
    time.sleep(1)

    # Select Object

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    object_name = create_window_from_list(object_list=objects_list,
                                          w=500, h=len(objects_list)*50,
                                          window_title='Select one object')
    print('\nObject Selected : ' + object_name)
    time.sleep(1)

    # Get statistics for selected surface

    print('\nAcquiring Statistics from Imaris for {object}'.format(object=object_name))
    time.sleep(2)
    data_stats = get_imaris_statistics(vImaris=vImaris,
                                      object_type=object_type,
                                      object_name=object_name)

    # Get Instantaneous track angles

    data_angles = data_stats.groupby( 'trackID' ).apply( lambda df_in : get_track_angles( df_in , return_ids = True ) )
    data_angles.reset_index( inplace = True )
    data_stats_out = pd.merge( left = data_stats , right = data_angles , on = ['trackID' , 'objectID'] )
    data_stats_out.sort_values( by = ['trackID' , 'time'] , inplace = True )
    all_stats = data_stats_out.copy()

    print('\nStatistics Acquired.')
    time.sleep(2)

    # Select time point to cluster

    t_cluster = 1
    if nT > 1:
        t_cluster = create_window_for_input(default=t_cluster,
                                            w=400, h=500,
                                            window_title='Time',
                                            window_text='Provide an integer time point for determining voxel clusters.'
                                                    'For others, this intensity distribution is used as reference.',
                                            valid_range=[1, nT])
    t_cluster = np.int64(t_cluster)
    time.sleep(2)

    # Definer parameters

    radius = 50
    density = 10

    window_text = 'Radius is used to define a sphere around every cell. ' \
                  'This value is used to get localized cell density.'
    radius = create_window_for_input(default=radius,
                                     w=400, h=500,
                                     valid_range=(0, nX),
                                     window_title='Provide a radius',
                                     window_text=window_text)
    r = np.int64(radius)

    window_text = 'Minimum number of cells in radius={rad},' \
                  'required to label the region as part of the nearest cluster.'.format(rad=r)
    density = create_window_for_input(default=density,
                                      w=400, h=500,
                                      valid_range=(1, 1000),
                                      window_title='Provide minimum density',
                                      window_text=window_text)
    n = np.int64(density)

    print('\nClustering cells using the following parameters :\n\n'
          'T       = {t}\n'
          'radius  = {rad}, \n'
          'density = {den} \n'.format(t=t_cluster, rad=r, den=n))
    time.sleep(2)

    # Cluster Cells

    data_tn = all_stats.copy()
    data_in = data_tn.loc[data_tn.time == t_cluster, ['Position X', 'Position Y', 'Position Z']].copy()
    X = data_in.values
    clusterer = DBSCAN(eps=r, min_samples=n)
    clusterer.fit(X)

    print('\nClustering Complete. Labelling time points started. \n')
    time.sleep(2)

    # Predict for all time points

    data_in = data_tn.loc[:, ['Position X', 'Position Y', 'Position Z']].copy()
    X = data_in.values
    labels = dbscan_predict(model=clusterer, X=X)
    all_stats.loc[:, 'cluster_label'] = labels

    print('\nPrediction complete.\n')
    time.sleep(2)

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)
    output_dir = get_output_dir(window_title = 'Select directory to save output',
                                initial_dir=imaris_dir,
                                w=500, h=300)

    print('\nSelected Directory path : {dir}'.format(dir=output_dir))
    time.sleep(2)

    output_model = imaris_name + '_' + object_name + '_model.joblib'
    output_file = imaris_name + '_' + object_name + '_clustered.txt'
    print('\nCurrent name : \n {}'.format(output_file))
    time.sleep(2)

    output_file = create_window_for_input(default=output_file,
                                          w=700, h=300,
                                          window_text='Modify the file name for any changes',
                                          window_title='Provide your output file name')

    output_path_model = output_dir + '/' + output_model
    output_path_stats = output_dir + '/' + output_file
    print('\nYou have chosen to save your files here : \n {m} \n {f}'.format(m=output_path_model, f=output_path_stats))
    time.sleep(2)

    try:
        joblib.dump(value=clusterer, filename=output_path_model)
        all_stats.to_csv(path_or_buf=output_path_stats, index=False, sep='|')
    except:
        print('Model object could not be saved. This usually happens when the OS does not support this operation.')
        print('We will save a statistics file with cluster label as the last column now.')
        time.sleep(3)

    print('''
    ###########################################################
    #########            Extension finished.        ###########
    #########  Wait for 5s to close automatically   ###########
    ###########################################################
     ''')
    time.sleep(5)