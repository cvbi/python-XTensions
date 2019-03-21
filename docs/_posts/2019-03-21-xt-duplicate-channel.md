---
layout: default
title:  "XT_duplicate_channel"
date:   2019-03-21 00:00:00
categories: XTensions
---

## Name : XT_duplicate_channel

---

01. [Description](#description)
02. [Usage](#usage)
03. [Code](#code)

---

### Description

This XTension creates a duplicate copy of the original cahnnel and adds a new channel with this copy.

---

### Usage

Trial

---

### Code

{% highlight python %}

# Subtracting Channels
#
#  Copyright (C) 2018 Nilesh Patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Channel Mods">
#        <Item name="Duplicate Channel" icon="Python" tooltip="Copy one channel and append to the list">
#         <Command>PythonXT::XT_duplicate_channel(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib


import numpy as np
from cvbi.gui import create_window_from_list

from tqdm import tqdm
from sklearn.cluster import KMeans

# Get Clusters at every time point


def XT_duplicate_channel(aImarisId):

    vImarisLib = ImarisLib.ImarisLib()
    vImaris = vImarisLib.GetApplication(aImarisId)
    vDataSet = vImaris.GetDataSet()

    print('''
    ####################################################################################
    ###########################     Extension started     ##############################
    ####################################################################################
    ''')
    time.sleep(2)

    nC = vDataSet.GetSizeC()
    nT = vDataSet.GetSizeT()

    channel_list = range(1, nC+1)

    channel_selected = create_window_from_list(channel_list, window_title='Select channel A')
    ch_in = np.int64(channel_selected)
    ch_in_name = vDataSet.GetChannelName(ch_in-1)
    print('Input acquired for channel : '+str(ch_in_name))
    time.sleep(2)

    ch_out = nC+1
    ch_out_name = ch_in_name+' - Duplicate'
    vDataSet.SetSizeC(ch_out)
    vDataSet.SetChannelName(ch_out - 1, ch_out_name)
    print('Selected Channel : '+str(ch_in_name))
    time.sleep(5)

    for ti in tqdm(range(nT)):

        data_channel_list = vDataSet.GetDataVolumeFloats(aIndexC=ch_in-1, aIndexT=ti)
        data_channel = np.array(data_channel_list)

        data_out = data_channel
        data_out_list = data_out.tolist()
        vDataSet.SetDataVolumeFloats(aData=data_out_list, aIndexC=ch_out-1, aIndexT=ti)
        time.sleep(3)


    print('''
    ####################################################################################
    #########     Extension finished, wait for 5s to close automatically     ###########
    ####################################################################################
    ''')
    time.sleep(5)


{% endhighlight %}

---

## Go back to [Home page][go-back-to-home]

[go-back-to-home]: https://cvbi.github.io/python-XTensions
