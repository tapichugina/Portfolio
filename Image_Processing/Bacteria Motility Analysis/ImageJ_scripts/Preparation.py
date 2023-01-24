from ij import IJ, ImagePlus
from ij.io import FileSaver
#-----------------------------
### Open and Prepare Image for Tracking
##-----------------------------
# Get currently selected image
#imp = WindowManager.getCurrentImage()

FOLDER_TO_SAVE='../Motility_27.10.2020/'
ORIG_FILE_NAME='../Motility_27.10.2020/Data/Psa_KB_KB_1_cziPsa_KB_KB_1_czi_40003.ome.tiff_ORIG.tiff'
PREP_FILE_NAME=FOLDER_TO_SAVE+ORIG_FILE_NAME.split('/')[-1].split('ORIG.tiff')[0]+'3_PREP.tiff'

#file_full_name="/Users/pichugina/Work/Data_Analysis/Capillary/Motility_27.10.2020/Data/"+fileName.split('.tiff')[0]+"_PREP.tiff"
imp=ImagePlus('../Motility_27.10.2020/Data/Psa_KB_KB_1_cziPsa_KB_KB_1_czi_40003.ome.tiff_ORIG.tiff')

# Substruct Background
IJ.run(imp,"Subtract Background...", "rolling=10 stack");
# Denoise
IJ.run(imp, "Median...", "radius=3 stack")
fs=FileSaver(imp)
fs.saveAsTiff(PREP_FILE_NAME)    