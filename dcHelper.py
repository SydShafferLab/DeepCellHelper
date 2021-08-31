import numpy as np
import os

from tifffile import imread

def readTiffs(path,channels):

    channels = [channel-1 for channel in channels]

    if os.path.isfile(path):

        array = imread(path)

        if array.ndim == 2:
            array = np.expand_dims(array,axis=-1)
        elif array.ndim == 3:
            if len(channels) == 0:
                array = np.moveaxis(array,0,-1)
            else:
                array = np.moveaxis(np.take(array,channels,0),0,-1)
        array = np.expand_dims(array,axis=0)

    elif os.path.isdir(path):

        files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file)) and file.endswith('.tif')]
        ims = [imread(os.path.join(path,file)) for file in files]
        shapes = np.array([im.shape for im in ims]).T

        if ims[0].ndim == 2:
            dims = (np.max(shapes[-2]),np.max(shapes[-1]))
            ims = [np.pad(im,((0,dims[0] - im.shape[0]),(0,dims[1] - im.shape[1]))) if im.shape != dims else im for im in ims]
            ims = np.expand_dims(ims,axis=-1)
        elif ims[0].ndim == 3:
            dims = (np.max(shapes[-2]),np.max(shapes[-1]),ims[0].shape[0])
            if len(channels) == 0:
                ims = [np.moveaxis(im,0,-1) for im in ims]
            else:
                ims = [np.moveaxis(np.take(im,channels,0),0,-1) for im in ims]
            ims = [np.pad(im,((0,dims[0] - im.shape[0]),(0,dims[1] - im.shape[1]),(0,0))) if im.shape != dims else im for im in ims]

        array = np.stack(ims,0)

    return array
