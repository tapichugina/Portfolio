#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 14:47:35 2020

@author: pichugina
"""
import numpy as np

def displacement(traj):
    '''
    displacement per frame
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        dr: step displacement vector
        mod_r: module of displacement vector
    '''
    traj=traj.sort_values(by='frame')
    ## dx, total traveled distance, end to end distance
    dr=np.diff(traj[["x","y"]],axis=0)
    mod_dr = np.sqrt(dr[:,0]**2+dr[:,1]**2)

    return dr,mod_dr

def total_displacement(traj):
    '''
    total displacement
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        return displacement
    '''
    traj=traj.sort_values(by='frame')
    dr,mod_dr=displacement(traj)
    return sum(mod_dr)

def end_to_end_displacement(traj):
    '''
    end to end trajectory distance
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        return   end to end displacement
    '''
    traj=traj.sort_values(by='frame')
    trajXY=traj[["x","y"]]
    d_end_to_end=np.sqrt(np.sum((trajXY.iloc[-1]-trajXY.iloc[0])**2))
    
    return d_end_to_end


def max_distance_origin(traj):
    '''
    max distance to origin (start of trajectory) 
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        max distance to origin
    '''
    traj=traj.sort_values(by='frame')
    trajXY=traj[["x","y"]]
    delta_start=np.sqrt(np.sum((trajXY-trajXY.iloc[0])**2,axis=1))
    return np.max(delta_start)

def persistence(traj):
    '''
    persistence=end_end_displacement/total_displacement
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        persistence
    '''
    traj=traj.sort_values(by='frame')
    TD=total_displacement(traj)
    
    # avoid division by 0
    if TD>0.5:
        return end_to_end_displacement(traj)/total_displacement(traj)
    else:
        return np.nan
    
def outreach_ratio(traj):
    '''
    outreach_ratio=max_distance_origin/total_displacement
    Parameters:
        -----------------------------------------------------------------------
        traj: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        outreach_ratio
    '''
    traj=traj.sort_values(by='frame')
    TD=total_displacement(traj)
    MaxDist=max_distance_origin(traj)
    
    # avoid division by 0
    if TD>0.5:
        return MaxDist/TD
    else:
        return np.nan

def med_speed(traj):
    '''
    maximum speed calculation
    
    Parameters:
        -----------------------------------------------------------------------
        traj: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        max_speed
    '''
    dr,mod_dr=displacement(traj)
    median_speed=np.median(mod_dr)
    return median_speed

def std_speed(traj):
    '''
    maximum speed calculation
    
    Parameters:
        -----------------------------------------------------------------------
        traj: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        max_speed
    '''
    dr,mod_dr=displacement(traj)
    std_s=np.std(mod_dr)
    return std_s

def MSD(traj):
    '''
    calculate MSD for the track
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        MSD
    '''
    dr,mod_dr=displacement(traj)
    MSD=np.sqrt(np.mean(dr[:,0]**2+dr[:,1]**2))
    return MSD

def global_angle(traj):
    '''
    calculate angles for track displacements relative to img coordinats system
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        array with angles in degree
    '''
    traj=traj.sort_values(by='frame')
    dr,mod_dr=displacement(traj)
    # acrtan2(dy,dr)
    list_angle=np.arctan2(dr[:,1],dr[:,0]) * 180 / np.pi
    return list_angle

    
def relative_angle(traj):
    '''
    calculate relative angles for tracks displacements
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        array with angles in degree
    '''
    traj=traj.sort_values(by='frame')
    
    t_duration=traj.shape[0]
    dr,mod_dr=displacement(traj)
    list_angle=[]
    for k in range(t_duration-2):
        cos_thetha=np.sum(dr[k]*dr[k+1])/mod_dr[k]/mod_dr[k+1]
        list_angle.append(np.arccos(cos_thetha)*180/np.pi)
        #print(k,k+1,cos_thetha)
    
    return list_angle

def med_relative_angle(traj):
    '''
    calculate median of relative angles for tracks displacements
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        median relative angle
    '''
    list_angle=relative_angle(traj)
    median_rel_angle=np.nanmedian(list_angle)
    return median_rel_angle

def std_relative_angle(traj):
    '''
    calculate median of relative angles for tracks displacements
    Parameters:
        -----------------------------------------------------------------------
        tracks: trajecrory date frame
    Returns:
        -----------------------------------------------------------------------
        median relative angle
    '''
    list_angle=relative_angle(traj)
    std_angle=np.nanstd(list_angle)
    return std_angle
    