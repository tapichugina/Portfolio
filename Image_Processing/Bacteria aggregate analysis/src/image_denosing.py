#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smmoth image by small gaussian (1.5px)kernel
Substract background. Background estimated by large gauss kernel (150 px)
We saved intermediate images:

denoised -small gauss kernel
background - large gauss kernel
prepared -final denoised image

@author: pichugina
"""

import numpy as np
import pandas as pd
import os


import skimage.io as io
from skimage import util
from skimage.filters import gaussian

from glob import glob

def image_denoising(img):
    """
    Denoised img 
    Small (1.5px) gauss kernel 
    Substract background. Background estimated by large gauss kernel (150 px)
    """
    # denoised
    denoised=gaussian(img,1.5)
    # substract background
    background=gaussian(img,150)
    img_prepared=denoised-background
    return denoised,background,img_prepared

def images_list(file_name):
    """
    create list of images that used for multiprocessing
    """ 
    
    folder_to_save=os.path.split(file_name)[0]
    file_prefix=os.path.split(file_name)[1].split('.')[0]
    img_stack=io.imread(file_name)
    
    # make a list with images for multiprocessor
    img_list=[img_stack[i] for i in range(img_stack.shape[0])]
    return img_list,folder_to_save,file_prefix

def save_results_after_multiprocess(denoising_results,folder_to_save,file_prefix):
    """
    saved results of multiprocessing
    """
    n_frames=len(denoising_results)
    rows,cols=denoising_results[0][0].shape
    
    denoised=np.zeros((n_frames,rows,cols),dtype="float32")
    background=np.zeros((n_frames,rows,cols),dtype="float32")
    img_prepared=np.zeros((n_frames,rows,cols),dtype="float32")
    
    for frame in range(n_frames):
        denoised[frame],background[frame],img_prepared[frame]=denoising_results[frame]
        
    io.imsave(os.path.join(folder_to_save,file_prefix+"_denoised.tif"),denoised)
    io.imsave(os.path.join(folder_to_save,file_prefix+"_background.tif"),background)
    io.imsave(os.path.join(folder_to_save,file_prefix+"_prep