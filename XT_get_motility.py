# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Item name="Get Motility for tracks" icon="Python" tooltip="Get motility values and associated data for all tracks">
#         <Command>PythonXT::XT_get_motility(%i)</Command>
#       </Item>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib

from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.gui import create_window_from_list, get_output_dir
from cvbi.base_imaris.stats import get_imaris_statistics
from cvbi.stats.track import get_motility

# Get All Statistics

def XT_get_motility(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

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
        data_motility = data_stats.groupby('trackID').apply(lambda df: get_motility(data_cell=df, time_limit=600))
        data_motility.reset_index(drop=True, inplace=True)
    except:
        print('\n Failure to calculate motility values \n')
        time.sleep(5)
        return

    print('\n Calculations finished, choose folder to save data locally \n')
    time.sleep(2)

    try:
        imaris_file = vImaris.GetCurrentFileName()
        imaris_name = imaris_file.split('\\')[-1].split('.')[0]
        data_motility['File'] = imaris_name
        output_dir = get_output_dir()
        output_file = imaris_name+'_'+object_name+'_motility.txt'
        output_path = output_dir+'/'+output_file
        data_motility.to_csv(output_path, index=False, sep='|')
    except:
        print('''
        Calculations finished successfully but there was an error in saving your dataset. \n
        Try closing other open Imaris applications and then run this XTension. \n 
        Please do not forget to save your work.\n
        Please contact Nilesh Patil : nilesh.patil@rochester.edu if this problem persists \n
        ''')
        return

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
