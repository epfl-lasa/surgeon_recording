import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import interpolate
import time 


def clean_optitrack(mydata_path):
    # Input : raw optitrack excel 
    # Output : Format mydata to structured panda DataFrame 

    rawmydataDF = pd.read_csv(mydata_path, header=0, index_col=0)

    # Copy DF
    cleanDF = rawmydataDF.copy()
    
    # Rename time cloumn for easier plots
    # cleanDF.rename(columns={'relative_time' : 'relative time', 'absolute_time' : 'absolute time'})

    print(cleanDF.head())

    # Remove 0s
    tweezerDF, needle_holderDF = remove_zeros_for_plots(cleanDF)

    return tweezerDF, needle_holderDF

def get_tweezer_labels():

    return ['tweezers_x',	'tweezers_y','tweezers_z','tweezers_qx', 'tweezers_qy', 'tweezers_qz', 'tweezers_qw']

def get_needle_holder_labels():

    return ['needle_holder_x',	'needle_holder_y','needle_holder_z','needle_holder_qx', 'needle_holder_qy', 'needle_holder_qz', 'needle_holder_qw']

def get_starting_time(cleanDF):
    # Get starting time from TPS --> WARNING : given in ms, need to convert 
    start_time_in_secs = cleanDF['absolute time'].iloc[0]*1e-3
    
    print("Starting time of TPS recording :", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_in_secs )) )

    return start_time_in_secs

# TODO : adapt for raw TPS 
def interpolate_clean_optitrack(cleanDF, start_idx=0, sr=1500, nb_rec_channels=6):
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

def remove_zeros_for_plots(optiDF):

    # Copy DF and separate for each tool
    tweezerDF = optiDF.copy()
    needle_holderDF = optiDF.copy()

    tweezerDF.drop(columns = get_needle_holder_labels())
    col_to_drop = get_tweezer_labels()
    col_to_drop.append('relative_time')
    col_to_drop.append('absolute_time')
    needle_holderDF.drop(columns= col_to_drop)

    # Remove 0s
    tweezerDF = tweezerDF[tweezerDF['tweezers_x'] != 0]
    needle_holderDF = needle_holderDF[needle_holderDF['needle_holder_x'] != 0]

    # Append back together
    # TODO : fix this ?
    # no_zeroesDF = pd.concat([tweezerDF, needle_holderDF], axis=1, ignore_index=True)

    return tweezerDF, needle_holderDF

def plot_optitrack_csv(mydata_path, title_str='Optitrack 3D position', nb_tools=2 ):
    # Plots raw data from optitrack, removing any row wiht 0 value

    df = pd.read_csv(mydata_path, header=0)
    
    # REMVOVE 0s POORLY (any rows with zero values)

    df = df[(df != 0).all(axis=1) ]

    #MATPLOTLIB
    fig = plt.figure()
    fig.suptitle(title_str)
    ax = fig.add_subplot(1,2,1, projection = '3d')
    
    ax.set_title("Tweezers 3D position")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.plot(df['tweezers_x'], df['tweezers_y'], df['tweezers_z'] )

    ax = fig.add_subplot(1,2,2, projection = '3d')

    ax.set_title("Needle Holder 3D position")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.plot(df['needle_holder_x'], df['needle_holder_y'], df['needle_holder_z'] )
    
    plt.show()
    

def plot_optitrackDF(tweezerDF, needle_holderDF, title_str='Optitrack 3D positions', show_plot=True):
    # Input must be reformatted DF of optitracked tools, one for each tool
    # Plots 3D positions of each tool 

    fig = plt.figure()
    fig.suptitle(title_str)
    ax = fig.add_subplot(1,2,1, projection = '3d')
    
    ax.set_title("Tweezers 3D position")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.plot(tweezerDF['tweezers_x'], tweezerDF['tweezers_y'], tweezerDF['tweezers_z'] )

    ax = fig.add_subplot(1,2,2, projection = '3d')

    ax.set_title("Needle Holder 3D position")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.plot(needle_holderDF['needle_holder_x'], needle_holderDF['needle_holder_y'], needle_holderDF['needle_holder_z'] )
    
    # Get labels
    # labels=df.columns.values.tolist()[2:nb_rec_channels+2]
    
    # fig, ax = plt.subplots(nb_rec_channels,1, sharex=True,figsize=(30,20))
    
    # fig.suptitle(title_str)
    # fig.supylabel('TPS [N]')
    # plt.subplots_adjust(top=0.95,
    #                     bottom=0.04,
    #                     left=0.055,
    #                     right=0.995,
    #                     hspace=0.4,
    #                     wspace=0.2)
    # plt.xlim([DF[time_for_plot].to_numpy()[0], DF[time_for_plot].to_numpy()[-1]])
    # plt.xlabel('time [s]')
     
    # for i in range(len(labels)):
    #     # ax[i].set_ylabel('ch' + str(i+1))
    #     ax[i].plot(DF[time_for_plot].to_numpy(), DF[labels[i]].to_numpy())
    #     ax[i].set_title(labels[i], fontsize = 6)
    #     ax[i].tick_params(axis='x', labelsize=6)
    #     ax[i].tick_params(axis='y', labelsize=6)
    #     ax[i].axhline(y=0.0, c="red", linewidth=1)
          
    if show_plot : plt.show()

def main():
    # Example of function calls 
    # TODO (?) : put functions in an object for easier import, can put data_path and some variables as properties in init

    # Path to mydata.csv folder
    data_dir = '/home/maxime/Workspace/surgeon_recording/exp_data/170423/1/1/'
    path_to_opti = data_dir + 'optitrack.csv'

    cleanDF = clean_optitrack(path_to_opti)   
    # plot_emgDF(cleanemgDF)
    print(f"Recording duration : {cleanDF['relative time'].iloc[-1]:.2f} s" )

    # Might not be necessary for data analysis
    # interpDF = interpolate_clean_tps(cleanDF, sr=500, start_idx=50)
    plot_optitrackDF(cleanDF, title_str='Calibrated TPS', time_for_plot='relative time', nb_rec_channels=6)

    return


if __name__ == '__main__':
    main()