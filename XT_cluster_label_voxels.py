# USe a scikit-learn saved model to label voxels that belong to individual clusters as separate channels
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Clustering">
#        <Item name="Label Voxels using density model" icon="Python" tooltip="Use a saved model to label individual voxels">
#         <Command>PythonXT::XT_cluster_label_voxels(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>

import os
import time
import ImarisLib

from cvbi.gui import *

from itertools import product
from tqdm import tqdm
from Tkinter import Tk

import numpy as np
from sklearn.externals import joblib
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import minmax_scale


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

def XT_cluster_label_voxels(aImarisId):

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

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir  = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    print('''
     ####################################################################################
     ###########################     Extension started     ##############################
     ####################################################################################
     ''')
    time.sleep(1)

    # Load model into memory

    print('Select model object ( it ends in .joblib ): ')
    model_file = get_input_file(window_title = 'Select the model file that belongs to this dataset :', initial_dir = imaris_dir, w = 500, h=400)
    clusterer = joblib.load(model_file)
    print(clusterer)
    print('\nModel object loaded into memory.\n')
    time.sleep(1)

    # Create dummy voxel array

    print('\nGetting dataset coordinate system.')
    nX = vDataSet.GetSizeX()
    nY = vDataSet.GetSizeY()
    nZ = vDataSet.GetSizeZ()
    nC = vDataSet.GetSizeC()
    nT = vDataSet.GetSizeT()

    x_min, x_max = vDataSet.GetExtendMinX(), vDataSet.GetExtendMaxX()
    y_min, y_max = vDataSet.GetExtendMinY(), vDataSet.GetExtendMaxY()
    z_min, z_max = vDataSet.GetExtendMinZ(), vDataSet.GetExtendMaxZ()
    time.sleep(2)


    print('\nCreating dummy array for labeling.')

    x = np.arange(nX)
    y = np.arange(nY)
    z = np.arange(nZ)
    X_all = np.array([[xi, yi, zi] for xi, yi, zi in product(x, y, z)])
    X = X_all.copy()

    time.sleep(2)


    # Scaling calculations

    print('\nScaling individual coordinates.')

    Xs_index = X[:, 0]
    Ys_index = X[:, 1]
    Zs_index = X[:, 2]
    time.sleep(2)

    Xs_coords = minmax_scale(Xs_index.astype(np.float64), feature_range = (x_min, x_max))
    Ys_coords = minmax_scale(Ys_index.astype(np.float64), feature_range = (y_min, y_max))
    Zs_coords = minmax_scale(Zs_index.astype(np.float64), feature_range = (z_min, z_max))
    pos_data = np.array([Xs_coords, Ys_coords, Zs_coords]).T
    time.sleep(2)

    # Label each voxel

    print('\nLabeling voxels for the complete dataset.')

    labels = dbscan_predict(clusterer, pos_data)
    unique_labels, unique_label_counts = np.unique(ar = labels, return_counts = True)

    c_copy = create_window_from_list(object_list = np.arange(1, nC+1),
                                     window_title = 'Select channel to copy Voxels from :',
                                     w = 500, h=nC*50)
    c_copy = np.int64(c_copy)
    c_copy_name = vDataSet.GetChannelName(c_copy-1)
    time.sleep(2)

    print('\nVectorized labeling finished.\n')

    for label in unique_labels:
        print('\nCopying data from label : {l}'.format(l=label))

        nC = vDataSet.GetSizeC()
        ch_out = nC + 1
        vDataSet.SetSizeC(ch_out)

        ch_out_name = 'Cluster voxels for label {l} from : {n}'.format(l=label, n=c_copy_name)
        ch_out_description = 'Cluster voxels for label {l} from : {n}'.format(l=label, n=c_copy_name)

        vDataSet.SetChannelName(ch_out-1, ch_out_name)
        vDataSet.SetChannelDescription(ch_out-1, ch_out_description)

        for ti in tqdm(range(nT)):

            data_list = vDataSet.GetDataVolumeFloats(aIndexC = c_copy-1, aIndexT = ti)
            data_array = np.array(data_list)
            data_out = np.zeros_like(data_array)

            for i in range(X.shape[0]):
                xi, yi, zi = X[i]
                if labels[i] == label:
                    data_out[xi, yi, zi] = data_array[xi, yi, zi]

            data_out_list = data_out.tolist()
            vDataSet.SetDataVolumeFloats(aData = data_out_list, aIndexC = ch_out-1, aIndexT = ti)

    print('''
     ####################################################################################
     #########     Extension finished, wait for 5s to close automatically     ###########
     ####################################################################################
     ''')
    time.sleep(5)