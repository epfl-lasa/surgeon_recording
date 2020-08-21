import sys
from os.path import join
import pandas as pd
import numpy as np
import cv2
from threading import Thread, Event
from multiprocessing import Lock
import os
import asyncio
import time
import plotly.graph_objects as go

from surgeon_recording.sensor_handlers.camera_handler import CameraHandler
from scipy.ndimage import gaussian_filter
from plotly.subplots import make_subplots



from scipy.spatial.distance import euclidean

from fastdtw import fastdtw
from dtw import dtw

#from dtaidistance import dtw

from scipy.interpolate import interp1d


class Analyser(object):
    def __init__(self):

    # entry: chosen_axes    ex: [x,y,z]
    #        data_files      ex: [cut11, cut12, cut13]  
    #            

    def compute_cinematics(self, data_folder, coordinates, data_files, plot_bool):  
        #plot graph for list of coordinate du type [x,y,z] ou [x,y]
        nb_rows=len(coordinates)
        nb_cols=len(data_files)

        subplots_label=[ name for k, name in enumerate(data_files) ]

        fig = make_subplots(rows=nb_rows, cols=nb_cols, 
                            subplot_titles=( subplots_label))

        results=dict()

        for k, name in enumerate(data_files):
          
            opt_data=pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/optitrack.csv")).set_index('index')

            header=list(opt_data.columns)[2:]
            nb_frames=int(len(header)/7)
            names=[]

            for i in range(nb_frames):
                names.append(header[i*7].replace('_x', ''))
                
            opt_labels = ["channel " + str(i) for i in range (0, nb_frames)]

            fig_list=[go.Figure()]*nb_rows

            time = opt_data.iloc[-1,1]
            period=time/len(opt_data)

            # x pos  x pos smooth    x speed    x speed smooth    x acc     x acc smooth    x jerk
            # y pos  y pos smooth    y speed    y speed smooth    y acc     y acc smooth    y jerk
            # z pos  z pos smooth    z speed    z speed smooth    z acc     z acc smooth    z jerk

            tab_plot = dict()

            for i, opt in enumerate(opt_labels):
                multiplier0=str(i*180)
                multiplier1=str(50+i*50)
                multiplier2=str(255-i*150) 

                time=opt_data['relative_time']
                
                for j, axes in enumerate(coordinates):
                    
                    tab_plot[axes+'_pos']=opt_data[names[i]+"_"+axes]
                    tab_plot[axes+'_pos_smooth']= gaussian_filter(tab_plot[axes+'_pos'],sigma=5)

                    tab_plot[axes+'_speed']=np.gradient(tab_plot[axes+'_pos_smooth'],period)
                    tab_plot[axes+'_speed_smooth'] = gaussian_filter(tab_plot[axes+'_speed'],sigma=3)

                    tab_plot[axes+'_acc']=np.gradient( tab_plot[axes+'_speed_smooth'],period)
                    tab_plot[axes+'_acc_smooth']= gaussian_filter(tab_plot[axes+'_acc'],sigma=3)

                    tab_plot[axes+'_jerk']=np.gradient(tab_plot[axes+'_acc_smooth'],period)

                    fig.add_trace(go.Scatter(x=time, y=tab_plot[axes+'_pos_smooth'], name=axes+'_pos'+opt,
                                             line=dict(color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)', width=4, dash='dot')), 
                                             row=j+1, col=k+1)
                    fig.add_trace(go.Scatter(x=time, y=tab_plot[axes+'_speed_smooth'], name=axes+'_speed '+opt,
                                             line=dict(color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)', width=4, dash='dash')),
                                             row=j+1, col=k+1)
                    fig.add_trace(go.Scatter(x=time, y=tab_plot[axes+'_acc_smooth'], name=axes+'_acc '+opt,
                                             line=dict(color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)', width=4,  dash='dashdot')),
                                             row=j+1, col=k+1) 
                    fig.add_trace(go.Scatter(x=time, y=tab_plot[axes+'_jerk'], name=axes+'_jerk '+opt,
                                             line=dict(color=f'rgba({multiplier0}, {multiplier1}, {multiplier2}, 1)', width=4)),
                                             row=j+1, col=k+1)
 
                    fig.update_xaxes(title_text="Time in s")
                    fig.update_yaxes(title_text="")
            
            results[name]=tab_plot        
            
        if plot_bool:
            fig.show()

        return results


    # entry: chosen_axes    ex: [x,y,z]
    #        data_files      ex: [cut11, cut12, cut13]  
    #        dtw_on  boolean to activate dtw before interpolation
  

    def plot_analysis(self, data_folder, coordinates, data_files, dtw_on):  
        #find longest vids for ref
        nb_data=len(data_files)
        data_lenght=[]
        nb_rows=len(coordinates)
        
        for k, name in enumerate(data_files):
            opt_data = pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/optitrack.csv")).set_index('index')
            data_lenght.append( opt_data.iloc[-1,1] - opt_data.iloc[0,1])
        index_max = max(range(len(data_lenght)), key=data_lenght.__getitem__)

        #compute cinematics for entry dataset
        results = self.compute_cinematics(data_folder, coordinates, data_files,0)
        
        opt_data=pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/optitrack.csv")).set_index('index')
        time=np.array(opt_data['relative_time'])

        fig = make_subplots(rows=nb_rows, cols=1, 
                            subplot_titles=( "Plot X", "Plot Y", "Plot Z" ))

        array_graph =[0]*nb_data
        f_interpol = [0]*nb_data
        len_stretch = [0] * nb_data  

        for j, axes in enumerate(coordinates):
            #data file[index max]==cuts13 for example
            ref = results[data_files[index_max]][axes+'_jerk']
            tab = []
            ref_stretched = []
          
            for k, names in enumerate(data_files):
                
                print('Axes '+axes+'  '+names)
                if k!= index_max:       
                    x = ref
                    y = results[names][axes+'_jerk']
                   
                    if dtw_on : 
                        manhattan_distance = lambda x, y: np.abs(x - y)
                        d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=manhattan_distance)
                        #distance, path = fastdtw(x, y, dist=euclidean)
                        stretch_array=results[names][axes+'_jerk'][np.array(path)[1]]
                        ref_array    =ref[np.array(path)[0]]
                    
                    else :
                        stretch_array=results[names][axes+'_jerk']
                        ref_array=results[data_files[index_max]][axes+'_jerk']

                    time_lin = np.linspace(0, len(stretch_array)-1, num=len(stretch_array), endpoint=True)
                    len_stretch[k]=len(stretch_array)-1
                  
                    f_interpol[k] = interp1d(time_lin, stretch_array, kind='cubic')
                    
                    time_lin = np.linspace(0, len(ref_array)-1, num=len(ref_array), endpoint=True)
                    f_ref= interp1d(time_lin, ref_array, kind='cubic')
                    len_ref = len(ref_array)-1
                                        
            f_interpol[index_max]  = f_ref
            len_stretch[index_max] = len_ref
            
            time=time[np.linspace(0, len(time)-1, num=400, endpoint=True).astype(int)]

            for k, names in enumerate(data_files):
                x_new = np.linspace(0, len_stretch[k], num=400, endpoint=True)
                array_graph[k] = f_interpol[k](x_new)
                fig.add_trace(go.Scatter(x=time, y=array_graph[k] , showlegend=False, name='jerk '+names,
                                                     line=dict(color=f'rgba(30, 100, 0, 0.4)', width=1, dash='dot')), 
                                                     row=j+1, col=1
                                                    )    
            #compute mean and std 
            mean = np.mean(array_graph, axis=0)
            std = np.std(array_graph, axis=0)

            fig.add_trace(go.Scatter(x=time, y=mean, name='mean',
                                                     line=dict(color=f'rgba(200, 100, 0, 1)', width=4, )), 
                                                     row=j+1, col=1
                                                     )
            fig.add_trace(go.Scatter(x=time, y=mean+std, name='std',
                                                     line=dict(color=f'rgba(0, 0, 50, 0.5)', width=2, )), 
                                                     row=j+1, col=1
                                                     )
            fig.add_trace(go.Scatter(x=time, y=mean-std, showlegend=False,
                                                     line=dict(color=f'rgba(0, 0, 50, 0.5)', width=2, )), 
                                                     row=j+1, col=1
                                                     )

            fig.update_yaxes(title_text="Jerk mag [m/s^3]", range=[-4, 4], row=j+1, col=1)
                
        fig.show()

        return 0
    



    












        
