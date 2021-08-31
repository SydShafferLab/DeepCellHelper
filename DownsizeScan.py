import tifffile
import glob

#downsize scans if needed for DeepCell Processing
TIFS = glob.glob('/Volumes/gharmHD1/20210917_DensityRep4/**/Stitch_tif/*.tif',recursive=True)

for tif in TIFS:
    img = tifffile.imread(tif)
    img = img[0:10000,0:10000]
    spltpath = tif.split('Stitch_tif')
    outdir = str(spltpath[0]+'Stitch_tif/DownSized')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    outpath = str(outdir+spltpath[1])
    tifffile.imwrite(outpath,img)
