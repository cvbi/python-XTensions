# Imaris XTension
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


import os
import time
import ImarisLib
import pandas as pd

from cvbi.gui import *
from cvbi.stats.track import get_track_angles
from cvbi.base_imaris.objects import GetSurpassObjects
from cvbi.base_imaris.stats import get_imaris_statistics

# Get All Statistics

def XT_GetStats(aImarisId):

    print('''
    ####################################################
    ##########     Extension started     ###############
    ####################################################
    ''')
    time.sleep(5)

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)

    object_type_list = ["surfaces", "spots", "cells"]
    object_type = create_window_from_list(object_list=object_type_list,
                                          window_title='Select one object type',
                                          w=500, h=500)

    print('Object type Selected : '+object_type)

    objects = GetSurpassObjects(vImaris=vImaris, search=object_type)
    objects_list = objects.keys()
    objects_selected = create_window_for_multiple_selection(object_list = objects_list,
                                                            window_title = 'Select surfaces get statistics.',
                                                            w = 500, h = 50*len(objects_list))
    print('\nObjects Selected : \n')
    print(objects_selected)
    time.sleep(3)

    output_dir = get_dir( initial_dir = imaris_dir )

    for object_name in objects_selected:

        # Get Imaris Statistics

        data_stats = get_imaris_statistics(vImaris=vImaris, object_type=object_type, object_name=object_name)

        # Get Instantaneous track angles

        data_angles = data_stats.groupby( 'trackID' ).apply( lambda df_in : get_track_angles( df_in , return_ids = True ) )
        data_angles.reset_index( inplace = True )
        data_stats_out = pd.merge( left = data_stats , right = data_angles , on = ['trackID' , 'objectID'] )
        data_stats_out.sort_values(by=['trackID','time'], inplace = True)

        output_file = imaris_name+'_'+object_name+'_statistics.txt'
        output_path = output_dir+'/'+output_file
        data_stats_out.to_csv(output_path, index=False, sep='|')

    print('''
    ###########################################################
    #########            Extension finished.        ###########
    #########  Wait for 5s to close automatically   ###########
    ###########################################################
    ''')
    time.sleep(5)
