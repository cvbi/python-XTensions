# -*- coding: utf-8 -*-
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
#
#  Ipython XTension and Ipython magics wrapped in one file.
#  Inspired by ipython-idlmagic
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#      <Submenu name = "Code">
#       <Item name="Jupyter-notebook" icon="Python" tooltip="Run iPython">
#         <Command>PythonXT::Run(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>
#
#
# Copyright (c) 2016 Egor Zindy <egor.zindy@manchester.ac.uk>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Some code and ideas taken from idlmagic.py
# https://github.com/ebellm/ipython-idlmagic/blob/master/idlmagic.py
#
# Copyright (C) 2013 Eric Bellm
# Copyright (C) 2012 The IPython Development Team
#
# Distributed under the terms of the BSD License. This software was derived
# from components of IPython; the full license is in
# the file COPYING, distributed as part of that software.
#


"""
===========
XTIPy magic
===========
Magics for interacting with Imaris via ImarisLib / BridgeLib

Usage
=====
``%imaris_version``
{IMARIS_VERSION_DOC}
``%imaris_help``
{IMARIS_HELP_DOC}
``%imaris_push``
{IMARIS_PUSH_DOC}
``%imaris_pull``
{IMARIS_PULL_DOC}
"""

from __future__ import print_function
import os
import sys
import time
import hotswap
import numpy as np
import ImarisLib
import BridgeLib
import tempfile


from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.testing.skipdoctest import skip_doctest
from IPython.utils.py3compat import unicode_to_str

print('Starting Jupyter Notebook in browser :')
print('\n'*10)
time.sleep(5)

class ImarisMagicError(Exception):
    pass

@magics_class
class ImarisMagics(Magics):
    """A set of magics useful for doing interactive work with Imaris via ImarisLib/BridgeLib
    """

    def __init__(self, shell):
        # You must call the parent constructor
        super(ImarisMagics, self).__init__(shell)
        print("You can now access BridgeLib, ImarisLib, vImaris, vDataSet, vScene and vFactory")

        self.ImarisId = int(os.environ.get("IMARISID"))
        self.vImaris, self.vDataSet = BridgeLib.Reconnect(self.ImarisId)

        #Make these available to the Interactive shell
        shell.user_ns["BridgeLib"]=BridgeLib
        shell.user_ns["ImarisLib"]=ImarisLib
        shell.user_ns["vImaris"]=self.vImaris
        shell.user_ns["vDataSet"]=self.vDataSet
        shell.user_ns["vScene"]=self.vImaris.GetSurpassScene()
        shell.user_ns["vFactory"]=self.vImaris.GetFactory()

    @skip_doctest
    @line_magic
    def imaris_screenshot(self, line):
        '''Line-level magic that takes a screenshot of Imaris.
        '''

        f = tempfile.NamedTemporaryFile(delete=False,suffix='.png')
        self.vImaris.SaveSnapShot(f.name)
        i = Image(filename=f.name)
        f.close()
        os.unlink(f.name)
        return i

    @skip_doctest
    @line_magic
    def imaris_pull(self, line):
        '''Line-level magic that pulls objects from Imaris.

        You can pull: spots, surfaces, filaments or cells.

            In [6]: %imaris_pull spots
            Out[6]: ['Spots 1', 'Spots 1 Selection']

            In [7]: spots[_[0]]
            Out[7]: 36ffa5dc-2456-4c94-9ad3-e639acd67122 -t:tcp -h 192.168.1.11 -p 62088
        '''

        if line == "":
            print(self.imaris_pull.__doc__)
            return

        ret = []
        outputs = line.split(' ')
        for output in outputs:
            output = unicode_to_str(output).lower()
            if output in ["spots", "surfaces", "filaments", "cells"]:
                objs = BridgeLib.GetSurpassObjects(self.vImaris,output)
                self.shell.push({output: objs})
                ret.append(objs.keys())
            else:
                raise ImarisMagicError('No such object available')

        if len(outputs) == 1:
            return ret[0]
        else:
            return ret

    @skip_doctest
    @line_magic
    def imaris_push(self, line):
        '''Line-level magic that pulls a variable from Imaris.
        '''

        if line == "":
            print(self.imaris_pull.__doc__)

    @skip_doctest
    @line_magic
    def imaris_help(self, line):
        '''Line-level magic that pulls the webpage from Imaris

        Just call this magic to open the "Imaris XT Interface" page in your browser.

            In [8]: %imaris_help
        '''

        #This is the path of the Imaris installation
        p = ImarisLib.__file__.split(os.sep)[:-3]
        p.append('html/xtinterface/index.html')
        #open in a new tab if possible
        webbrowser.open(os.path.join(*p),2)

    @skip_doctest
    @line_magic
    def imaris_version(self, line):
        '''Line-level magic that display the version number.
        '''

        return self.vImaris.GetVersion()


__doc__ = __doc__.format(
    IMARIS_PUSH_DOC = ' '*8 + ImarisMagics.imaris_push.__doc__,
    IMARIS_PULL_DOC = ' '*8 + ImarisMagics.imaris_pull.__doc__,
    IMARIS_HELP_DOC = ' '*8 + ImarisMagics.imaris_help.__doc__,
    IMARIS_VERSION_DOC = ' '*8 + ImarisMagics.imaris_version.__doc__,
    )

def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics, plugins or aliases, for example.
    magics = ImarisMagics(ipython)
    ipython.register_magics(magics)


def Run(aImarisId):
    vImaris, vDataSet = BridgeLib.Reconnect(aImarisId)

    # Check if the object is valid
    if vImaris is None:
        print("Could not connect to Imaris!")
        exit(1)

    #No need to check for a vDataSet, maybe you want to import Datasets using BridgeLib.
    #if vDataSet is None:
    #    print("No data available!")
    #    exit(1)

    global ImarisId
    ImarisId = aImarisId
    #The hotswap module watcher...
    #_watcher = hotswap.ModuleWatcher()
    #_watcher.run()

    #print(os.system("python --version"))
    os.environ["IMARISID"] = str(aImarisId)
    path_old = os.environ["PYTHONPATH"].replace('/','\\').rstrip()
    os.environ["PYTHONPATH"] = os.getcwd()+os.path.pathsep+path_old
    sys.argv = [sys.argv[0]] #,'--ip=\'*\'','--notebook-dir=\'%s\'' % p]

    print(os.environ["PYTHONPATH"])
    #print(os.system("python --version"))
    time.sleep(5)

    os.system('jupyter notebook --notebook-dir=~')
    #sys.exit(main())
