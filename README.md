# DeepCell Helper

Scripts for streamlining workflows using the [DeepCell](https://github.com/vanvalenlab/deepcell-tf) segmentation library.

## Modules

* readTiffs: reads either a single .tif file or directory of .tif files into an array with DeepCell's required input format
  * `path` path of either a single .tif file or directory of .tif files
  * `channels` list of channels to be included
  * Return `numpy.ndarray` with the format `(batch, x, y, channel)`

## Using GPU
If using a GPU you will also need to donload cudNN version 8.2 here: https://developer.nvidia.com/cudnn and place it in the DeepCell folder
