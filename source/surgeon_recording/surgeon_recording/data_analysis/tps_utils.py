from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.signal as sp
from scipy.fft import fft
import os
from scipy import interpolate
import time 


def clean_tps(mydata_path):
    # Input : raw TPS signal
    # Output : Format mydata to structured panda DataFrame 

    rawmydataDF = pd.read_csv(mydata_path, header=0)
    
    # Convert channels labels to finger labels
    column_list = list(rawmydataDF.columns) # rawmydataDF.columns.values.tolist()
    finger_list = channel_to_finger_label()

    # Create new DF with correct labels
    column_names = ['relative time', 'absolute time'] #, 'absolute date time']
    column_names.extend(finger_list)
    cleanDF = pd.DataFrame(columns=column_names)

    # Get value for correct channel and write to new DF
    i = 0 
    for column_name in column_list[15:]:
        # copy to new DF
        cleanDF[finger_list[i]] = rawmydataDF[column_name]
        i+=1

    # Reset relativ etime to mathc aboslute 
    cleanDF['relative time'] = (rawmydataDF[' absolute_time'] - rawmydataDF[' absolute_time'].iloc[0])* 1e-3

    # Copy absolute time
    cleanDF['absolute time'] = rawmydataDF[' absolute_time']
    

    # Print starting absolute time
    # get_starting_time(cleanDF)

    # Complicates matter smore than anything, kept comented for possible later use to ease readability
    # Convert absolute time to datetime format
    # for i in range(len(rawmydataDF.index)):
    #     cleanDF['absolute datetime'].iloc[i] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rawmydataDF['absolute time [s]'].iloc[i]))
    
    return cleanDF


def get_starting_time(cleanDF):
    # Get starting time from TPS --> WARNING : given in ms, need to convert 
    start_time_in_secs = cleanDF['absolute time'].iloc[0]*1e-3
    
    print("Starting time of TPS recording :", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_in_secs )) )

    return start_time_in_secs

# TODO : adapt for raw TPS 
def interpolate_clean_tps(cleanDF, start_idx=0, sr=1500, nb_rec_channels=6):
    # Input : Clean emg DF, index at which to start interpolation (remove first points if needed), Sampling rate of emg
    # Output : interp emg DF with relative time an dinterpolated data

    # Create interpolated DF
    labels_list = cleanDF.columns.values.tolist()[2:nb_rec_channels+2]
    column_names = ['relative time', 'absolute time']
    column_names.extend(labels_list)
    interpDF = pd.DataFrame(columns=column_names)

    # Create time array
    start_time = cleanDF['absolute time'].iloc[start_idx]
    end_time =  cleanDF['absolute time'].iloc[-1]
    duration = end_time - start_time
    nb_samples = int(sr*duration)
    time_array = np.linspace(cleanDF['relative time'][start_idx], duration, nb_samples)

    # Add time arrays to interpDF
    interpDF['relative time'] = time_array
    interpDF['absolute time'] = time_array + cleanDF['absolute time'].iloc[0] # TODO : should be start_time here, but this creates offset, why ??

    # Get orginal time array form recording
    rec_time_array = np.linspace(cleanDF['relative time'][start_idx], duration, len(cleanDF.index[start_idx:]))
    # rec_time_array = cleanDF['relative time'][start_idx:]

    # Interpolate par channel
    for label in labels_list:
        interp_function = interpolate.InterpolatedUnivariateSpline(np.array(rec_time_array), cleanDF[label].iloc[start_idx:])
        interpDF[label] = interp_function(time_array)

    return interpDF


def plot_tps_csv(mydata_path, title_str='Calibrated TPS', nb_rec_channels=6 ):
    # Plots raw data from mydata.csv 

    mydataDF = pd.read_csv(mydata_path, header=0)
 
    # Get labels
    labels=mydataDF.columns.values.tolist()[15:]
    
    #MATPLOTLIB
    fig, ax = plt.subplots(nb_rec_channels,1, sharex=True,figsize=(30,20))
    
    fig.suptitle(title_str)
    fig.supylabel('TPS [N]')
    # plt.subplots_adjust(top=0.95,
    #                     bottom=0.04,
    #                     left=0.055,
    #                     right=0.995,
    #                     hspace=0.4,
    #                     wspace=0.2)
    plt.xlabel('time [s]')
    
    for ch_nbr in range(1, nb_rec_channels+1):
        # ax[ch_nbr-1].set_ylabel('ch' + str(ch_nbr))
        ax[ch_nbr-1].plot(mydataDF[' relative_time'].to_numpy()*1e-3, mydataDF[labels[ch_nbr-1]].to_numpy())
        ax[ch_nbr-1].set_title(channel_to_finger_label()[ch_nbr-1], fontsize = 6)
        ax[ch_nbr-1].tick_params(axis='x', labelsize=6)
        ax[ch_nbr-1].tick_params(axis='y', labelsize=6)
         
    plt.show()
    

def plot_tpsDF(DF, time_for_plot='relative time', title_str='Clean TPS', nb_rec_channels=6):
    # Input must be reformatted DF of emg, time_for_plot one of ['relative time', 'absolute time']
    # Plots all channels from emgDF

    # Get labels
    labels=DF.columns.values.tolist()[2:nb_rec_channels+2]
    
    fig, ax = plt.subplots(nb_rec_channels,1, sharex=True,figsize=(30,20))
    
    fig.suptitle(title_str)
    fig.supylabel('TPS [N]')
    plt.subplots_adjust(top=0.95,
                        bottom=0.04,
                        left=0.055,
                        right=0.995,
                        hspace=0.4,
                        wspace=0.2)
    plt.xlim([DF[time_for_plot].to_numpy()[0], DF[time_for_plot].to_numpy()[-1]])
    plt.xlabel('time [s]')
     
    for i in range(len(labels)):
        # ax[i].set_ylabel('ch' + str(i+1))
        ax[i].plot(DF[time_for_plot].to_numpy(), DF[labels[i]].to_numpy())
        ax[i].set_title(labels[i], fontsize = 6)
        ax[i].tick_params(axis='x', labelsize=6)
        ax[i].tick_params(axis='y', labelsize=6)
          
    # plt.show()

def channel_to_finger_label():
    # Returns corresponding muscle for plot label depending on emg placement
    finger_list = [
    'Left index finger',
    'Left middle finger',
    'Left Thumb',
    'Right Thumb',
    'Right Index',
    'Right middle finger']

    return finger_list

def get_streaming_id():
    
    stream_id_list = [1,0,2,7,8,6]
    return stream_id_list

def main():
    # Example of function calls 
    # TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init

    # Path to mydata.csv folder
    data_dir = '/home/maxime/Workspace/surgeon_recording/exp_data/13022023/1/1/'
    path_to_tps = data_dir + 'TPS_calibrated.csv'

    # plot_mydata_raw(path_to_mydata)

    cleanDF = clean_tps(path_to_tps)   
    # plot_emgDF(cleanemgDF)
    print(f"Recording duration : {cleanDF['relative time'].iloc[-1]:.2f} s" )

    # Might not be necessary for data analysis
    # interpDF = interpolate_clean_tps(cleanDF, sr=500, start_idx=50)
    plot_tpsDF(cleanDF, title_str='Calibrated TPS', time_for_plot='relative time', nb_rec_channels=6)

    return


if __name__ == '__main__':
    main()