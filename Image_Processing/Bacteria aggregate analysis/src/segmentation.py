#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: pichugina
"""

import numpy as np
import pandas as pd
import os

import skimage.io as io
from skimage import util

from glob import glob
from skimage import measure
from skimage.segmentation import clear_border


def outsu_threshold(file_name):
    from skimage.filters import threshold_otsu
    """
    create list of images that used for multiprocessing
    """ 
    
    folder_to_save=os.path.split(file_name)[0]
    file_prefix=os.path.split(file_name)[1].split('.')[0]
    images_prepared=io.imread(file_name)
    
    images_binary=np.zeros_like(images_prepared,dtype=np.ubyte)
    threshold=threshold_otsu(images_prepared)
    images_binary[images_prepared>threshold]=255
    
    ### clear objects toutching the boader
    for frame in range(images_binary.shape[0]):
        images_binary[frame]=clear_border(images_binary[frame])
    
    io.imsave(os.path.join(folder_to_save,file_prefix+"_segmented.tif"),images_binary)
    img_dict={"img":images_prepared,"binary":images_binary}
    
    return img_dict,file_prefix,threshold