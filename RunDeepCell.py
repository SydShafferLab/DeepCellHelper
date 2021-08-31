##FILL FOLLOWING VARIABLES

#path do a single tif file or directory with multiple tif Files

input = '/home/gharm/DeepCell/DeepCellHelper/10X_full.tif'

# which channel contains a nuclear stain to use for segmentation (number)
NucleusChannel= 1

# which channel contains a cytoplasmic stain to use for segmentation (number)
CytoplasmChannel= 0

#which objective did you use for these scans (note that if using something other than Shaffer Lab scope this will not work and you need to change the library in RunDeepCell function)
objective = '10x'




import time
t0 = time.time()
import os
import glob
os.chdir('/home/gharm/DeepCell/DeepCellHelper/')
from Cyto_Nuc_DeepCell import RunDeepCell

TIFS = glob.glob('/home/gharm/Scan_data/**/*.tif',recursive=True)

for tif in TIFS:
    print(tif)
    RunDeepCell(tif,NucleusChannel,CytoplasmChannel,objective)

t1 = time.time()
total = t1-t0
print(total)
