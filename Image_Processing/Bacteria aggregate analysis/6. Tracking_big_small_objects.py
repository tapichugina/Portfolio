#!/usr/bin/env python
# coding: utf-8

# In[14]:


import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

import skimage.io as io
from skimage import util

from glob import glob
import trackpy

import ast


# In[15]:


def viz_trajectories(images_binary,clean_tracks,tracks_folder):
    """
    viz all trajectories on the images sequence
    """

    for frame in range(images_binary.shape[0]):
        fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(20,20))
        # show image
        ax.imshow(images_binary[frame],cmap='gray')
        ax.axis('off')
        
        # viz tracks
        tracks_frame=tracks[tracks['frame']<=frame]
        for id,group in tracks_frame.groupby("particle"):
            ax.plot(group['x'],group['y'],lw=2,color='red')
            
        
        fig.savefig(tracks_folder+"/im_traj_"+str(frame)+".png",bbox_inches='tight')


# ## Read data

# In[16]:


file_list=glob("../data/*_Dark_prepared.tif")
images_dict={}
for file_name in file_list:
    images_prepared=io.imread(file_name)
    binary_file=file_name.split(".tif")[0]+'_segmented'+'.tif'
    images_binary=io.imread(binary_file)
    img_dict={"img":images_prepared,"binary":images_binary}
    file_prefix=os.path.split(file_name)[1].split('.')[0].split("_prepared")[0]
    images_dict[file_prefix]=img_dict


# In[18]:


images_dict.keys()


# In[11]:


Data=pd.read_csv("../data/Measurements.csv")


# ## Tracking all objects

# In[12]:


for fname, df in Data.groupby("file_name"):
    print(fname)
    
    ##=============================##
    ## tracking                    ##
    ##=============================##
    df=df.rename(columns={'centroid-1':"x",'centroid-0':"y"})
    tracks = trackpy.link_df(df,search_range=35.5)

    # filter out trajectories less than 5 frames
    clean_tracks = trackpy.filter_stubs(tracks,threshold=5)
    clean_tracks.to_csv("../data/"+"tracks_overlay_id_{}.csv".format(fname))
    
    # plot traj overlays
    tracks_folder='../data/'+fname+"_tracks"
    os.mkdir(tracks_folder)
    viz_trajectories(images_dict[fname]["img"],clean_tracks,tracks_folder)


# ## Tracking big objects

# In[13]:


for fname, df in Data.groupby("file_name"):
    print(fname)
   
    df=df.rename(columns={'centroid-1':"x",'centroid-0':"y"})

    # tracking only big objects
    df_big=df[df['area']>500]
    
    # tracking
    tracks = trackpy.link_df(df_big,search_range=35.5)
    
    # filter out trajectories less than 5 frames
    clean_tracks = trackpy.filter_stubs(tracks,threshold=5)
    clean_tracks.to_csv("../data/"+"tracks_overlay_id_{}_big.csv".format(fname))
    
    # save trajectories overlays
    tracks_folder='../data/'+fname+"_tracks_big"
    os.mkdir(tracks_folder)
    viz_trajectories(images_dict[fname]["img"],clean_tracks,tracks_folder)

