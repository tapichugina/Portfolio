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



def tracking_objects():
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
    viz_trajectories(images_dict[fname]["img"],clean_tracks,