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


import os
import time
import ImarisLib

from cvbi.gui import *
from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.stats.track import get_motility

import pandas as pd

# Get All Statistics

def XT_get_motility(aImarisId):


    print('''
    ########################################################
    ################     Extension started     #############
    ########################################################
    ''')
    time.sleep(5)

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    print('Choose object type to get statistics')
    object_type_list = ["surfaces", "spots", "cells"]
    object_type = create_window_from_list(object_list=object_type_list,
                                          window_title='Select one object type',
                                          w=500, h=50*len(object_type_list))

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    objects_selected = create_window_for_multiple_selection(object_list = objects_list,
                                                            window_title = 'Select surfaces get motility.',
                                                            w = 500, h = 50*len(objects_list))
    print('\nObjects Selected : \n')
    print(objects_selected)
    time.sleep(3)

    print('\n Object type Selected : '+object_type)

    print('\nChoose output folder to save results\n')
    output_dir = get_dir( initial_dir=imaris_dir )

    for object_name in objects_selected:
        print('\nObject Selected : '+object_name)
        time.sleep(2)

        # Get raw data

        print('\nGetting Cell movement data for : '+object_name)
        time.sleep(2)
        data_stats = get_imaris_statistics(vImaris=vImaris, object_type=object_type, object_name=object_name)

        # Run calculations

        print('\nCalculating Motility coefficients for : '+object_name)
        time.sleep(2)
        data_motility = data_stats.groupby('trackID').apply(lambda df: get_motility(data_cell=df, time_limit=601))
        data_motility.reset_index(drop=False, inplace=True)
        data_motility['File'] = imaris_name
        data_motility_subset = data_motility.copy()
        condition = data_motility_subset.r2.gt(0.8).values
        data_motility_subset = data_motility_subset.loc[condition, :]

        # Save Data

        print('Saving data for {o}'.format(o=object_name))
        output_file = imaris_name+'_'+object_name+'_motility.txt'
        output_file_subset = imaris_name+'_'+object_name+'_motility_subset.txt'

        output_path = output_dir+'/'+output_file
        output_path_subset = output_dir+'/'+output_file_subset

        try:
            data_motility = data_motility.drop(['level_1'], axis=1)
        except:
            pass

        data_motility.to_csv(output_path, index=False, sep='|')
        data_motility_subset.to_csv(output_path_subset, index=False, sep='|')

    print('''
    ##############################################################
    #########             Extension finished.            #########
    #########     Wait for 5s to close automatically     #########
    ##############################################################
    ''')
    time.sleep(5)
