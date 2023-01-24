from ij import IJ
from ij.io import FileSaver
import os

#######################################################
###### Preprocessing
#######################################################
import os
top='/../Motility_27.10.2020/results/Traj_Overlay'
for root, dirs, files in os.walk(top, topdown=False):
    for name in dirs:
    	if (name!='.ipynb_checkpoints'):
        	print os.path.join(root, name)
	        folder_path=os.path.join(root, name)
	        IJ.run("Image Sequence...", "open={} onvert_to_rgb sort".format(folder_path))
	        imp = IJ.getImage()
	        IJ.saveAs(imp,"PNG", "{}/{}_TRAJ_OVERLAY.png".format(top,name))
	        imp.close()

