import numpy as np
import os
import cv2
from tifffile import imread,imsave

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



#split up images into tiles that the GPU on the cluster can handle

def tile_tif(img_path):

    # Some image; get width and height
    image = imread(img_path)
    _,h, w = image.shape

    #determine if image needs to be tiled
    status= "not_tiled"
    img_area=h*w

    if img_area > 10000*10000:
        #update status to tiled
        status= "tiled"
        # Tile parameters
        wTile = np.int(np.ceil(w/(np.ceil(w/10000))))
        hTile = np.int(np.ceil(h/(np.ceil(h/10000))))

        # Number of tiles
        nTilesX = np.uint8(np.ceil(w / wTile))
        nTilesY = np.uint8(np.ceil(h / hTile))

        # Total remainders
        remainderX = nTilesX * wTile - w
        remainderY = nTilesY * hTile - h

        # Set up remainders per tile
        remaindersX = np.ones((nTilesX-1, 1)) * np.uint16(np.floor(remainderX / (nTilesX-1)))
        remaindersY = np.ones((nTilesY-1, 1)) * np.uint16(np.floor(remainderY / (nTilesY-1)))
        remaindersX[0:np.remainder(remainderX, np.uint16(nTilesX-1))] += 1
        remaindersY[0:np.remainder(remainderY, np.uint16(nTilesY-1))] += 1

        # Initialize array of tile boxes
        tiles = np.zeros((nTilesX * nTilesY, 4), np.uint16)

        # Determine proper tile boxes
        k = 0
        x = 0
        for i in range(nTilesX):
            y = 0
            for j in range(nTilesY):
                tiles[k, :] = (x, y, hTile, wTile)
                k += 1
                if (j < (nTilesY-1)):
                    y = y + hTile - remaindersY[j]
            if (i < (nTilesX-1)):
                x = x + wTile - remaindersX[i]


        #Get tiles base on tile information found above and export as tif
        outdir = str(os.path.dirname(img_path) + '/tiled_tif/')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            
        for i in range(tiles.shape[0]):

            #get rows
            x=tiles[i][0]
            width=tiles[i][0]+tiles[i][2]

            #if not at end of image add 500 pixels for overlap
            if width < w:
                width = width + 500

            #Get columns
            y=tiles[i][1]
            height=tiles[i][1]+tiles[i][3]

            #if not at end of image add 500 pixels for overlap
            if height < h:
                height = height + 500

            #get tile and export as tif
            tile = image[:,x:width,y:height]
            outpath = str(outdir + img_path.split("/")[-1].split('.tif')[0] + "_tile_" + str(i) + ".tif")
            imsave(outpath,tile)
