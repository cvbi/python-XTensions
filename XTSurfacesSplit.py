#  SurfacesSplit XTension
#
#  Copyright Bitplane AG
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#      <Submenu name = "Default">
#       <Item name="Surfaces Split" icon="Python" tooltip="Split one Surfaces component into different Surfaces. One new component is created for each disconnected Surface.">
#         <Command>PythonXT::XTSurfacesSplit(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>


import ImarisLib
import time
import random

def XTSurfacesSplit(aImarisId):
	# Create an ImarisLib object
	vImarisLib = ImarisLib.ImarisLib()

	# Get an imaris object with id aImarisId
	vImaris = vImarisLib.GetApplication(aImarisId)

	# Check if the object is valid
	if vImaris is None:
		print 'Could not connect to Imaris!'
		# Sleep 2 seconds to give the user a chance to see the printed message
		time.sleep(2)
		return

	# Get the factory
	vFactory = vImaris.GetFactory()

	# Get the surpass scene
	vSurpassScene = vImaris.GetSurpassScene()

	# This XTension requires a loaded dataset
	if vSurpassScene is None:
		print 'Please create some Surfaces in the Surpass scene!'
		time.sleep(2)
		return

	# get the surfaces
	vSurfaces = vFactory.ToSurfaces(vImaris.GetSurpassSelection())

	# search the surfaces if not previously selected
	if not vFactory.IsSurfaces(vSurfaces):
		for vChildIndex in range(vSurpassScene.GetNumberOfChildren()):
			vDataItem = vSurpassScene.GetChild(vChildIndex)
			if vSurfaces is None:
				if vFactory.IsSurfaces(vDataItem):
					vSurfaces = vFactory.ToSurfaces(vDataItem)
		# did we find the surfaces?
		if vSurfaces is None:
			print 'Please create some Surfaces in the Surpass scene!'
			time.sleep(2)
			return

	vNumberOfSurfaces = vSurfaces.GetNumberOfSurfaces()
	vSurfacesName = vSurfaces.GetName()
	vSurfaces.SetVisible(0)

	# create new group
	vSurfacesGroup = vFactory.CreateDataContainer()
	vSurfacesGroup.SetName(vSurfacesName + ' split')

	for vSurfaceIndex in range(vNumberOfSurfaces):
		vNewSurfaces = vSurfaces.CopySurfaces([vSurfaceIndex])
		vNewSurfaces.SetName( vSurfacesName + ' [' + str( vSurfaceIndex + 1 ) + ']'  )
		vNewSurfaces.SetColorRGBA(int(256**3*random.random()));
		vSurfacesGroup.AddChild(vNewSurfaces, -1);

	vSurpassScene.AddChild(vSurfacesGroup, -1)


