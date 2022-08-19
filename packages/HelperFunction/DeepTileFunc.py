import sys
import numpy as np
import tifffile
import cv2
import deeptile
import time
import gc
from deeptile.extensions import segmentation
from deeptile.extensions import stitch
from deeptile.core.algorithms import transform

# Run cell using DeepTile (new version)

def RunDeepTile(path,nuc_channel,cyto_channel,objective,algorithm,type,tileSize=10000,Well=False,DeepCellBatch=30,DeepTileBatch=1):
    start = time.time()
    #redifine channels for 0 index
    nuc_channel = nuc_channel-1
    cyto_channel = cyto_channel-1

    #Input Data
    if nuc_channel < 0:
        channels = [cyto_channel]
    elif cyto_channel < 0:
        channels = [nuc_channel]
    else:
        channels = [nuc_channel,cyto_channel]


    print("channels =", channels)

    # Set Parmeters
    RESOLUTIONS = {'4x':3.25, '4X':3.25 ,'10x':1.3, '10X':1.3, '10x_fast': .75, '10X_fast': .75 ,'20x':.5,'20X':.5, '60x':.2167, '60X':.2167,'100x':.13,'100X':.13}
    resolution = RESOLUTIONS[objective]

    # Create DeepTile object
    dt = deeptile.load(path, link_data=False)

     #load image in proper configuration (not tested)
    if len(dt.image.shape) == 3:
        dt.image= dt.image[channels,...]
        dt.image = np.squeeze(dt.image)
    elif len(dt.image.shape) == 4:
        dt.image = dt.image[channels,...,0]
        dt.image = np.squeeze(dt.image)

    #generate tiles
    tile_size = (tileSize, tileSize)
    overlap = (0.1, 0.1)
    tiles = dt.get_tiles(tile_size, overlap)

    #add second image if necessary for deepcell compatibility
    if nuc_channel < 0:
        if len(channels) == 1:
            tiles = np.stack((np.zeros_like(tiles), tiles))
    elif cyto_channel < 0:
        if len(channels) == 1 :
            tiles = np.stack((tiles, np.zeros_like(tiles)))


    # Segment tiles and stitch
    model_parameters = {}
    eval_parameters = {'image_mpp' : resolution, 'compartment' : type , 'batch_size' : DeepCellBatch}
    func_process = segmentation.deepcell_mesmer_segmentation(model_parameters, eval_parameters)
    masks = dt.process(tiles, func_process, batch_size = DeepTileBatch)
    mask = dt.stitch(masks.s[0], stitch.stitch_masks())

    if len(mask.shape) < 3:
        mask = mask[np.newaxis,...]

    # remove all masks located outside the well
    if Well == True:
      ##find well perimeter
      image = tifffile.imread(path)

      if len(image.shape) >2:
          image = image[nuc_channel,...]

      image = (image/256).astype('uint8')
      #percent by which the image is resized
      scale_percent = 30
      #calculate the x percent of original dimensions
      width = int(image.shape[1] * scale_percent / 100)
      height = int(image.shape[0] * scale_percent / 100)
      # dsize
      dsize = (width, height)
      # resize image
      image = cv2.resize(image, dsize)
      maxRadius = round(max(image.shape)/1.5)
      print(image.shape)
      print(max(image.shape))
      print(maxRadius)
      minRadius = round(max(image.shape)/4)
      minDist = round(max(image.shape))
      downSize = 10
      #add blur
      blurred = cv2.GaussianBlur(image, (11,11), 0)
      del(image)
      gc.collect()
      #determine parametets for Canny (used in HoughCircles)
      v = np.median(blurred)
      sigma=.33
      #---- Apply automatic Canny edge detection using the computed median----
      lower = int(max(0, (1.0 - sigma) * v))
      upper = int(min(255, (1.0 + sigma) * v))
      if lower <=0:
          lower = .001
      circles = cv2.HoughCircles(image=blurred,
                                 method=cv2.HOUGH_GRADIENT,
                                 dp=downSize,
                                 minDist=minDist,
                                 param1=lower,
                                 param2=upper,
                                 minRadius=minRadius,
                                 maxRadius=maxRadius
                                )

      del(blurred)
      gc.collect()

      if circles is None:
          print ('No Well found found')

      elif len(circles) > 1:
          print("could not define well")

      elif len(circles) == 1:
          x, y, r = circles[0][0]
          scale_x = np.round(x/(scale_percent/100)).astype("int")
          scale_y = np.round(y/(scale_percent/100)).astype("int")
          scale_r = np.round(r/(scale_percent/100)).astype("int")

      if nuc_channel >= 0:
          nuc_mask = mask[0,...]
          nrows, ncols = nuc_mask.shape
          rows, cols = np.ogrid[:nrows, :ncols]
          outer_disk_mask = ((rows - scale_x)**2 + (cols - scale_y)**2 > scale_r**2)
          nuc_mask[outer_disk_mask] = 0
          keys = np.sort(np.unique(nuc_mask))
          values = np.array(range(0,len(keys)))
          # Get argsort indices
          sidx = keys.argsort()
          ks = keys[sidx]
          vs = values[sidx]
          mask[0,...] = vs[np.searchsorted(ks,nuc_mask)]

      if cyto_channel >= 0:
          cyto_mask = mask[1,...]
          nrows, ncols = cyto_mask.shape
          rows, cols = np.ogrid[:nrows, :ncols]
          outer_disk_mask = ((rows - scale_x)**2 + (cols - scale_y)**2 > scale_r**2)
          cyto_mask[outer_disk_mask] = 0
          keys = np.sort(np.unique(cyto_mask))
          values = np.array(range(0,len(keys)))
          # Get argsort indices
          sidx = keys.argsort()
          ks = keys[sidx]
          vs = values[sidx]
          mask[1,...] = vs[np.searchsorted(ks,cyto_mask)]

    #define outpath
    outpath =  path.split('.tif')[0]

    #write tif files with masks
    if nuc_channel >= 0:
        tifffile.imwrite(str(outpath + "_"+ algorithm + '_nuc_mask.tif'), np.uint32(mask[0,...]))

    if cyto_channel >= 0:
        tifffile.imwrite(str(outpath + "_"+ algorithm +'_cyto_mask.tif'), np.uint32(mask[1,...]))

    print("Mask Files can be found in this directory:", outpath)

    end = time.time()
    print(end-start)

    return np.uint32(mask)
