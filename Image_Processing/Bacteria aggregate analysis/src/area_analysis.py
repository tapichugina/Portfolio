import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib

from sklearn import linear_model
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error



import sys
sys.path.append('../src/')
import chow_test_v

###### Tests ######################
# test one trajectory plot
# traj=tracks[tracks['particle']==4]
# window=5
# scale=1.96


# fig,ax=plt.subplots(figsize=(15,5))
# anomalies=area_analysis.simple_anomaly_detector(traj,ax,5,1.96,plot_flag=True)
# print(anomalies)
# result=area_analysis.fit_area_with_anomalies(traj,anomalies,ax)



# single experiment
# file_prefix="43121_Dark"
# tracks=images_dict[file_prefix]["tracks_big"]
# images=images_dict[file_prefix]["img"]
# binary=images_dict[file_prefix]["binary"]


# Ngroups=tracks.groupby('particle').ngroups
# Nrows=np.int(np.ceil(Ngroups/5))

# sns.set(font_scale=2)
# fig,ax=plt.subplots(nrows=Nrows,ncols=5,figsize=(40,Nrows*5))
# axx=ax.ravel()

# counter=0
# Area=pd.DataFrame()
# for id, traj in tracks.groupby('particle'):
#     df_result=area_analysis.area_analysis(traj,axx[counter])
#     #print(df_result)
#     Area=pd.concat([Area,df_result])
#     counter=counter+1
# Area=Area.reset_index()


def area_analysis(traj,ax):
    """
    linear regression
    input: trajectories 
    output: dictionaries
            "particle"- particle id
            "traj_len"-len of the trajectories
            "slope", - slope of the linear regression
            "intersept",
            "MSE":mean_squared_error,
            "R2":r2_score
    """
    traj=traj.sort_values('frame')
    particle=traj['particle'].values[0]
    time=traj['frame']
    traj_len=time.shape[0]
    area=traj['area']
    
    # detect anomalies
    anomalies=simple_anomaly_detector(traj,ax,5,1.96,plot_flag=True)

    # linear regression
    if len(anomalies)==0:
        result,area_predict=linear_regression(time,area)
        result["particle"]=traj["particle"].values[0]
        result["interval_counter"]=1
        result["len"]=traj_len
        ax.plot(time, area, color='black',label="data")
        ax.plot(time, area_predict, color='red', linewidth=3,label="fit LinearRegression")
        df_result=pd.DataFrame([result])
    else:
        result=fit_area_with_anomalies(traj,anomalies,ax)
        df_result=pd.DataFrame(result)

    
    return df_result
        
        



def simple_anomaly_detector(traj,ax,window=5,scale=1.96,plot_flag=False):
    """
    simple anomaly detector
    """
    break_id=[]
    
    # set minimal size of trajectories for anomaly detection
    if (traj.shape[0]>15):
        tt=traj.copy()
        tt=tt.sort_values('frame')
        tt=tt.set_index('frame')
        tt=tt['area']
    
        
        # find candidates for anomaly
        rolling_mean = tt.rolling(window=5).mean()
        mae=mean_absolute_error(tt[window:], rolling_mean[window:])
        deviation = np.std(tt[window:] - rolling_mean[window:])
        lower_bond = rolling_mean - (mae + scale * deviation)
        upper_bond = rolling_mean + (mae + scale * deviation)
        
        anomalies=pd.Series('NA',index=tt.index)
        anomalies_lower = tt[tt<lower_bond]
        anomalies_upper = tt[tt>upper_bond]
       
        if (plot_flag==True):
            # plot anomalies
            #fig,ax=plt.subplots(figsize=(8,5))
            ax.set_title("trajectory id = {}".format(traj["particle"].values[0]))
            ax.plot(rolling_mean, "g",label="Rolling mean trend") # label="Rolling mean trend"
            ax.plot(tt, "black", label="data")
            ax.plot(upper_bond, "r--",label="Upper Bond / Lower Bond") #label="Upper Bond / Lower Bond"
            ax.plot(lower_bond, "r--")
            ax.plot(anomalies_upper, "go", markersize=10,label="anomalies")
            ax.plot(anomalies_lower, "go", markersize=10)
            #ax.legend()
            
        ## chow test

        
        for id in np.hstack([anomalies_upper.index,anomalies_lower]):
            #print(id)
            
            part1=tt[0:id]
            x1=part1.index.values
            y1=part1.values
            #print(part1,x1,y1)
    
            part2=tt[(id+1):]
            x2=part2.index.values
            y2=part2.values
            #print(part2,x2,y2)
            
            if (len(y1)>3)&(len(y2)>3):
                is_break,p_val= chow_test_v.p_value(y1, x1, y2, x2)
                if is_break==1:
                    #print("hear")
                    break_id.append(id)
                    
                    if (plot_flag==True):
                        ax.plot(id,tt.loc[id],"ro", markersize=10,label="anomalies-break")
            


            
    return break_id


def linear_regression(time,prop):
    """
    Linear regression time vs properties
    (could be area,orientation,compactness)
    
    """
    from sklearn import linear_model
    from sklearn.metrics import mean_squared_error, r2_score
    
    # reshape required for LinearRegression
    time=time.values.reshape(-1, 1)
    
    # Create linear regression object
    regr = linear_model.LinearRegression(fit_intercept=True)
    regr.fit(time, prop)
    
    # Make predictions using the testing set
    prop_predict = regr.predict(time)
    
    
    #     # The coefficients
    #     print('Coefficients: \n', regr.coef_)
    #     # The mean squared error
    #     print('Mean squared error: %.2f'% mean_squared_error(area, area_predict))
    #     # The coefficient of determination: 1 is perfect prediction
    #     print('Coefficient of determination: %.2f'% r2_score(area,area_predict))

    # Plot outputs
    result={"slope":regr.coef_[0], 
                   "intersept":regr.intercept_,
                   "MAE":mean_absolute_error(prop,prop_predict),
                   "R2":r2_score(prop,prop_predict)}
    
    return result,prop_predict
   



def fit_area_with_anomalies(traj,anomalies,ax):
    
    ##====================================##
    ##        Select intervals for fit    ##
    ##====================================##
    #the length of the interval should be >5 frames
    
    def check_interval_length(break_intervals,inter):
        if inter.size>5:
            break_intervals.append(inter)
            
    break_intervals=[]
    # start interval
    interval_start=np.arange(0,anomalies[0])
    check_interval_length(break_intervals,interval_start)
    # middel intervals
    for i in range(0,len(anomalies)-1):
        interval=np.arange(anomalies[i]+1,anomalies[i+1])
        check_interval_length(break_intervals,interval)
    # end interval
    interval_end=np.arange(anomalies[-1],traj["particle"].shape[0]+1)
    check_interval_length(break_intervals,interval_end)
    

    
    ##=============================================##
    ##        Fit intervals by linear regression   ##
    ##=============================================##
    Result=[]
    interval_counter=1
    for inter in break_intervals:
        start=inter[0]
        end=inter[-1]
        peace_to_fit=traj[(traj["frame"]>=start)&(traj["frame"]<=end)]
        result,prop_predict=linear_regression(peace_to_fit["frame"],peace_to_fit["area"])
        result["particle"]=traj["particle"].values[0]
        result["interval_counter"]=interval_counter
        result["len"]=peace_to_fit.shape[0]
        Result.append(result)
        interval_counter=interval_counter+1
        ax.plot(peace_to_fit["frame"],prop_predict,color='red',lw=4,label="fit LinearRegression")
        
    return Result