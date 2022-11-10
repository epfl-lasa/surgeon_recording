## This file is used to plot the different useful functions for our notebook 

### Writen by Marwen on 07_2022

#### Library importation ##########

import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go 
import matplotlib.pyplot as plt

from scipy import signal


###################################



## The function below is import to display a 3d trajectory of our tools 
def basic_3d_trajectory(data, run, tools,starting,ending, save = False):
    fig = go.Figure()
    data_copy = data[run].copy()
    data_copy = data_copy[data_copy['needle_holder2_x'] != 0  ]
    data_copy = data_copy[data_copy['tweezer_x'] != 0]
    data_copy = data_copy[data_copy['relative_time'] > starting]
    data_copy = data_copy[data_copy['relative_time'] < ending]
    #for tool in tools :
     #   data_copy = data_copy.loc(data_copy[tool+'_x'] != 0)
    for tool in tools :
        fig.add_trace(go.Scatter3d(x = data_copy[tool+'_x'][:], y = data_copy[tool+'_y'][:], z = data_copy[tool+'_z'][:], marker = dict(size = 2), name = tool))
    


    fig.update_layout(
        title=f'Displacement of the tools in 3D for {run}',
        width = 1000,
        height = 800,
        autosize = False,
        legend_title="Tools "
        )
    if not save :
        fig.show()
    else:
        fig.write_image(f'./figures/3D_Displacement_of_tools_{run}.svg')
        print('Finished saving the different plots !')### Plotting the trajectory  segmentation
        
        
        
### here is an update of the 3D trajectories for the segmented parts  

def basic_3d_trajectory_segmented(data, data_seg, run, tools, save = False):
    fig = go.Figure()
    data_copy_ent = {}
    for i in range(2):
        if i == 0 :
            data_copy = data[run].copy()
        else: 
            data_copy = data_seg[run].copy()
        
        data_copy = data_copy[data_copy['needle_holder2_x'] != 0  ]
        data_copy = data_copy[data_copy['tweezer_x'] != 0]    
        data_copy_ent[i] = data_copy.copy()
    for i in range(2):
        for tool in tools :
            if i == 0:
                sep = 'full'
                sz = 1
            else:
                sep = 'seg'
                sz = 2
            fig.add_trace(go.Scatter3d(x = data_copy_ent[i][tool+'_x'][:], y = data_copy_ent[i][tool+'_y'][:], z = data_copy_ent[i][tool+'_z'][:], 
                                       marker = dict(size = sz), name = f'{tool}_{sep}'))
    fig.update_layout(
        title=f'Displacement of the tools in 3D for {run}',
        width = 1000,
        height = 800,
        autosize = False,
        legend_title="Tools "
        )
    if not save :
        fig.show()
    else:
        fig.write_image(f'./figures/3D_Displacement_of_tools_{run}.svg')
        print('Finished saving the different plots !')
        
        
 ## Here we can add a simple Velocity or acceleration function : 


def plot_acc_velocity(signal, time_vector, y_axis = 'Velocity', axis = 'one'):
    
    
    
    if axis == 'one' :
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x = time_vector, y = signal))


        fig.update_layout(
            xaxis_title="Time Vector",
            yaxis_title=y_axis
        )
    if axis == 'three':
        fig = make_subplots(rows = 3)
        ## Make it look nice for the presentation 
        fig.update_layout(
                    title=f'Velocity of a specific tool around three axis',
                    legend_title="Axis" )
        for i in range(3):
            fig.add_trace(go.Scatter(x= time_vector , y = signal[:,i] , marker = dict(size = 1), name = f'axis_{i}'),row=i+1,col=1)
            fig.update_layout(
                    xaxis_title="Time_vector (s)",
                    yaxis_title="Velocity (m/s)"
            )
       
        
    fig.show()
        
        
        
        
        
        
        
        
        
        
    
#The last function will diplay the displacement of each tool :

def plotting_displacement(data ,run, tools , step = 1, len_rec = None, save = False, format_s = 'jpg', subject = '1'):
    fig = go.Figure()
    if not len_rec :
        len_rec = len(data[run]['relative_time'])
    for tool in tools :
        for j in ['x','y','z'] :
            fig.add_trace(go.Scatter(x = data[run]['relative_time'][::step], y = data[run][tool+'_'+f'{j}'][::step], mode = 'markers', name = tool+f'_{j}'))
    
    fig.update_layout(
        title=f'Displacement of the tools for {run}',
        xaxis_title="Relative Time",
        yaxis_title="Displacement",
        legend_title="Tools and axis"
    )

    if save : 
        fig.write_image(f'./figures/Displacement_of_toolssubject_{subject}_{run}.{format_s}')
        print('Finished saving the different plots !')
    else :
        fig.show()
        
        
        
### Here is a plot of a segmented displacement for the trajectory : 


def plotting_displacement_segmented(data , data_seg, run, tools , step = 1, len_rec = None, save = False, format_s = 'jpg', subject = '1'):
    fig = go.Figure()
    if not len_rec :
        len_rec = len(data[run]['relative_time'])
    for tool in tools :
        for j in ['x','y','z'] :
            fig.add_trace(go.Scatter(x = data[run]['relative_time'][::step], y = data[run][tool+'_'+f'{j}'][::step], mode = 'markers', name = tool+f'_{j}'))
            fig.add_trace(go.Scatter(x = data_seg[run]['relative_time'][::step], y = data_seg[run][tool+'_'+f'{j}'][::step], mode = 'markers', name = tool+f'_{j}_seg'))
    fig.update_layout(
        title=f'Displacement of the tools for {run}',
        xaxis_title="Relative Time",
        yaxis_title="Displacement",
        legend_title="Tools and axis"
    )

    if save : 
        fig.write_image(f'./figures/Displacement_of_toolssubject_{subject}_{run}.{format_s}')
        print('Finished saving the different plots !')
    else :
        fig.show()
        
        

        
## This will display the new 3 trajectory with a new interpolation format. 

def basic_3d_trajectory_interpolated(time_vectors, data, run, tools,starting,ending, save = False , mode = 'select'):
    fig = go.Figure()
    if mode == 'select':
        data_copy = data[run].copy()
        time_vector = time_vectors[run].copy()
        print(len(data_copy['tweezer']), len(time_vector))
        for tool in tools :
            data_diplay = data_copy[tool][time_vectors[run] >= starting]
            #time_vector =  time_vector[time_vector >starting]
            data_display = data_diplay[time_vectors[run] <= ending]
            fig.add_trace(go.Scatter3d(x = data_display[::2,0], y = data_display[::2,1], z = data_display[::2,2], marker = dict(size = 2), name = tool))
    else:
        data_display = data.copy() 
        fig.add_trace(go.Scatter3d(x = data_display[::2,0], y = data_display[::2,1], z = data_display[::2,2], marker = dict(size = 2)))
        
       
        


    fig.update_layout(
        title=f'Displacement of the tools in 3D for {run}',
        width = 1000,
        height = 800,
        autosize = False,
        legend_title="Tools "
        )
    if not save :
        fig.show()
    else:
        fig.write_image(f'./figures/3D_Displacement_of_tools_{run}.svg')
        print('Finished saving the different plots !')
    
    
    
    
    
    
    
def design_filter_bp(order, cuttoff_1, cuttoff_2):
    
    ### Try to design the filter and visualize it : 
    ## This part is reused from the documentation of the library
    b, a = signal.butter(order, [cuttoff_1,cuttoff_2], 'bp', analog=True)
    w, h = signal.freqs(b, a)
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    #plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.axvline(cuttoff_1, color='green') # cutoff frequency
    plt.axvline(cuttoff_2, color='red') # cutoff frequency
    plt.show()
    
    
    
    

    
    
    

    
    
    
def plotting_with_different_parts(time_intervals,time_vector, trajectory, tools, subject):
    # this graph can be used to  plot the 3d trajectory with several parts and having both tools
    fig = go.Figure()
    raw_symbols = ['circle', 'diamond',
            'diamond-open', 'square', 'square-open', 'x']
    for j,tool in enumerate(tools):
        fig.add_trace(go.Scatter3d(x = trajectory[tool][:,0],y = trajectory[tool][:,1] ,z = trajectory[tool][:,2] ,  
                                   marker = dict(size=1), mode = 'markers', marker_symbol = raw_symbols[j] 
                                   , name = f'full_trajectory_{tool}'))
        for i, interval in enumerate(time_intervals[tool]):
            start_indent = np.min(np.where(time_vector > interval[0] ))
            end_indent = np.min(np.where(time_vector> interval[1]))
            fig.add_trace(go.Scatter3d(x = trajectory[tool][start_indent:end_indent,0],y = trajectory[tool][start_indent:end_indent,1] ,
                                       z = trajectory[tool][start_indent:end_indent,2] ,marker = dict(size = 2), mode = 'markers', 
                                       name = f'{tool}_part_{i+1}'))
       
    fig.update_layout(
            title=f'Displacement of the tools and decomposition of the movement  {subject}',
            width = 1000,
            height = 800,
            autosize = False,
            legend_title="tools and parts :")
    fig.show()
    
    
    
    

    
def plotting_PSD_graph_3_axis(f,Pxx_den, axis = True):
    if axis:
        for i in range(3):
            label = f'axis_{i+1}'
            plt.semilogy(f[label],Pxx_den[label], label = label)
    else:
        plt.semilogy(f,Pxx_den, label ='first_axis')

    plt.ylim([1e-15, 1e2])
    if not axis:
        plt.xlim([0 ,20])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.legend()
    
    plt.show()