
'''
List of the measurements

Geometric

centroid
major_axis_length
minor_axis_length
orientation. Angle between the 0th axis (rows) and the major axis of the ellipse that has the same second moments as the region, ranging from -pi/2 to pi/2 counter-clockwise.
area
perimeter
eccentricity. Eccentricity of the ellipse that has the same second-moments as the region. The eccentricity is the ratio of the focal distance (distance between focal points) over the major axis length. The value is in the interval [0,1] When it is 0, the ellipse becomes a circle.
bbox
compactness. 4pi for the circle, 16 for the square
circularity. 1 for the circle ( it is maximum value and pi/4 for the square)
Intensity

min_intensity
mean_intensity
max_intensity
contrast
Local peaks within labeled region

peaks
is_peak (False- no peaks were found, True - several peaks were found)
'''


import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib

import skimage.io as io
from skimage import util

from glob import glob
from skimage import measure
from skimage.feature import peak_local_max
from skimage.segmentation import clear_border


def props_measurement(images_binary,images):
    
    total_result_df=pd.DataFrame()
    for frame in range(images.shape[0]):
        label_image = measure.label(images_binary[frame])
        
        ## measurements
        props = measure.regionprops_table(label_image,images[frame],properties=
                                      ['label', 
                                       'centroid',
                                       'major_axis_length',
                                       'minor_axis_length',
                                       'orientation',
                                       'area',
                                       'perimeter',
                                       'eccentricity',
                                       'bbox',])
        result_df=pd.DataFrame(props)
        
        # additional non-standart measurements
        result_df["frame"]=frame
        
        # intensity
        result_df=intensity_measurements(result_df,images[frame],images_binary[frame])
        result_df["compactness"]=result_df['perimeter']**2/result_df['area']
        result_df["circularity"]=4*np.pi*result_df['area']/result_df['perimeter']**2
        result_df["contrast"]=(result_df['max_intensity']-result_df['min_intensity'])/(result_df['max_intensity']+result_df['min_intensity'])
        

        total_result_df=pd.concat([total_result_df,result_df])
        
    total_result_df.reset_index(inplace=True)
    
    
    # local peaks
    coordinats,is_peaks=local_maximum_measurement(total_result_df,images)
    total_result_df['peaks']=coordinats
    total_result_df['is_peaks']=is_peaks
        
    return total_result_df

def intensity_measurements(df,img,img_binary):
    """calculate min, mean, max of the intensity within each segmented object
    Parameters
    ----------
    df : data frame with object position coordinats
    img : original image
    imt_binary: segmented img
    
    Returns
    -------
    data frame with added min,mean, max columns
    """
    
    max_intensity=[]
    mean_intensity=[]
    min_intensity=[]

                     
    for id in df.index:
        frame=df.loc[id,'frame']
        props=df.loc[id,:]

        min_row,min_col,max_row,max_col=props.loc["bbox-0":"bbox-3"].values.astype(int)
        region=img[min_row:max_row,min_col:max_col]
        region_binary=img_binary[min_row:max_row,min_col:max_col]
       
        # intensity measurement within segmented object
        max_intensity.append(np.max(region[region_binary==255]))
        mean_intensity.append(np.mean(region[region_binary==255]))
        min_intensity.append(np.min(region[region_binary==255]))
        
        # fig,ax=plt.subplots(nrows=1,ncols=3)
        # mask=region_binary==255
        # masked_img=region*mask     
        # ax[0].imshow(region)
        # ax[1].imshow(region_binary)
        # ax[2].imshow(masked_img)
    
    df["max_intensity"]=max_intensity
    df["mean_intensity"]=mean_intensity
    df["min_intensity"]=min_intensity
        
    return  df



