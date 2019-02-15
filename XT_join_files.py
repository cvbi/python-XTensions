# Clustering Voxels Extension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#          <Submenu name = "Data Manipulation">
#               <Item name="Combine 2 datasets" icon="Python" tooltip="Combine two datasets to create a single output">
#                 <Command>PythonXT::XT_join_files(%i)</Command>
#               </Item>
#           </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib
import os

import pandas as pd
from cvbi.gui import *

# Get All Statistics


def XT_join_files(aImarisId):

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


    print('\nSelect first file to combine\n')
    file_01 = get_input_file(window_title='Select File to read : ',
                             initial_dir = imaris_dir,
                             w = 600, h=400)
    sep_01 = '|'

    data_left = pd.read_csv(file_01, sep =sep_01)

    print('\nSelect second file to combine\n')
    file_02 = get_input_file(window_title='Select File to read : ',
                             initial_dir = imaris_dir,
                             w = 600, h=400)
    sep_02 = '|'

    data_right = pd.read_csv(file_02, sep =sep_02)



    # Join Files

    join_formats = ["Rows", "Columns"]
    join_format = create_window_from_list(object_list=join_formats, window_title='How are you going to combine?')

    if join_format == 'Columns':
        join_types = ['left', 'inner']
        join_type = create_window_from_list(object_list=join_types, window_title='How are you going to combine?')

        time.sleep(2)
        data_out = pd.merge(left = data_left,
                            right = data_right,
                            how=join_type,
                            on='trackID',
                            suffixes = ('', '_right'))
    else:
        data_out = pd.concat([data_left, data_right], ignore_index = True)

    try:

        output_dir = get_output_dir(window_title = 'Select folder to save output', initial_dir=imaris_dir)
        output_file = imaris_name+'_combined.txt'
        output_file = create_window_for_input(default=output_file,
                                              w=700, h=200,
                                              window_text='Modify the file name for any changes',
                                              window_title='Provide your output file name')
        output_path = output_dir+'/'+output_file
        data_out.to_csv(output_path, index=False, sep='|')
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
