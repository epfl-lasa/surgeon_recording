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

import plotly.io as pio
pio.renderers.default='browser'

def clean_emg(mydata_path, emg_placement, nb_rec_channels=16,clip_upper = 3000):
    # Input : raw EMG signal
    # Output : Format mydata to structured panda DataFrame 

    rawmydataDF = pd.read_csv(mydata_path, sep=';', header=0)
    
    # Convert channels labels to muscle labels
    channel_list = rawmydataDF.columns.values.tolist()[2:nb_rec_channels+2]
    muscle_list = channel_to_muscle_label(emg_placement)

    # Create new DF with correct labels
    column_names = ['relative time', 'absolute time'] #, 'absolute date time']
    column_names.extend(muscle_list)
    cleanDF = pd.DataFrame(columns=column_names)

    # Get absolute value for each channel and write to new DF
    for channel_nbr in range(len(channel_list)):
        # Clip data
        rawmydataDF[channel_list[channel_nbr]].clip(-5000, 5000, inplace=True)
        # copy to new DF
        cleanDF[muscle_list[channel_nbr]] = abs(rawmydataDF[channel_list[channel_nbr]])

    # Convert time array from ms to s
    cleanDF['relative time'] = rawmydataDF['time [ms]'] * 1e-3

    # Copy absolute time
    cleanDF['absolute time'] = rawmydataDF['absolute time [s]']
    
    #Replace values higher than clip_upper by nan 
    cleanDF.clip(upper = clip_upper)
    cleanDF = cleanDF.replace(clip_upper, np.nan)
                
    # Fill NaN with the previous non-NaN value in the same column
    cleanDF.fillna(method = 'ffill', inplace = True)

    # Complicates matter smore than anything, kept comented for possible later use to ease readability
    # Convert absolute time to datetime format
    # for i in range(len(rawmydataDF.index)):
    #     cleanDF['absolute datetime'].iloc[i] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rawmydataDF['absolute time [s]'].iloc[i]))
    
    return cleanDF

def interpolate_clean_emg(cleanDF, start_idx=0, sr=1500, nb_rec_channels=16):
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

def plot_mydata_raw(mydata_path, title_str='Raw EMG', nb_rec_channels=16, ytitle = 'raw EMG n[mV]',  emg_placement = "Jarque-Bou"):
    # Plots raw data from mydata.csv 

    mydataDF = pd.read_csv(mydata_path, sep=';', header=0)
    
    #To delete Unnamed column added at the end 
    mydataDF = mydataDF.loc[:,~mydataDF.columns.str.match("Unnamed")] 

    # Get labels
    labels=mydataDF.columns.values.tolist()[2:nb_rec_channels+2]
    nb_channels = len(labels)
    
    # #PLOTLY
    # # Create figure and plot
    # fig = make_subplots(rows=nb_channels, cols=1, shared_xaxes=True, vertical_spacing=0.02, 
    #                     x_title='Time [ms]', y_title='EMG [mV]', subplot_titles=labels)
    
    # for ch_nbr in range(1, nb_channels+1):
    #     fig.add_trace(go.Scatter(x=mydataDF['time [ms]'], y=mydataDF['ch'+str(ch_nbr)]), row=ch_nbr, col=1)

    # fig.update_layout(height=1500, width=1500, title_text=title_str, showlegend=False)
    
    # fig.show()
    
    #MATPLOTLIB
    fig, ax = plt.subplots(16,1, sharex=True,figsize=(30,20))
    
    fig.suptitle(title_str)
    fig.supylabel(ytitle)
    plt.subplots_adjust(top=0.95,
                        bottom=0.04,
                        left=0.055,
                        right=0.995,
                        hspace=0.4,
                        wspace=0.2)
    plt.xlabel('time [ms]')
    plt.ylabel('EMG [mV]')
    
    for ch_nbr in range(1, nb_channels+1):
        ax[ch_nbr-1].set_ylabel('ch' + str(ch_nbr))
        ax[ch_nbr-1].plot(mydataDF['time [ms]'].to_numpy(), mydataDF['ch'+str(ch_nbr)].to_numpy())
        ax[ch_nbr-1].set_title(channel_to_muscle_label( emg_placement)[ch_nbr-1], fontsize = 6)
        ax[ch_nbr-1].tick_params(axis='x', labelsize=6)
        ax[ch_nbr-1].tick_params(axis='y', labelsize=6)
         
    plt.show()
    

def plot_emgDF(emgDF, time_for_plot='relative time', title_str='Clean EMG', ytitle = 'EMG normalized by MVIC', nb_rec_channels=16):
    # Input must be reformatted DF of emg, time_for_plot one of ['relative time', 'absolute time']
    # Plots all channels from emgDF

    # Get labels
    labels=emgDF.columns.values.tolist()[2:nb_rec_channels+2]
    
    # #PLOTLY
    # # Create figure and plot
    # fig = make_subplots(rows=len(labels), cols=1, shared_xaxes=True, vertical_spacing=0.02,
    #                     x_title='Time [s]', y_title= ytitle, subplot_titles=labels)
    
    # for i in range(len(labels)):
    #     fig.add_trace(go.Scatter(x=emgDF[time_for_plot], y=emgDF[labels[i]]), row=i+1, col=1)

    # fig.update_layout(height=1500, width=1500, title_text=title_str, showlegend=False)
    # fig.update_annotations(font_size=14)
    
    # fig.show()
    
     #MATPLOTLIB
    fig, ax = plt.subplots(16,1, sharex=True,figsize=(30,20))
    
    fig.suptitle(title_str)
    fig.supylabel(ytitle)
    plt.subplots_adjust(top=0.95,
                        bottom=0.04,
                        left=0.055,
                        right=0.995,
                        hspace=0.4,
                        wspace=0.2)
    plt.xlim([0, emgDF[time_for_plot].to_numpy()[-1]])
    plt.xlabel('time [s]')
    
     
    for i in range(len(labels)):
        ax[i].set_ylabel('ch' + str(i+1))
        ax[i].plot(emgDF[time_for_plot].to_numpy(), emgDF[labels[i]].to_numpy())
        ax[i].set_title(labels[i], fontsize = 6)
        ax[i].tick_params(axis='x', labelsize=6)
        ax[i].tick_params(axis='y', labelsize=6)
          
    plt.show()

def channel_to_muscle_label(emg_placement):
    # Returns corresponding muscle for plot label depending on emg placement

    if emg_placement == 'Protocol':
        muscle_list = [
        'Abductor Pollicis brevis R',
        'Flexor Capri Radialis R',
        'Flexor Carpi Ulnaris R',
        'Extensor Pollicis Brevis R',
        'Extensor Digitorum Communis R',
        'Extensor Carpi Ulnaris R',
        'Biceps Brachii R',
        'Triceps Brachii R',
        'Abductor Pollicis brevis L',
        'Flexor Capri Radialis L',
        'Flexor Carpi Ulnaris L',
        'Extensor Pollicis Brevis L',
        'Extensor Digitorum Communis L',
        'Extensor Carpi Ulnaris L',
        'Biceps Brachii L',
        'Triceps Brachii L']

    elif emg_placement == 'Jarque-Bou':
        muscle_list = [ 
        'Flexor Carpi Ulnaris R',
        'Flexor Capri Radialis R',
        'Flexor Digitorum Superficialis R',
        'Abductor Pollicis longus and extensor pollicis brevis  R',
        'Extensor Digitorum R',
        'Extensor Carpi Ulnaris R',
        'Extensor Carpi Radialis R',
        'Abductor Pollicis Brevis R',
        'Flexor Carpi Ulnaris L',
        'Flexor Capri Radialis L',
        'Flexor Digitorum Superficialis L',
        'Abductor Pollicis longus and extensor pollicis brevis L',
        'Extensor Digitorum L',
        'Extensor Carpi Ulnaris L',
        'Extensor Carpi Radialis L',
        'Abductor Pollicis Brevis L']

    return muscle_list

def butterworth_filter(emgDF, sr=1500, fco_HP=10, fco_LP=500, N=4):

    # Create new DF from emgDF
    labels_list = emgDF.columns.values.tolist()
    butterworthDF = pd.DataFrame(columns=labels_list)

    # Copy time arrays
    butterworthDF['relative time'] = emgDF['relative time'] 
    butterworthDF['absolute time'] = emgDF['absolute time']

    # Set up filter parameters
    fny = sr/2 #nyquist frequency
    fco = [fco_HP, fco_LP]  #cut off frequency
    N = 4
    [b, a] = sp.butter(N, 1.116*np.array(fco)/fny, btype = 'bandpass')

    # Filter data
    for label in labels_list[2:]:
        butterworthDF[label] = sp.filtfilt(b, a, emgDF[label].values)

    return butterworthDF

def rms_filter(emgDF, rms_window=20):

    # Create new DF from emgDF
    labels_list = emgDF.columns.values.tolist()
    rmsDF = pd.DataFrame(columns=labels_list)

    # Copy time arrays
    rmsDF['relative time'] = emgDF['relative time'] 
    rmsDF['absolute time'] = emgDF['absolute time']

    # Filter data
    for label in labels_list[2:]:
        rmsDF[label] = np.sqrt(np.convolve(np.square(emgDF[label]), np.ones(rms_window)/rms_window, mode='same'))

    return rmsDF

#To compare 2 ordered lists
def compare (a,b):
    s = 0
    L=[]
    for i in range(len(a)):
        if a[i] == b[i]:
            s+=1
            L.append(a[i])
    return (s,L)

#returns [ nb of common pts compared to expected, the common emgs channels]
def calibration_validation(Lmaxcalib,expected = [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]):
    #Get the order of when the max appeared by printing the index
    l=[]
    for i in range(len(Lmaxcalib)):
        l.append([Lmaxcalib[i],i])
    l.sort()
    sort_index = []
    
    for x in l:
        sort_index.append(x[1]) # list of index of max of each muscle
        
    return (compare(sort_index,expected))

def normalization(emgDF, emg_calib):
    normDF = emgDF.copy()
    for col in range (2, emgDF.shape[1]):
        max_col = emg_calib.iloc[:, col].max() #finds the highest value of each column
        min_col = emg_calib.iloc[:, col].min() #finds the smallest value of each column
        
        normDF.iloc[:,col] = (normDF.iloc[:,col] - min_col) / (max_col - min_col) #normalization
    return (normDF)


def main():
    # Example of function calls 
    # TODO : Should be used in separate script with 'from emg_utils import *'
    # TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init

    # Path to mydata.csv folder
    data_dir = r'C:/Users/cabasse/Documents/surgeon_recording/source/surgeon_recording/surgeon_recording/emg_recordings/20-12-2022/calibration_torstein_1/'
    path_to_mydata = data_dir + 'mydata.csv'
    emg_placement = 'Protocol'

    # plot_mydata_raw(path_to_mydata)

    cleanemgDF = clean_emg(path_to_mydata, emg_placement)   
    # plot_emgDF(cleanemgDF)
    print(f"Recording duration : {cleanemgDF['relative time'].iloc[-1]:.2f} s" )

    # Might not be necessary for data analysis
    interpDF = interpolate_clean_emg(cleanemgDF, start_idx=50)
    plot_emgDF(interpDF, title_str='Interpolated EMG')

    butt = butterworth_filter(interpDF)
    # plot_emgDF(butt)

    rms = rms_filter(cleanemgDF)
    # plot_emgDF(rms)

    return


if __name__ == '__main__':
    main()