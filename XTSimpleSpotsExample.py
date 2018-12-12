#  PythonXT Simple Spots Example for Imaris
#
#  Copyright Bitplane AG
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Default">
#       <Item name="Simple Spots Example" icon="Python" tooltip="Simple XTension creating a Spot in the Center of the Dataset">
#         <Command>PythonXT::XTSimpleSpotsExample(%i)</Command>
#       </Item>
#      </Submenu>
#      </Menu>
#    </CustomTools>


import time
import ImarisLib

def XTSimpleSpotsExample(aImarisId):

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
    
  # Get the currently loaded dataset  
  vImage = vImaris.GetDataSet()
  
  # This xtension requires a loaded dataset
  if vImage is None:
    print 'An image has to be loaded into Imaris first'
    time.sleep(2)
    return

  # Get the extents of the image
  vExtentMinX = vImage.GetExtendMinX();
  vExtentMinY = vImage.GetExtendMinY();
  vExtentMinZ = vImage.GetExtendMinZ();
  vExtentMaxX = vImage.GetExtendMaxX();
  vExtentMaxY = vImage.GetExtendMaxY();
  vExtentMaxZ = vImage.GetExtendMaxZ();

  vImageSizeX = vExtentMaxX - vExtentMinX;
  vImageSizeY = vExtentMaxY - vExtentMinY;
  vImageSizeZ = vExtentMaxZ - vExtentMinZ;
  
  vMinRadius = min(vImageSizeX, vImageSizeY, vImageSizeZ) / 2;
  
  # Calculate the center of the image
  vCenterX = (vExtentMinX + vExtentMaxX) / 2;
  vCenterY = (vExtentMinY + vExtentMaxY) / 2;
  vCenterZ = (vExtentMinZ + vExtentMaxZ) / 2;
  
  # Create a spots component
  vSpotsComponent = vImaris.GetFactory().CreateSpots();
  
  # Add one spot in the center
  # The positions array is 2 dimensional
  vSpotsComponent.Set([[vCenterX, vCenterY, vCenterZ]], [0], [vMinRadius]);
  
  # Give the component are nice name
  vSpotsComponent.SetName('Image Center Spot');
  
  # Color the one spot red
  vSpotsComponent.SetColorRGBA(255);

  # Add the spots component at the end of the surpass tree
  vImaris.GetSurpassScene().AddChild(vSpotsComponent, -1);
