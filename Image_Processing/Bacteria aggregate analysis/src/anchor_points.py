
from glob import glob
import trackpy

import ast
from ipywidgets import interact, widgets


# import code from the src
### import code from src folder


from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error


def object_anchor_area(traj,binary_images,ax):
    """ calculate overlapped area i.e sum of pixels that are stay the same across time """
    
    min_row,min_col=np.min(traj.loc[:,'bbox-0':'bbox-1'])
    max_row,max_col=np.max(traj.loc[:,'bbox-2':'bbox-3'])
    
    time_start=np.min(traj.frame)
    time_end=np.max(traj.frame)
    binary_img_region=binary_images[time_start:time_end,min_row:max_row,min_col:max_col]
    
    # calculate anchor mask
    anchor_points=np.zeros_like(binary_img_region[0],dtype=np.int32)
    anchor_points=np.sum(binary_img_region,axis=0)
    anchor_mask=anchor_points>=(255*(binary_img_region.shape[0]))
    ax.imshow(anchor_points,vmin=255,vmax=np.max(anchor_points),cmap='plasma')
    
    ax.axis("off")
    
    # overlap
    sum_overlap_px=np.sum(anchor_mask)
    if np.sum(anchor_mask)>0:
        ax.set_title("file_id={} \n particle_id={} \n anchored=True \n overlapped_area={:.2f}".format(traj["file_name"].iloc[0],traj["particle"].iloc[0],sum_overlap_px/np.mean(traj.area)))
    else:
        ax.set_title("{} \n anchored=False".format(traj["particle"].iloc[0]))
    #print(traj.particle.iloc[0],np.mean(traj.area),sum_overlap_px)
    
    result={'particle':traj.particle.iloc[0],
            'mean_area':np.mean(traj.area),
            'overlapped_area':sum_overlap_px,
            'overlapped_area_ratio':sum_overlap_px/np.mean(traj.area),
            'traj_len':traj.shape[0]}
    
    return result 