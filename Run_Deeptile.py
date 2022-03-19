import os
import glob

##FILL FOLLOWING VARIABLES

#path do a single tif file or directory with multiple tif Files

TIFS = glob.glob("/home/gharm/Hemma_Scope_Images/*.tif",recursive=True)

# which channel contains a nuclear stain to use for segmentation (number)
NucleusChannel= 1

# which channel contains a cytoplasmic stain to use for segmentation (number)
CytoplasmChannel= 0

#which objective did you use for these scans (note that if using something other than Shaffer Lab scope this will not work and you need to change the library in RunDeepCell function)
objective = '10x'

#specify sample algorith you are using (tissue: deepcell_mesmer, TC nucleus:deepcell_nuclear, TC cytoplasm :deepcell_cytoplasm )

algorithm = 'deepcell_nuclear'

# change this path to location ot DeepCellHelper

dc_tilePath = '/home/gharm/DeepTile'


# change tile size(default =10000)
tileSize=10000

# If your image contains the outline of a round well make this argument True if not say False (default False)
Well = True

##SHOULD NOT NEED TO EDIT BELOW THIS LINE
os.chdir('/home/gharm/DeepCell/DeepCellHelper/')
from Cyto_Nuc_DeepCell import RunDeepTile

for tif in TIFS:
    RunDeepTile(tif,NucleusChannel,CytoplasmChannel,objective,algorithm,tileSize,Well)
