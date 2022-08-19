# DeepCellHelper
The purpose of this repository is to help you rapidly get cell segmentation running using deepcell on google colab (although it should also run in a jupyter notebook). 

NOTE: This repository adds a small function to make deepcell easy to run. To make things simple for the end user, all packages you need are included in this
repository, but were not written by me. The repository for the cell segmentation algorithm used, deepcell, can be found here: https://github.com/vanvalenlab/deepcell-tf.
The function used to split up large images into manageable tiles for deepcell can be found here: https://github.com/arjunrajlaboratory/DeepTile.

## Setting up for use on Google Colab 
Google Colab gives access to GPUs which makes running deepcell significantly faster. An issue with google colab is that every time you open a session it does not save
any previously installed packages. To avoid the need to install large packages such as deepcell each time we will create a folder on google drive containing the necessary
package and then mount google drive to google colab.

1. The first step is to download DeepCellHelper from GitHub by clicking the green "Code" button above and selecting "Download ZIP." You should now have a file in your download folder 
called "DeepCellHelper-main." Rename this folder to "DeepCellHelper".

2. Go to your google drive account and, in the "My Drive" folder, create a folder called "Colab" and add in the DeepCellhelper folder downloaded from this repository.

3. Once the folder has uploaded, open the "RunDeeptile.ipynb" file with google colab (if you are accessing drive through your browser, you can do this by right-clicking on the file and hovering over "open with" 
and selecting "Google Colaboratory")

4. You now need to mount google drive to this google colab session. To do this, click on the folder icon on the left side of the colab notebook, and then click on the icon folder that has the google drive icon on it.
You may be asked to run a code cell to mount the google drive and select which drive you would like to connect, follow the prompts provided.

Steps for mounting drive:
<img src="https://github.com/SydShafferLab/DeepCellHelper/blob/main/imagesForReadMe/MountingDrive.png">

5. You should now be able to see a new folder appear called "drive". Navigate through this drive folder by clicking through "drive>MyDrive>Colab>DeepCellHelper". Once in the Deep cell helper folder, right-click on the 
"packages" folder and click "Copy path" and then paste this path into the code cell shown below. If you set up your files as indicated above the path should already be correct, the key here is that the path input is 
the path to the downloaded "packages" folder. You should now be ready to run deepcell.

Code cell you should input the package path into:
<img src="https://github.com/SydShafferLab/DeepCellHelper/blob/main/imagesForReadMe/AddPackagePath.png">
