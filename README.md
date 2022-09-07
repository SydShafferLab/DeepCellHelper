# DeepCellHelper
The purpose of this repository is to help you rapidly get cell segmentation running using deepcell on google colab (although it should also run in a jupyter notebook). 

NOTE: This repository adds a small function to make deepcell easy to run. To make things simple for the end user, all packages you need are included in this repository but were not written by me. The repository for the cell segmentation algorithm used, deepcell, can be found here: https://github.com/vanvalenlab/deepcell-tf.
The function used to split up large images into manageable tiles for deepcell can be found here: https://github.com/arjunrajlaboratory/DeepTile.

## Setting up for use on Google Colab (you should only need to do this once)
Google Colab gives access to GPUs which makes running deepcell significantly faster. An issue with google Colab is that every time you open a session it does not save any previously installed packages. To avoid the need to install large packages such as deepcell each time we will create a folder on google drive containing the necessary package and then mount google drive to google Colab.

1. The first step is to download DeepCellHelper from GitHub by clicking the green "Code" button above and selecting "Download ZIP." You should now have a file in your download folder called "DeepCellHelper-main". Rename this folder to "DeepCellHelper".

2. Go to your google drive account and, in the "My Drive" folder, create a folder called "Colab" and add to it the DeepCellHelper folder downloaded from this repository.

3. Once the folder has uploaded, open the "RunDeeptile.ipynb" file with google Colab (if you are accessing drive through your browser, you can do this by right-clicking on the file and hovering over "open with" 
and selecting "Google Colaboratory")

4. You now need to mount google drive to this google colab session. To do this, click on the folder icon on the left side of the colab notebook, and then click on the icon folder that has the google drive icon on it. You may be asked to run a code cell to mount the google drive and select which drive you would like to connect, follow the prompts provided.

Steps for mounting drive:
<img src="https://github.com/SydShafferLab/DeepCellHelper/blob/main/imagesForReadMe/MountingDrive.png">

5. You should now be able to see a new folder appear called "drive". Navigate through this drive folder by clicking through "drive>MyDrive>Colab>DeepCellHelper". Once in the DeepCellHelper folder, right-click on the 
"packages" folder and click "Copy path" and then paste this path into the code cell shown below. If you set up your files as indicated above the path should already be correct. The key here is that the path input in this comand is 
the path to the downloaded "packages" folder.

Code cell you should input the package path into:
<img src="https://github.com/SydShafferLab/DeepCellHelper/blob/main/imagesForReadMe/AddPackagePath.png">

6. Finally in the block of code set up to change a bunch of user-defined parameters (should be code cell 3) change the path under the parameter labeled " change to path of HelperFunction" to the full path to the HelperFunction folder ex. '/content/drive/MyDrive/Colab/DeepCellHelper/packages/HelperFunction'. You should now be ready to run deepcell.

## Running DeepCell Helper
All you need to run deeptile should be in the RunDeeptile.ipynb file. This section runs through what each section does.

1. The first thing to do is to tell Colab we want to run on the GPU. To do this select "Runtime" from the top menu, select "Change run time type", and select "GPU" in the Hardware accelerator menu. If you are using a free version of Colab you will be very limited in the amount of memory you get so you will only be able to analyze small images (or small tiles of an image) at a time. If you have Colab Pro then also select "High-RAM" in the "Runtime shape" menu to avoid these limitations.

2. Although we set up a package folder to try and limit the amount of installing we need to do every time we open a colab session, some packages don't play well with this and need to be installed each time. This is why we pip install some packages each time we start a session by running the first code cell (you can run a cell by clicking on the play button or using shift+return).

3. After installing these packages we import a few basic packages and add the path to the "packages" folder to the system so it can load the packages we have saved on google drive.

4. The next cell is where you input paths and setting for running deepcell. here is an overview of each:
   - **TIFS:** here we use glob to get a list of all image paths (images need to be in tif format) you want to run deepcell on.
   - **NucleusChannel:** This is the channel of your image that contains the nuclei you want to segment. Input 0 if you do not want to segment nuclei.
   - **CytoplasmChannel:** This is the channel of your image that contains the cytoplasm you want to segment. Input 0 if you do not want to segment the cytoplasm.
   - **objective:** This is the objective on the microscope used to take the images you are processing. The model uses this information to understand how many um each pixel is for a given image. Note that the higher the magnification used to take the image the larger image/tileSize can be processed at once. as input here you can just say the objective name like '10x' or '20x', however, this assumes these images have been taken using the Shaffer Lab scope. If you used another microscope then you will need to go into the 'DeepTileFunc.py' and change the um per pixel value for each objective. Finally, I have optimized this parameter for large scans of nuclei using a 10x objective on the Shaffer Lab scope. If this is the application you are using this funtion for I suggest you use '10x_fast' as input here.
   - **algorithm:** This selects which model you want to use to segment your cells. Most of the time I used the algoritm trained on tissue data by inputing 'tissue' even if I am analyzing cells on a plate. You can also try using a model trained on tissue cultured cells by entering 'TC'. Finally you want to try a different model you can try using cellpose by entering 'cellpose'.
   - **compartment:** Enter which compartment of the cell you would like to segment. For the nucleus enter 'nuclear' for the cytoplasm enter 'cytoplasm'. If you want to segment both the nucleus and the cytoplasm I suggest using the option 'nuc_cyto' for the best results, but you can also try 'both'(both is not an option when using the cellpose algorithm).
   - **diameter:** This parameter is only relevent if you are using cellpose as your algorithm. This input should be what you expect your average cell size to be. If you are unsure you can enter None and it will try and estimate it. If you get bad results with segmentation you may want to try a few different diameters.
   - **tileSize:** Some images are too big for the deepcell model to take in so we need to break the image up into tiles. The max tile size you can input depends on the hardware you are running this funtion on, and on the objective used to take the image. One thing not to do is enter a tile size much bigger than your actual image size as this will just waste resources. With google Colab Pro to look at 10x images with the '10x_fast' objective I use 10000 as my tile size. you will have to do some trial and error to find the optimal tile size for your image.
   - **Well:** If the image you have contains the boundary of a well the cell segmenting algorithm may call nuclei on the bright well boundary and outside the well. If you set this parameter to TRUE, an algorithm will try and find the edge of the well and then delete all masks outside the well boundary. If there is no well boundary or you do not want this functionality input FALSE.
  
     ### **More Advanced settings:**
   - **DeepCellBatch:** This defines how many small sections of a tile deepcell can process in parallel, the more GPU you have the higher the number you can use here.
   - **DeepTileBatch:** This defines how many tiles are given to deepcell at any given time, more tiles at a time let you run more tiles in parallel. I have found that this number is limited by system RAM. The more RAM you have the higher you can make this number.
          
5. Once you have entered all these parameters run the code cell to save them all and load in the RunDeepTile function.

6. Finally run the "run segmentation" code block which will segment all files in the TIFS list. The mask files will be output in the same directory as each input image.
