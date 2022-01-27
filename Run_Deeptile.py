import glob
import os
import sys
import numpy as np

##FILL FOLLOWING VARIABLES

#path do a single tif file or directory with multiple tif Files

TIFS = glob.glob('/Users/guillaumeharmange/Desktop/Test_Dat/tst_img.tif',recursive=True)

#path to final mask
OutPath = '/Users/guillaumeharmange/Desktop/Test_Dat/tst_img_mask.tif'
# which channel contains a nuclear stain to use for segmentation (number)
NucleusChannel= 1

# which channel contains a cytoplasmic stain to use for segmentation (number)
CytoplasmChannel= 2

#which objective did you use for these scans (note that if using something other than Shaffer Lab scope this will not work and you need to change the library in RunDeepCell function)
objective = '10x'

#specify sample type of sample you are using (TC or tissue)
#type = 'tissue'
algorithm = 'deepcell_mesmer'

# change this path to location ot DeepCellHelper
#dc_helperPath = '/Users/guillaumeharmange/Documents/GitHub/DeepCellHelper'

dc_tilePath = '/Users/guillaumeharmange/Documents/GitHub/DeepTile'

##SHOULD NOT NEED TO EDIT BELOW THIS LINE

#os.chdir(dc_helperPath)
#from Cyto_Nuc_DeepCell import RunDeepCell
#from dcHelper import tile_tif

sys.path.append(dc_tilePath)

from deeptile import DeepTile

import tifffile


#load images
image = tifffile.imread(TIFS)
#image = image[NucleusChannel-1,...]
image =  np.stack((image[NucleusChannel-1,...],image[CytoplasmChannel-1,...]), axis =0)

# Set Parmeters
RESOLUTIONS = {'10x':1.3, '10X':1.3,'20x':.5,'20X':.5, '60x':.2167, '60X':.2167,'100x':.13,'100X':.13}
resolution = RESOLUTIONS[objective]

# Number of tiles
_,h, w = image.shape
wTile = np.int(np.ceil(w/(np.ceil(w/10000))))
hTile = np.int(np.ceil(h/(np.ceil(h/10000))))

nTilesX = np.uint8(np.ceil(w / wTile))
nTilesY = np.uint8(np.ceil(h / hTile))

print(nTilesY)
print(nTilesX)

# run DeepCell
dt = DeepTile(image)

dt.create_job(n_blocks=(nTilesY ,nTilesX), overlap=(0.1, 0.1), algorithm=algorithm , eval_parameters={"image_mpp":resolution})

masks = dt.run_job()

tifffile.imwrite(OutPath, np.uint32(masks[0,...]))
