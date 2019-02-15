# Clustering Cells Extension
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Clustering">
#        <Item name="Label Cells using density model" icon="Python" tooltip="Use clustered model to label new cells.">
#         <Command>PythonXT::XT_cluster_label_cells(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import os

from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.gui import *

import numpy as np
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

def XT_cluster_label_cells(aImarisId):

    print('''
     ####################################################################################
     ###########################     Extension started     ##############################
     ####################################################################################
     ''')
    time.sleep(2)

    vImarisLib = ImarisLib.ImarisLib()
    vImaris    = vImarisLib.GetApplication(aImarisId)
    vDataSet   = vImaris.GetDataSet()

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir  = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)
    input_model = get_input_file(window_title='Select model file to load :', initial_dir=imaris_dir, w=500, h=200)
    output_dir  = get_output_dir(window_title='Select folder to save output file :', initial_dir=imaris_dir, w=500, h=200)

    # Load model

    clusterer = joblib.load(filename=input_model)
    print('Model successfully loaded.')
    time.sleep(2)

    # Select Object Type

    object_type_list = ["surfaces", "cells", "spots"]
    object_type = create_window_from_list(object_list = object_type_list,
                                          w = 300, h = 50*len(object_type_list),
                                          window_title = 'Select one object')
    print('\nObject type Selected : ' + object_type)
    time.sleep(1)

    # Select Object

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    objects_selected = create_window_for_multiple_selection(object_list = objects_list,
                                                            window_title = 'Select surfaces get cluster labels.',
                                                            w = 500, h = 50*len(objects_list))
    print('\nObjects Selected : \n')
    print(objects_selected)
    time.sleep(1)

    for object_name in objects_selected:

        # Path for output
        output_file = imaris_name + '_' + object_name + '_transferred_labels.txt'
        output_path_stats = output_dir + '/' + output_file
        time.sleep(1)

        # Get statistics for selected surface

        print('\nAcquiring Statistics from Imaris for {o}'.format(o=object_name))
        time.sleep(2)
        all_stats = get_imaris_statistics(vImaris=vImaris,
                                          object_type=object_type,
                                          object_name=object_name)
        print('\nStatistics for {o} Acquired.'.format(o=object_name))
        time.sleep(2)

        # Predict for all time points

        data_tn = all_stats.copy()
        data_in = data_tn.loc[:, ['Position X', 'Position Y', 'Position Z']].copy()
        X = data_in.values
        labels = dbscan_predict(model=clusterer, X=X)
        all_stats.loc[:, 'cluster_label'] = labels

        print('\nLabelling complete for {o}\n'.format(o=object_name))
        time.sleep(2)

        all_stats.to_csv(path_or_buf=output_path_stats, index=False, sep='|')

    print('''
     ####################################################################################
     #########     Extension finished, wait for 5s to close automatically     ###########
     ####################################################################################
     ''')
    time.sleep(5)