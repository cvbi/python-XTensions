# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Item name="Get All Statistics" icon="Python" tooltip="Get all Statistics from Imaris for a selectd cell surface">
#         <Command>PythonXT::XT_GetStats(%i)</Command>
#       </Item>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import BridgeLib


from cvbi.gui import create_window_from_list,get_output_dir
from cvbi.statistics import get_imaris_statistics


# Get All Statistics



def XT_GetStats(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(5)

    choose_object_type_from = ["spots", "surfaces", "filaments", "cells"]
    object_type = create_window_from_list(choose_object_type_from)

    imaris_objects = BridgeLib.GetSurpassObjects(vImaris, object_type)
    choose_object_from = imaris_objects.keys()
    object_name = create_window_from_list(choose_object_from)
    all_stats = get_imaris_statistics(imaris_objects, object_name)

    output_dir = get_output_dir()
    output_file = object_name+'.txt'
    output_path =output_dir+'/'+output_file
    all_stats.to_csv(output_path, index=False, sep='|')

    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)
