# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#          <Submenu name = "Metrics">
#               <Item name="Run movement w.r.t cluster analysis" icon="Python" tooltip="Get Movement Metrics">
#               <Command>PythonXT::XT_run_comparative_movement_analysis(%i)</Command>
#               </Item>
#           </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import os

from cvbi.gui import *
from cvbi.stats.movement import *
from cvbi.base_imaris.objects import GetSurpassObjects

import pandas as pd


# Get All Statistics

def XT_run_comparative_movement_analysis(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

    object_type_list = ["spots", "surfaces", "filaments", "cells"]
    object_type = create_window_from_list(object_list=object_type_list,
                                          window_title='Select one object type',
                                          w = 500, h = 50*len(object_type_list))
    print('\nObject type Selected : '+object_type)
    time.sleep(2)

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()

    object_cluster = create_window_from_list(object_list=objects_list,
                                             window_title='Select surface used for clustering :',
                                             w = 500, h = 50*len(objects_list))
    print('\nClustering surface : '+object_cluster)
    time.sleep(2)

    objects_moving = create_window_for_multiple_selection(object_list = objects_list,
                                                          window_title = 'Select surfaces to compare :',
                                                          w = 500, h = 50*len(objects_list))
    print('\nComparison surfaces :\n')
    print(objects_moving)
    time.sleep(2)

    output_dir = get_output_dir(window_title = 'Select folder to save output :',
                                initial_dir=imaris_dir,
                                w = 500, h = 400)
    print('\nOutput directory selected : '+output_dir)
    time.sleep(2)

    time_limits = [30, 60, 120]
    path_out_percentage = output_dir+'/'+'aggregate_row.xlsx'

    data_moving, cell_moving, path_data_moving, path_data_motility = None, None, None, None

    for cell_moving in objects_moving:

        print('Reading data for {f}'.format(f = cell_moving))

        path_data_moving = output_dir+'/'+imaris_name + '_' + cell_moving + '_transferred_labels.txt'
        path_data_motility = output_dir+'/'+imaris_name + '_' + cell_moving + '_motility_subset.txt'

        time.sleep(2)

        if os.path.exists(path_data_moving):
            data_moving = pd.read_csv(path_data_moving, sep = '|')
            print('Data for labels read correctly.')
            time.sleep(2)
        else:
            print('''
            Data file doesn't exist. 
            Please check the path shown below to confirm that you have completed the previous steps.
            
            {f}
            
            '''.format(f=path_data_moving))
            time.sleep(10)

        if os.path.exists(path_data_motility):
            data_motility = pd.read_csv(path_data_motility, sep = '|')
            print('Data for motility read correctly.')
            time.sleep(2)
        else:
            print('''
            Data file doesn't exist. 
            Please check the path shown below to confirm that you have completed the previous steps.
    
            {f}
    
            '''.format(f = path_data_motility))
            time.sleep(10)

        for t_limit in time_limits:

            print('Cell Type : ' + cell_moving + '       ' + 'Time Block : ' + str(t_limit))

            path_out_cell = output_dir + '/' + cell_moving + '_stats_cell_' + str(t_limit) + '_Mins.xlsx'
            path_out_track = output_dir + '/' + cell_moving + '_stats_track_' + str(t_limit) + '_Mins.xlsx'
            time.sleep(2)

            data_moving_subset = data_moving.loc[data_moving.Time.lt(t_limit * 60).values, :].copy()
            print('Subseting finished.')
            time.sleep(2)

            # Calculate All metrics

            print('\nRunning Cell level metric calculation')
            time.sleep(2)
            data_out_cell = data_moving_subset.groupby('trackID').apply(lambda df: get_metrics_cell(data_cell = df)).reset_index(drop = True)

            print('\nRunning Track level metric calculation')
            time.sleep(2)
            data_out_track = data_out_cell.groupby('trackID').apply(lambda df: get_metrics_track(df = df)).reset_index(drop = False)

            print('\nRunning dataset level metric calculation')
            time.sleep(2)
            data_out_dict = get_metrics_dataset(df = data_out_track, cell_moving = cell_moving, t_limit = t_limit)

            print('\nCalculations finished.')
            time.sleep(2)

            try:
                data_out_row = data_out_row.append(other = pd.DataFrame(data_out_dict).T, ignore_index = True)
            except:
                data_out_row = pd.DataFrame(data_out_dict).T

            data_out_cell.to_excel(path_out_cell, index = False)
            data_out_track.to_excel(path_out_track, index = False)

            # Combine with motility
            path_out = output_dir+'/' + cell_moving + '_motility_subset_cluster_information_' + str(t_limit) + '_Mins.xlsx'
            selected_columns = ['trackID', 'track_always_in', 'track_always_out', 'start', 'end']
            data_out = pd.merge(left = data_motility,
                                right = data_out_track.loc[:, selected_columns],
                                how = 'left',
                                on = 'trackID',
                                suffixes = ('', '_from_clustering'))
            data_out.to_excel(path_out, index = False)

    data_out_row.to_excel(path_out_percentage, index = False)



    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
