
## Library importation: 

import numpy as np
import scipy.interpolate as inter



### Function that will delete the lines that have zero for Needle_holder and tweezers: 
def delete_zero_lines(data, run, tools):
    if tools.count('scissors'):
        return data[run]
    data_copy = data[run]
    data_copy = data_copy[data_copy[tools[0]+'_x'] != 0  ]
    data_copy = data_copy[data_copy[tools[1]+'_x'] != 0]    
    return data_copy



### Very useful function for executing the interpolation: 

def interpolation(data , run, tools, frequency = 120):
    Interpole = {}
    tool_movement = {}
    data_copy = data[run].copy()
    # Create the interpolation function 
    for tool in tools:
        Interpole[tool] = inter.interp1d( data_copy['relative_time'], data_copy[[tool+'_x',tool+'_y', tool+'_z']] , axis = 0 )
        # we will create our time vector: 
        time_step = 1/frequency
        time_vector = np.arange(data_copy['relative_time'].min(),data_copy['relative_time'].max(),time_step )
        ## Create the interpoled functions to be able to execute the analysis of the movement :
        tool_movement[tool] = Interpole[tool](time_vector)
    return time_vector, tool_movement



### The following function will be useful to get the time of execution of each task

def excecution_time(data, list_runs,black_list):
    times = {}
    for run in list_runs:
        if not black_list.count(run):
            times[run] = data[run]['relative_time'].max()-data[run]['relative_time'].min()
    mean_execution_time = sum(times.values())/len(times)
    print(f'This is the mean execution time for the task of one suture point {mean_execution_time} in seconds , {mean_execution_time/60} in minutes ')
    
    return times, mean_execution_time



def Central_differentiation(Data, time_step, order = 'first'):
    
    ### We will loose the first points to be able to execute the differentiation 
    
    f_xt_1 = Data[:-2]
    f_xt_2 = Data[2:]
    df_dt = (f_xt_2-f_xt_1)/(2*time_step)
    if order == 'first':  
        print('The first order derivation was computed')
        return df_dt
    if order == 'Second':
        print('The second order derivation was computed')
        f_xt_1 = df_dt[:-2]
        f_xt_2 = df_dt[2:]
        df_d2t = (f_xt_2 - f_xt_1)/(2*time_step)
        
        return df_d2t
    
    

    
## This function will execute the Euclidien distance of our signal 

def distance_3d(signal, type = 'euclidien'):
    
    if type == 'euclidien':
        distance = np.sqrt(signal[:,0]**2 + signal[:,1]**2 + signal[:,2]**2)
    
    
    return distance



# The function below helps to numérically integrate back the signal in its input
def trap_integration(time_vector, signal):
    ##Here we will compute back the movement by trapezoidale integration:
    n = np.shape(time_vector)[0]
    h = (time_vector[-1]-time_vector[0])/n
    #print(1/h, h)
    
    integral = h * (signal[:-1] + signal[1:])
    
    return integral
    
    
    
    