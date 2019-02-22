# Imaris XTension
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#          <Submenu name = "Data processing">
#               <Item name="Filter dataset based on perimeter and curvature ratio" icon="Python" tooltip="Subset dataset">
#                 <Command>PythonXT::XT_subset_file_emma(%i)</Command>
#               </Item>
#           </Submenu>
#      </Menu>
#    </CustomTools>


import os
import time
import ImarisLib

import pandas as pd
from cvbi.gui import *



def XT_subset_file_emma(aImarisId):

    print('''
    #####################################################
    ###########     Extension started     ###############
    #####################################################
    ''')
    time.sleep(3)

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)

    imaris_file = vImaris.GetCurrentFileName()
    imaris_dir = os.path.dirname(imaris_file)
    imaris_name = os.path.basename(imaris_file)


    input_dir  = get_dir( window_title = 'Select Input Folder ' , initial_dir = imaris_dir )
    output_dir = get_dir( window_title = 'Select Output Folder' , initial_dir = input_dir )

    print('Input  folder : {f}'.format(f=input_dir))
    print('Output folder : {f}'.format(f=output_dir))
    time.sleep(2)

    file_in = get_file( window_title= 'Select File to read :' ,
                        initial_dir = input_dir ,
                        filetypes = (("csv files","*.csv"),
                                     ("txt files","*.txt"),
                                     ("all files","*.*")),
                        w = 600 , h=400 )
    print('Input file : {f}'.format(f=file_in))
    time.sleep(2)
    sep_in = ','

    print('Reading dataset...')
    data_in = pd.read_csv(file_in, sep =sep_in)
    data_out = data_in.copy()
    time.sleep(2)

    # Perimeter filter
    print('Subsetting based on perimeter.')
    time.sleep(2)

    data_out = data_out.groupby( ['trackid'] ).apply( lambda df : df.loc[df.perimeter.le( 1.8 * df.perimeter.min( ) ) , :] ).reset_index( drop = True )
    time.sleep(2)

    # Curvature ratio filter
    print('Subsetting based on curvature.')
    time.sleep(2)
    data_out = data_out.groupby( ['trackid'] ).apply( lambda df : df.loc[df.curvature_ratio.ge( 1.5 ) , :] ).reset_index( drop = True )
    time.sleep(2)


    data_out.sort_values(by=['trackid', 'frame'], inplace = True)

    output_file = "combined_subset_filtered_on_columns"
    output_file = create_window_for_input( default = output_file ,
                                           w = 700 , h = 200 ,
                                           window_text = 'Modify the file name for any changes' ,
                                           window_title = 'Provide your output file name' )

    print('Input dataset had {n1} observations, output dataset has {n2} observations'.format(n1=data_in.shape[0], n2=data_out.shape[0]))
    time.sleep(3)

    try:
        print('Saving complete dataset.')
        time.sleep(1)
        output_path = output_dir+'/'+output_file+'.csv'
        data_save = data_out.copy()
        data_save.to_csv(output_path, index=False, sep=',')

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
    #####################################################
    ######          Extension finished             ######
    ######  Wait for 5s to close automatically     ######
    #####################################################
    ''')
    time.sleep(5)

