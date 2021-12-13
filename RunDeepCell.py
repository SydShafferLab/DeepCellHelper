import glob
import os

##FILL FOLLOWING VARIABLES

#path do a single tif file or directory with multiple tif Files

TIFS = glob.glob('/home/gharm/Scan_data/**/*.tif',recursive=True)

# which channel contains a nuclear stain to use for segmentation (number)
NucleusChannel= 1

# which channel contains a cytoplasmic stain to use for segmentation (number)
CytoplasmChannel= 0

#which objective did you use for these scans (note that if using something other than Shaffer Lab scope this will not work and you need to change the library in RunDeepCell function)
objective = '10x'

#specify sample type of sample you are using (TC or tissue)
type = 'tissue'


# change this path to location ot DeepCellHelper
os.chdir('/home/gharm/DeepCell/DeepCellHelper/')

##SHOULD NOT NEED TO EDIT BELOW THIS

from Cyto_Nuc_DeepCell import RunDeepCell
from dcHelper import tile_tif

#for tif in TIFS:
#    #subset tif file into tiles manageable for the GPU if image is larger than 10k by 10K pixels
#    tile_tif(tif)
#    tile_dir = os.path.dirname(tif)
#    tile_dir = str(tile_dir + '/*.tif')
#    TILES = glob.glob(tile_dir,recursive=True)

for tif in TIFS:
    RunDeepCell(tif,NucleusChannel,CytoplasmChannel,objective,type)

    #put tiles back together
