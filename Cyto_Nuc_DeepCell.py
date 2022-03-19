import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
from matplotlib import pyplot as plt
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from deepcell.applications import CytoplasmSegmentation
from deepcell.applications import NuclearSegmentation
from deepcell.applications import Mesmer
import tifffile
import cv2

#to use helper funtion need to be in directory
from dcHelper import readTiffs

sys.path.append("/home/gharm/DeepTile")
from deeptile import DeepTile


def RunDeepCell(path,nuc_channel,cyto_channel,objective,type):

    #Input Data
    if nuc_channel <=0:
        channels = [cyto_channel]
    elif cyto_channel <=0:
        channels = [nuc_channel]
    else:
        channels = [nuc_channel,cyto_channel]


    print("channels =", channels)
    image = readTiffs(path,channels)
    if image.shape[3] == 1:
        image=np.take(image,[0,0],-1)
    print(image.shape)
    #redifine channels for 0 index
    nuc_channel = nuc_channel-1
    cyto_channel = cyto_channel-1
    #input resolution of input image
    #these only true for Shaffer Lab scope assumin 2x2 binning, need to change based on scope
    RESOLUTIONS = {'4x':3.25, '4X':3.25, '10x':1.3, '10X':1.3,'20x':.5,'20X':.5, '60x':.2167, '60X':.2167,'100x':.13,'100X':.13}
    resolution = RESOLUTIONS[objective]


    #get weights for segmentation
    if nuc_channel >= 0:
        if type == 'TC':
            NucSeg = NuclearSegmentation()
        elif type == 'tissue':
            MesSeg = Mesmer()
        else:
            print("input for type variable is unknown")
            sys.exit()

    if cyto_channel >= 0:
        CytoSeg = CytoplasmSegmentation()

    #perform segmentation
    if nuc_channel >= 0:
        if type == 'TC':
            Nuc_labeled_im = NucSeg.predict(image[:,...,nuc_channel,None], image_mpp = resolution)
        if type == 'tissue':
            Nuc_labeled_im = MesSeg.predict(image, image_mpp = resolution, compartment='nuclear')
    else:
        Nuc_labeled_im = "no nuclear channel inputed"

    if cyto_channel >= 0:
        Cyto_labeled_im = CytoSeg.predict(image[:,...,cyto_channel,None], image_mpp = resolution)
        #Cyto_labeled_im2 = MesSeg.predict(image, image_mpp = resolution)
    else:
        Cyto_labeled_im = "no cytoplasm channel inputed"

    #define outpath
    if os.path.isfile(path):
        #split_path = path.split('/')[0:-1]
        #outpath = str('/'.join(split_path) + '/')
        outpath =  path.split('.tif')[0]
    elif os.path.isdir(path):
        outpath = str(path + '/')

    #write tif files with masks
    if nuc_channel >= 0:
        #tifffile.imwrite(str(outpath+'nuc_mask.tif'), Nuc_labeled_im)
        tifffile.imwrite(str(outpath+'_nuc_mask.tif'), Nuc_labeled_im)

    if cyto_channel >= 0:
        tifffile.imwrite(str(outpath+'_cyto_mask.tif'), Cyto_labeled_im)
        #tifffile.imwrite(str(outpath+'mesmer_cyto_mask.tif'), Cyto_labeled_im2)

    print("Mask Files can be foun in this directory:", outpath)

    return Nuc_labeled_im, Cyto_labeled_im



# Run cell using DeepTile


def RunDeepTile(path,nuc_channel,cyto_channel,objective,algorithm,tileSize=10000,Well=False):

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
    RESOLUTIONS = {'4x':3.25, '4X':3.25, '10x':1.3, '10X':1.3,'20x':.5,'20X':.5, '60x':.2167, '60X':.2167,'100x':.13,'100X':.13}
    resolution = RESOLUTIONS[objective]


    # load image and put in proper format
    image = tifffile.imread(path)

    if len(image.shape) == 2:
        image = image
    elif len(image.shape) == 3:
        image = image[channels,...]
        image = np.squeeze(image)
    elif len(image.shape) == 4:
        image = image[channels,...,0]
        image = np.squeeze(image)


    if nuc_channel < 0:
        if len(channels) == 1:
            image =  np.stack((np.full(image.shape, 0),image), axis =0)
    elif cyto_channel < 0:
        if len(channels) == 1 :
            image =  np.stack((image,np.full(image.shape, 0)), axis =0)


    print(image.shape)
    # Number of tiles
    _,h, w = image.shape
    wTile = np.int(np.ceil(w/(np.ceil(w/tileSize))))
    hTile = np.int(np.ceil(h/(np.ceil(h/tileSize))))

    nTilesX = np.uint8(np.ceil(w / wTile))
    nTilesY = np.uint8(np.ceil(h / hTile))


    # run DeepCell using DeepTile
    dt = DeepTile(image)

    dt.create_job(n_blocks=(nTilesY ,nTilesX), overlap=(0.1, 0.1), algorithm=algorithm , eval_parameters={"image_mpp":resolution})

    masks = dt.run_job()

    # remove all masks located outside the well
    if Well == True:
      ##find well perimeter
      small_img = (image[0,...]/256).astype('uint8')
      #percent by which the image is resized
      scale_percent = 30
      #calculate the x percent of original dimensions
      width = int(small_img.shape[1] * scale_percent / 100)
      height = int(small_img.shape[0] * scale_percent / 100)
      # dsize
      dsize = (width, height)
      # resize image
      small_img = cv2.resize(small_img, dsize)
      maxRadius = round(max(small_img.shape)/1.5)
      minRadius = round(max(small_img.shape)/4)
      minDist = round(max(small_img.shape))
      downSize = 10
      #add blur
      blurred = cv2.GaussianBlur(small_img, (11,11), 0)
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
          nuc_mask = masks[0,...]
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
          masks[0,...] = vs[np.searchsorted(ks,nuc_mask)]
      if cyto_channel >= 0:
          cyto_mask = masks[1,...]
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
          masks[1,...] = vs[np.searchsorted(ks,cyto_mask)]

    #define outpath
    outpath =  path.split('.tif')[0]

    #write tif files with masks
    if nuc_channel >= 0:
        tifffile.imwrite(str(outpath + "_"+ algorithm + '_nuc_mask.tif'), np.uint32(masks[0,...]))

    if cyto_channel >= 0:
        tifffile.imwrite(str(outpath + "_"+ algorithm +'_cyto_mask.tif'), np.uint32(masks[1,...]))

    print("Mask Files can be found in this directory:", outpath)

    return np.uint32(masks)
