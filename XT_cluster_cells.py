# Clustering Voxels Extension
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

from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.gui import *

import numpy as np
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

    # Select Object Type

    object_type_list = ["surfaces", "cells", "spots"]
    object_type = create_window_from_list(object_list=object_type_list,
                                          w=300,
                                          h=len(object_type_list)*40,
                                          window_title='Select one object')
    print('\n Object type Selected : ' + object_type)
    time.sleep(1)

    # Select Object

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    object_name = create_window_from_list(object_list=objects_list,
                                          w=300,
                                          h=len(objects_list)*40,
                                          window_title='Select one object')
    print('\n Object Selected : ' + object_name)
    time.sleep(1)

    # Get statistics for selected surface

    all_stats = get_imaris_statistics(vImaris=vImaris,
                                      object_type=object_type,
                                      object_name=object_name)
    print('\n Statistics Acquired.')
    time.sleep(2)

    # Select time point to cluster

    t_cluster = 1
    if nT > 1:
        t_cluster = create_input_window(default=t_cluster,
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
    radius = create_input_window(default=radius,
                                 w=400, h=500,
                                 valid_range=(0, nX),
                                 window_title='Provide a radius',
                                 window_text=window_text)
    r = np.int64(radius)

    window_text = 'Minimum number of cells in radius={rad},' \
                  'required to label the region as part of the nearest cluster.'.format(rad=r)
    density = create_input_window(default=density,
                                  w=400, h=500,
                                  valid_range=(1, 1000),
                                  window_title='Provide minimum density',
                                  window_text=window_text)
    n = np.int64(density)

    print('\n Clustering cells using the following parameters :\n'
          'T       = {t}\n'
          'radius  = {rad}, \n'
          'density = {den}'.format(t=t_cluster+1, rad=r, den=n))
    time.sleep(2)

    # Cluster Cells

    data_tn = all_stats.copy()
    data_in = data_tn.loc[data_tn.time == t_cluster, ['Position X', 'Position Y', 'Position Z']].copy()
    X = data_in.values
    db = DBSCAN(eps=r, min_samples=n)
    db.fit(X)

    print('\n Clustering Complete. Labelling time points started. \n')
    time.sleep(2)

    # Predict for all time points

    data_in = data_tn.loc[:, ['Position X', 'Position Y', 'Position Z']].copy()
    X = data_in.values
    labels = dbscan_predict(model=db, X=X)
    all_stats.loc[:, 'cluster_label'] = labels

    print('\n Prediction complete.\n')
    time.sleep(2)

    output_dir = get_output_dir(w=300, h=200)
    print('Selected Directory path : {dir}'.format(dir=output_dir))
    time.sleep(2)

    imaris_file = vImaris.GetCurrentFileName()
    imaris_name = imaris_file.split('\\')[-1].split('.')[0]
    output_file = str(imaris_name) + '_' + object_name + '_clustered.txt'
    print('\n Current name : \n {}'.format(output_file))
    time.sleep(2)
    output_file = create_input_window(default=output_file,
                                      w=300, h=100,
                                      window_text='Modify the file name for any changes',
                                      window_title='Provide your output file name')

    output_path = output_dir + '\\' + output_file
    print('\n You have chosen to save your file here : \n {}'.format(output_path))
    time.sleep(2)
    all_stats.to_csv(output_path, index=False, sep='|')

    print('''
     ####################################################################################
     #########     Extension finished, wait for 5s to close automatically     ###########
     ####################################################################################
     ''')
    time.sleep(5)