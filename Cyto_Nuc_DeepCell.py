import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
from matplotlib import pyplot as plt
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from deepcell.applications import CytoplasmSegmentation
#removed nuclear segmenter as it performs worse than mesmer, if you want to try it just uncoment all the lines associated with NuclearSegmentation
from deepcell.applications import NuclearSegmentation
from deepcell.applications import Mesmer
import tifffile
#to use helper funtion need to be in directory
from dcHelper import readTiffs


def RunDeepCell(path,nuc_channel,cyto_channel,objective):

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
    RESOLUTIONS = {'10x':1.3, '10X':1.3,'20x':.5,'20X':.5, '60x':.2167, '60X':.2167,'100x':.13,'100X':.13}
    resolution = RESOLUTIONS[objective]


    #get weights for segmentation
    if nuc_channel >= 0:
        NucSeg = NuclearSegmentation()
        #MesSeg = Mesmer()
    if cyto_channel >= 0:
        CytoSeg = CytoplasmSegmentation()

    #perform segmentation
    if nuc_channel >= 0:
        Nuc_labeled_im = NucSeg.predict(image[:,...,nuc_channel,None], image_mpp = resolution)
        #Nuc_labeled_im2 = MesSeg.predict(image, image_mpp = resolution, compartment='nuclear')
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

    print("Mask Files can be foun in this directory:", outpath)
    #write tif files with masks
    if nuc_channel >= 0:
        #tifffile.imwrite(str(outpath+'nuc_mask.tif'), Nuc_labeled_im)
        tifffile.imwrite(str(outpath+'_nuc_mask.tif'), Nuc_labeled_im)

    if cyto_channel >= 0:
        tifffile.imwrite(str(outpath+'_cyto_mask.tif'), Cyto_labeled_im)
        #tifffile.imwrite(str(outpath+'mesmer_cyto_mask.tif'), Cyto_labeled_im2)

    return Nuc_labeled_im, Cyto_labeled_im
