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
import plotly

from scipy.spatial.distance import euclidean

from fastdtw import fastdtw
from dtw import dtw
import plotly.express as px
#from dtaidistance import dtw

from scipy.interpolate import interp1d

from scipy import signal
from sklearn import preprocessing


class Analyser(object):
    def __init__(self):
        self.data = {}
    # entry: chosen_axes    ex: [x,y,z]
    #        data_files      ex: [cut11, cut12, cut13]  
    #            

    def compute_cinematics(self, data_folder, coordinates, data_files, plot_bool, sigma):  
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
                    tab_plot[axes+'_pos_smooth']= gaussian_filter(tab_plot[axes+'_pos'],sigma=sigma[0])

                    tab_plot[axes+'_speed']=np.gradient(tab_plot[axes+'_pos_smooth'],period)
                    tab_plot[axes+'_speed_smooth'] = gaussian_filter(tab_plot[axes+'_speed'],sigma=sigma[1])

                    tab_plot[axes+'_acc']=np.gradient( tab_plot[axes+'_speed_smooth'],period)
                    tab_plot[axes+'_acc_smooth']= gaussian_filter(tab_plot[axes+'_acc'],sigma=sigma[2])

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
  

    def plot_analysis(self, data_folder, graph_choice, data_files, dtw_on, sigma, nb_interpolation_pts):  
        #find longest vids for ref
        nb_data=len(data_files)
        nb_rows=len(graph_choice)

        array_graph = [0] * nb_data
        f_interpol = [0] * nb_data
        len_stretch = [0] * nb_data  

        data_lenght = []
        data_index = [0]*nb_data

        #find the longest vid
        index_max, data_lenght = self.get_index_max(data_folder, data_files)
        
        #compute cinematics for entry dataset

        coordinates=graph_choice.copy()
        if 'tps' in coordinates: 
            coordinates.remove('tps')
        if 'emg' in coordinates: 
            coordinates.remove('emg')
        if len(coordinates) > 0:   
            results = self.compute_cinematics(data_folder, coordinates, data_files, 0, sigma)
        
        opt_data=pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/optitrack.csv")).set_index('index')
        time=np.array(opt_data['relative_time'])
        fig = make_subplots(rows=nb_rows, cols=1, 
                            subplot_titles=( graph_choice ))
   
        for i, s in enumerate(data_files):
            data_index[i]=int(s[3:])

        #to find the time when cutting start    
        time_cut=pd.read_csv(join(data_folder, 'data10_08_20/cut_start_time.csv')).set_index('index')    
        time_cut_sample=np.divide(np.array( time_cut.iloc[data_index,0]),data_lenght)*100

        print(graph_choice)

        y_max_tps, y_max_emg, y_min_emg = 0, 0, 0
        #plot tps graph
        if any("tps" in s for s in graph_choice):
            y_max_tps=self.tps_plot( data_folder, index_max, data_files, fig, dtw_on, nb_interpolation_pts, graph_choice )

        #plot emg graph
        if any("emg" in s for s in graph_choice):
            y_max_emg, y_min_emg=self.emg_plot( data_folder, index_max, data_files, fig, dtw_on, nb_interpolation_pts, graph_choice )

        self.plot_cut_indicator(time_cut_sample, fig, data_files, data_folder, graph_choice, y_max_tps, y_max_emg, y_min_emg)

        for j, axes in enumerate(coordinates):
            #data file[index max]==cuts13 for example
            ref = results[data_files[index_max]][axes+'_jerk']
            tab = []
            ref_stretched = []
          
            for k, names in enumerate(data_files):       
                print('Axes '+axes+'  '+names)        
                if k!= index_max:      
                    other_serie = results[names][axes+'_jerk']
                    len_stretch, f_interpol, f_ref, len_ref = self.get_interpolation_function(ref, other_serie, dtw_on, len_stretch, f_interpol, k ) 
                                        
            f_interpol[index_max]  = f_ref
            len_stretch[index_max] = len_ref    
          
            norm_time=np.linspace(0, 100, num=nb_interpolation_pts, endpoint=True)
            
            array_graph=self.interpolated_data( f_interpol, len_stretch, data_files, nb_interpolation_pts )
            #plot_each_jerk
            for k, names in enumerate(data_files):
                fig.add_trace(go.Scatter(x=norm_time, y=array_graph[k] , showlegend=False, name='jerk '+names,
                                                     line=dict(color=f'rgba(30, 100, 0, 0.4)', width=1, dash='dot')), 
                                                     row=j+1, col=1
                                                    )    
            #compute mean and std 
            mean = np.mean(array_graph, axis=0)
            std = np.std(array_graph, axis=0)
            
            fig.add_trace(go.Scatter(x=norm_time, y=mean, name='optitracks mean '+axes,
                                                     line=dict(color=f'rgba(200, 100, 0, 1)', width=4, )), 
                                                     row=j+1, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean+std, name='std', showlegend=False,
                                                     line=dict(color=f'rgba(0, 0, 50, 0.5)', width=2, )), 
                                                     row=j+1, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean-std, showlegend=False, 
                                                     line=dict(color=f'rgba(0, 0, 50, 0.5)', width=2, )), 
                                                     row=j+1, col=1
                                                     )
            fig.update_yaxes(title_text="Jerk mag [m/s^3]", range=[-3, 3], row=j+1, col=1)
                
        fig.show()
        return 0
    

    def emg_plot(self, data_folder, index_max, data_files, fig, dtw_on, nb_interpolation_pts, graph_choice ):

        nb_data=len(data_files)

        emg_rows=graph_choice.index('emg')+1

        
        cols = px.colors.qualitative.Dark24
        f_interpol = [0] * nb_data
        len_stretch = [0] * nb_data  

        data_lenght=[]
        data_index=[0]*nb_data

        tps_data=pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/emg.csv")).set_index('index')

        header=list(tps_data.columns)[2:]

        y_max=[0]*len(header)
        y_min=[0]*len(header)

        for i, channel in enumerate(header):
            #data for each channel
            ref_data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/emg.csv")).set_index('index')
            ref_data_by_finger = ref_data_by_file[channel]
          
            for k, name in enumerate(data_files):              
                if k!= index_max:
                    print('EMG'+name)
                    data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/emg.csv")).set_index('index')                 
                    data_by_channel = data_by_file[channel]                  
                    len_stretch, f_interpol, f_ref, len_ref=self.get_interpolation_function(ref_data_by_finger, data_by_channel, 0, len_stretch, f_interpol, k ) 
        
            #fill the missing value for k=index_max        
            f_interpol[index_max]  = f_ref
            len_stretch[index_max] = len_ref

            array_graph=self.interpolated_data( f_interpol, len_stretch, data_files, nb_interpolation_pts )

             #compute mean and std 
            mean = np.mean(array_graph, axis=0)
            std = np.std(array_graph, axis=0)
            
            y_max[i]=np.max(std+mean)
            y_min[i]=np.min(mean-std)

            #plot mean and std fot each channel
            norm_time=np.linspace(0, 100, num=nb_interpolation_pts, endpoint=True)


            fig.add_trace(go.Scatter(x=norm_time, y=mean, name=channel, legendgroup="group"+channel,  opacity=1,
                                                     line=dict(color=cols[i], width=4, )), 
                                                     row=emg_rows, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean+std, name='std'+channel, showlegend=False, legendgroup="group"+channel,  opacity=0.7,
                                                     line=dict(color=cols[i], width=2, )), 
                                                     row=emg_rows, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean-std, name='std'+channel, showlegend=False, legendgroup="group"+channel,  opacity=0.7,
                                                     line=dict(color=cols[i], width=2, )), 
                                                     row=emg_rows, col=1
                                                     ) 
            fig.update_yaxes(title_text="Emg magnitude",  row=5, col=1)  

        return max(y_max), min(y_min) 


    def tps_plot(self, data_folder, index_max, data_files, fig, dtw_on,  nb_interpolation_pts, graph_choice ):

        nb_data=len(data_files)
        tps_rows=graph_choice.index('tps')+1

        
        cols = plotly.colors.DEFAULT_PLOTLY_COLORS
        f_interpol = [0]*nb_data
        len_stretch = [0] * nb_data  

        data_lenght=[]
        data_index=[0]*nb_data

        tps_data=pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/tps.csv")).set_index('index')

        header=list(tps_data.columns)[2:]

        y_max=[0]*len(header)

        for i, finger in enumerate(header):

            multiplier0=str(50+i*50)
            multiplier1=str(i*20)
            multiplier2=str(200-i*80)

            #data for each finger
            ref_data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/tps.csv")).set_index('index')
            ref_data_by_finger = ref_data_by_file[finger]

            for k, name in enumerate(data_files):     
                if k!= index_max:
                    print('TPS'+name)
                    data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/tps.csv")).set_index('index')   
                    data_by_finger = data_by_file[finger]          

                    len_stretch, f_interpol, f_ref, len_ref=self.get_interpolation_function(ref_data_by_finger, data_by_finger, dtw_on, len_stretch, f_interpol, k ) 
   
            #fill the missing value for k=index_max        
            f_interpol[index_max]  = f_ref
            len_stretch[index_max] = len_ref

            array_graph=self.interpolated_data( f_interpol, len_stretch, data_files, nb_interpolation_pts )       

             #compute mean and std 
            mean = np.mean(array_graph, axis=0)
            std = np.std(array_graph, axis=0)
            
            y_max[i]=np.max(std+mean)
            #plot mean and std fot each finger
            norm_time=np.linspace(0, 100, num=nb_interpolation_pts, endpoint=True)
            
            fig.add_trace(go.Scatter(x=norm_time, y=mean, name='tps '+finger, legendgroup="group"+finger, opacity=1,
                                                     line=dict( width=4, color=cols[i] )), 
                                                     row=tps_rows, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean+std, name='std'+finger, showlegend=False,legendgroup="group"+finger, opacity=0.7,
                                                     line=dict( width=2, color=cols[i] )), 
                                                     row=tps_rows, col=1
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean-std, name='std'+finger, showlegend=False, legendgroup="group"+finger, opacity=0.7,
                                                     line=dict( width=2, color=cols[i] )), 
                                                     row=tps_rows, col=1
                                                     ) 
            fig.update_yaxes(title_text="Tps magnitude",  row=4, col=1)  

        return max(y_max)     



    def plot_cut_indicator(self, time_cut_sample, fig, data_files, data_folder, graph_choice,  y_max_tps, y_max_emg, y_min_emg) :


        y_range_max =  {
                          "x": 8,
                          "y": 8,
                          "z": 8,
                          "tps": y_max_tps,
                          "emg": y_max_emg,   
                        }

        y_range_min =  {
                          "x": -4,
                          "y": -4,
                          "z": -4,
                          "tps": 0,
                          "emg": y_min_emg,   
                        }

        #plot cut_start_time
        for i, graph_name in enumerate(graph_choice):

            fig.add_trace(go.Bar(x=time_cut_sample,
                                 y=[y_range_max[graph_name]]*len(time_cut_sample),
                                 base=[y_range_min[graph_name]]*len(time_cut_sample),
                                 opacity=0.7,
                                 showlegend=False,
                                 #name="cut start",
                                 hovertext=  data_files ,
                                 width=[0.1]*len(time_cut_sample),
                                 marker_color='rgb(26, 50, 70)'
                                    ),
                                row=i+1, col=1)
            fig.add_trace(go.Bar(x=[np.mean(time_cut_sample)],
                                 y=[y_range_max[graph_name]],
                                 base=[y_range_min[graph_name]],
                                 opacity=0.7,
                                 showlegend=False,
                                 #name="cut start",
                                 hovertext=  data_files ,
                                 width=[0.4]*len(time_cut_sample),
                                 marker_color='rgb(26, 50, 70)'
                                    ),
                                row=i+1, col=1)

        return 0



    def emg_plot_only(self, data_folder, data_files, dtw_on, nb_interpolation_pts ):

        nb_data = len(data_files)
        
        cols = px.colors.qualitative.Dark24
        f_interpol = [0] * nb_data
        len_stretch = [0] * nb_data 
        data_index = [0]*nb_data 

        index_max, data_lenght = self.get_index_max(data_folder, data_files)
        fig = go.Figure()

        for i, s in enumerate(data_files):
            data_index[i] = int(s[3:])

        emg_data = pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/emg.csv")).set_index('index')

        header = list(emg_data.columns)[2:]

        y_max = [0]*len(header)
        y_min = [0]*len(header)

        for i, channel in enumerate(header):
            #data for each channel
            ref_data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[index_max]+"/emg.csv")).set_index('index')
            ref_data_by_finger = ref_data_by_file[channel]

            #gaussian filter
            ref_data_by_finger =  self.emg_filter(ref_data_by_finger)
          
            for k, name in enumerate(data_files):              
                if k!= index_max:
                    print('EMG'+name)
                    data_by_file = pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/emg.csv")).set_index('index')                 
                    data_by_channel = data_by_file[channel]

                    #gaussian filter
                    data_by_channel = self.emg_filter(data_by_channel)
                   

                    #send back function of interpolation and lenght of streched funcction 
                    len_stretch, f_interpol, f_ref, len_ref=self.get_interpolation_function(ref_data_by_finger, data_by_channel, 0, len_stretch, f_interpol, k ) 
        
            #fill the missing value for k=index_max        
            f_interpol[index_max]  = f_ref
            len_stretch[index_max] = len_ref

            array_graph = self.interpolated_data( f_interpol, len_stretch, data_files, nb_interpolation_pts )

             #compute mean and std 
            mean = np.mean(array_graph, axis=0)
            std = np.std(array_graph, axis=0)
            
            y_max[i] = np.max(std+mean)
            y_min[i] = np.min(mean-std)

            #plot mean and std fot each channel
            norm_time = np.linspace(0, 100, num=nb_interpolation_pts, endpoint=True)


            fig.add_trace(go.Scatter(x=norm_time, y=mean, name=channel, legendgroup="group"+channel,  opacity=1,
                                                     line=dict(color=cols[i], width=4, )), 
                                                   
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean+std, name='std'+channel, showlegend=False, legendgroup="group"+channel,  opacity=0.7,
                                                     line=dict(color=cols[i], width=2, )), 
                                                    
                                                     )
            fig.add_trace(go.Scatter(x=norm_time, y=mean-std, name='std'+channel, showlegend=False, legendgroup="group"+channel,  opacity=0.7,
                                                     line=dict(color=cols[i], width=2, )), 
                                                     
                                                     ) 
            fig.update_yaxes(title_text="Emg magnitude",  ) 

        y_max_emg, y_min_emg = max(y_max), min(y_min)

        time_cut = pd.read_csv(join(data_folder, 'data10_08_20/cut_start_time.csv')).set_index('index')    
        time_cut_sample = np.divide(np.array( time_cut.iloc[data_index,0]),data_lenght)*100 

        fig.add_trace(go.Bar(x=time_cut_sample,
                         y=[y_max_emg-y_min_emg]*len(time_cut_sample),
                         base=[y_min_emg]*len(time_cut_sample),
                         opacity=0.7,
                         showlegend=False,
                         #name="cut start",
                         hovertext=  data_files ,
                         width=[0.1]*len(time_cut_sample),
                         marker_color='rgb(26, 50, 100)'
                            ))

        fig.add_trace(go.Bar(x=[np.mean(time_cut_sample)],
                         y=[y_max_emg-y_min_emg],
                         base=[y_min_emg],
                         opacity=0.7,
                         showlegend=False,
                         #name="cut start",
                         hovertext=  'mean' ,
                         marker_color='rgb(26, 50, 100, 1)',
                         width=[0.5],
                            ))
        fig.show() 
        return 0


    #use optitracks file
    def get_index_max(self, data_folder,  data_files):
        data_lenght=[]

        for k, name in enumerate(data_files):
            opt_data = pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/optitrack.csv")).set_index('index')
            data_lenght.append( opt_data.iloc[-1,1] - opt_data.iloc[0,1])
        
        index_max = max(range(len(data_files)), key=data_lenght.__getitem__)
        
        return index_max, data_lenght


    def interpolated_data(self, f_interpol, len_stretch, data_files, nb_interpolation_pts ):
        array_graph =[0]*len(data_files)
        
        for k, names in enumerate(data_files):
            x_new = np.linspace(0, len_stretch[k], num=nb_interpolation_pts, endpoint=True)
            array_graph[k] = f_interpol[k](x_new)
            
        return array_graph


        #aligne time using either dtw+ interpolation or just interpolation
    def get_interpolation_function(self, ref, other_serie, dtw_on, len_stretch, f_interpol, k ) :
       
        x = np.array(ref)
        y = np.array(other_serie)
       
        if dtw_on : 
            manhattan_distance = lambda x, y: np.abs(x - y)
            d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=manhattan_distance)
            #distance, path = fastdtw(x, y, dist=euclidean)
            stretch_array = y[np.array(path)[1]]
            ref_array    = x[np.array(path)[0]]
        
        else :
            stretch_array=other_serie
            ref_array=ref

        time_lin = np.linspace(0, len(stretch_array)-1, num=len(stretch_array), endpoint=True)
        
        len_stretch[k]=len(stretch_array)-1
        f_interpol[k] = interp1d(time_lin, stretch_array, kind='cubic')
        
        time_lin = np.linspace(0, len(ref_array)-1, num=len(ref_array), endpoint=True)
        
        f_ref= interp1d(time_lin, ref_array, kind='nearest')
        len_ref = len(ref_array)-1
        return len_stretch, f_interpol, f_ref, len_ref


    def emg_test_filter( self, data_folder, data_files, index ):
        emg_data=pd.read_csv(join(data_folder, 'data10_08_20/'+data_files[0]+"/emg.csv")).set_index('index')
        fig=go.Figure()
        header=list(emg_data.columns)[2:]

        for k, name in enumerate(data_files):
            for i, channel in enumerate(header)  : 

                emg_data=pd.read_csv(join(data_folder, 'data10_08_20/'+name+"/emg.csv")).set_index('index')
                filtred_data=self.emg_filter(emg_data[channel])
                norm_time=np.linspace(0, 100, num=len(filtred_data), endpoint=True)
                fig.add_trace(go.Scatter(x=norm_time, y=filtred_data, name=name+channel,  opacity=1,
                                                             line=dict( width=4, )))
        fig.show()
        return 0


    def emg_filter( self, entry_signal ):
        #remove mean 
        mean=np.mean(entry_signal)
        entry_signal=entry_signal-mean

        #rectify signal 
        entry_signal1=abs(entry_signal)

        print('entry',min(entry_signal1))
        
        #lowpass filter
        sos = signal.butter(4, 50, 'lowpass', fs=1000, output='sos')
        filtred_signal = signal.sosfilt(sos, entry_signal1)

        print('after_highpass', min(filtred_signal))

        #highpass filter
        sos = signal.butter(5, 0.5, 'highpass', fs=1000, output='sos')
        #filtred_signal = signal.sosfilt(sos, filtred_signal)
        print('lowpass')
        print(min(filtred_signal))

        #normalisation
        #filtred_signal=preprocessing.normalize([filtred_signal])

        #gaussian filter
        #filtred_signal=gaussian_filter(filtred_signal,sigma=15)

        return filtred_signal