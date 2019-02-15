# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#          <Submenu name = "Metrics">
#               <Item name="Get Motility for tracks" icon="Python" tooltip="Get motility values and associated data for all tracks">
#                 <Command>PythonXT::XT_get_motility(%i)</Command>
#               </Item>
#           </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import os

from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.gui import create_window_from_list, get_output_dir
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.stats.track import get_motility

# Get All Statistics

def XT_get_motility(aImarisId):


    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    object_type_list = ["spots", "surfaces", "filaments", "cells"]
    object_type = create_window_from_list(object_list=object_type_list, window_title='Select one object type')

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    object_name = create_window_from_list(object_list=objects_list, window_title='Select one object')

    print('\n Object type Selected : '+object_type)
    print('\n Object Selected : '+object_name)
    time.sleep(2)

    print('\n Getting Cell movement data for : '+object_name)
    time.sleep(2)
    try:
        data_stats = get_imaris_statistics(vImaris=vImaris, object_type=object_type, object_name=object_name)
    except:
        print('\n Failure to acquire Imaris statistics \n')
        time.sleep(5)
        return

    print('\n Calculating Motility coefficients for : '+object_name)
    time.sleep(2)
    try:
        data_motility = data_stats.groupby('trackID').apply(lambda df: get_motility(data_cell=df, time_limit=601))
        data_motility.reset_index(drop=False, inplace=True)
    except:
        print('\n Failure to calculate motility values \n')
        time.sleep(5)
        return

    print('\n Calculations finished, choose folder to save data locally \n')
    time.sleep(2)

    try:

        data_motility['File'] = imaris_name
        data_motility_subset = data_motility.copy()
        condition = data_motility_subset.r2.gt(0.8).values
        data_motility_subset = data_motility_subset.loc[condition, :]

        output_dir = get_output_dir(initial_dir=imaris_dir)
        output_file = imaris_name+'_'+object_name+'_motility.txt'
        output_file_subset = imaris_name+'_'+object_name+'_motility_subset.txt'

        output_path = output_dir+'/'+output_file
        output_path_subset = output_dir+'/'+output_file_subset

        data_motility = data_motility.drop(['level_1'], axis=1)
        data_motility.to_csv(output_path, index=False, sep='|')
        data_motility_subset.to_csv(output_path_subset, index=False, sep='|')
    except:
        print('''
        Calculations finished successfully but there was an error in saving your dataset. \n
        Try closing other open Imaris applications and then run this XTension. \n 
        Please do not forget to save your work.\n
        Please contact Nilesh Patil : nilesh.patil@rochester.edu if this problem persists \n
        ''')
        time.sleep(5)
        return

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
