#  Gauss Filtering XTension
#
#  Copyright Bitplane AG
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#      <Submenu name = "Default">
#       <Item name="Gauss Filtering" icon="Python" tooltip="Calls the Imaris Gauss Filter method with specified channel index and smoothing value.">
#         <Command>PythonXT::XTGaussFiltering(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>


import ImarisLib
import time
import random

# GUI imports
from Tkinter import *
import tkMessageBox
import tkSimpleDialog


def XTGaussFiltering(aImarisId):
	# Create an ImarisLib object
	vImarisLib = ImarisLib.ImarisLib()

	# Get an imaris object with id aImarisId
	vImaris = vImarisLib.GetApplication(aImarisId)
		
	# Initialize and launch Tk window
	vRootTkWindow = Tk()
	# Hide the default Tk root window
	vRootTkWindow.withdraw()

	# Check if the object is valid
	if vImaris is None:
		print('Could not connect to Imaris!')
		tkMessageBox.showwarning(
            "connection failed",
            "Could not connect to Imaris!"
		)
		time.sleep(2)
		return

	# Get the dataset
	vDataSet = vImaris.GetDataSet()
	if vDataSet is None:
		print('An image must be loaded to run this XTension!')
		tkMessageBox.showwarning(
            "Image needed",
            "An image must be loaded to run this XTension!"
		)
		time.sleep(2)
		return
	
	vChannelIndex = 0
	vNumberOfChannels = vDataSet.GetSizeC()
	# Get the channel index from the user if there are multiple channels
	if vNumberOfChannels > 1:
		# Create and display the channel selection window
		vChannelTkWindow = Toplevel()
		vChannelTkWindow.title("Channel")
		
		Label(vChannelTkWindow, 
			text="""Choose the channel to be smoothed:""",
			justify = LEFT,
			padx = 5).pack()
		
		vChannelRadioButton = IntVar()
		# Set default value
		vChannelRadioButton.set(-1)
		for vIndice in range(vNumberOfChannels):
			# Add a radio button for each channel
			vRadioButton = Radiobutton(vChannelTkWindow,
						text=str(vIndice+1) + " - " + vDataSet.GetChannelName(vIndice),
						padx = 20,
						pady = 5,
						variable=vChannelRadioButton, 
						value=vIndice)
			# Set the layout
			vRadioButton.pack(anchor=W)
		vValidationButton = Button(vChannelTkWindow, text="OK", command=vChannelTkWindow.destroy)
		vValidationButton.pack(expand = 1, fill= BOTH)
		# Wait for the answer of the channel selection window
		vRootTkWindow.wait_window(vChannelTkWindow)
		
		# Get the selected value
		vChannelIndex = vChannelRadioButton.get()
		# If the window is closed without any channel selected
		if vChannelIndex is -1:
			return

	vSigma = tkSimpleDialog.askfloat("Smoothing value", "Specify the smoothing value: ")
	# If a click on "Cancel" occured
	if vSigma is None:
		return
	
	# The GUI windows are not needed anymore
	vRootTkWindow.destroy

	vIP = vImaris.GetImageProcessing()
	vIP.GaussFilterChannel(vDataSet, vChannelIndex, vSigma)
	

