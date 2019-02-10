# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#          <Submenu name = "Metrics">
#               <Item name="Get All Imaris Statistics" icon="Python" tooltip="Get all Statistics from Imaris for a selectd surface">
#               <Command>PythonXT::XT_GetStats(%i)</Command>
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


# Get All Statistics

def XT_GetStats(aImarisId):

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

    print('Object type Selected : '+object_type)

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    object_name = create_window_from_list(object_list=objects_list, window_title='Select one object')
    print('Object Selected : '+object_name)

    all_stats = get_imaris_statistics(vImaris=vImaris, object_type=object_type, object_name=object_name)

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    output_dir = get_output_dir(initial_dir=imaris_dir)
    output_file = imaris_name+'_'+object_name+'_statistics.txt'
    output_path = output_dir+'/'+output_file
    all_stats.to_csv(output_path, index=False, sep='|')

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
