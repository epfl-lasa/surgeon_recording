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
from shutil import copyfile
from surgeon_recording.sensor_handlers.camera_handler import CameraHandler
from os.path import exists
from bisect import bisect_left

import csv
from natsort import natsorted

from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class Synchro(object):
    
    """
    A class used to define functions for synchronization of 3 videos (RS, GOPRO, MICROSCOPE) and sensor data
    
    """
    
    def __init__(self):
        self.available_cameras = ['GOPRO', 'MICROSCOPE', 'REALSENSE']
        self.needed_sensors = ['camera', 'emg']

        self.data = {}
        self.images = {}

        self.mutex = Lock()
        
        self.nb_frames = {}
        self.sum_frame = {}
        
        self.abs_time_vector = {}
        
        self.csv_names = []
        
        self.index = {}
        self.relative_time = {}
        self.absolute_time = {}
        
        self.pos_start = {}
        self.pos_stop = {}
        self.rel_time_start = {}
        self.rel_time_stop = {}
        self.abs_time_start = {}
        self.abs_time_stop = {}
        
        #self.blank_image = CameraHandler.create_blank_image(encode=True)
        #self.data_changed = False
        #self.stop_event = Event()
        #self.image_extractor_thread = Thread(target=self.extract_images)
        #self.image_extractor_thread.daemon = True
        #self.image_extractor_thread.start()

               
        
    def play(self, directory, camera):
        """ allows to store for each camera the data from the camera csv file in the data variable. Can access the different data using the column names. """
        self.files = directory
        with self.mutex:
            indexes = {}
            self.files_list = []
            #for i, s in enumerate(files):
            #datafile = files[i]
                #if exists(datafile):
            #self.files_list.append(s)
            self.data[camera] = pd.read_csv(directory)
            #self.init_image_list()
            #self.align_relative_time()
            #self.data_changed = True
            
    def take_closest(self, myList, myNumber, min_frame):
        """ gives closest value to MyNumber (time reference) in MyList (time available for other cameras) and it position, starting looking in the list from min_frame  """
    
    #Assumes myList is sorted. Returns closest value to myNumber.
    #If two numbers are equally close, return the smallest number.
        myList = myList.values.tolist()
        pos = bisect_left(myList, myNumber, min_frame)       
        #donne la position a laquelle il faudrait placer la valeur pour garder la liste ordonnee, et on regarde que au dessus de la frame de ref (avant abs_time NAN anyway)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
            return [pos, after]
        else:
            return [pos, before]   
        
    
    def bag_to_png(self, path_to_data, data_folder, camera):
        """ extract all png from a bag file (here for RS camera, file stored in BAG folder for REALSENSE)"""
       
        bag_file = [x[2] for x in os.walk(join(data_folder, camera, 'BAG'))]
        print(bag_file[0][0])

        path_bag_file = join(path_to_data, recording_session , subject, camera, 'BAG', bag_file[0][0])
        print('bag file: ' + path_bag_file)
        path_png=  join(path_to_data, recording_session , subject,  camera, 'PNG', 'png')
        print('png folder: ' + path_png)
        os.system('rs-convert -i ' + path_bag_file + ' -p ' + path_png)
        
    def png_to_MP4(self,fps, data_folder, camera): 
        """ Get all png into one mp4 video (here for RS camera). The images are sorted by names to have accurate stream in time. """
        
        image_folder=join(data_folder, camera, 'PNG')
        print('image folder: ' + image_folder)
                   
        image_files = [os.path.join(image_folder,img) for img in os.listdir(image_folder) if img.endswith(".png")]
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(natsorted(image_files), fps=fps)
        path_mp4 = join(data_folder, camera, 'MP4', 'rs_converted.mp4')
        print('mp4 file: ' + path_mp4)
        clip.write_videofile(path_mp4)
    
    def concatenate_videos(fps, data_folder, camera):
        """get the different segments created by the gopro and microscope cameras into 1 single video. The segments must be in the segments folder under camera folder. """
        L =[]

        for root, dirs, files in os.walk(join(data_folder, camera, 'segments')):

            files = natsorted(files)
            print(files)
            for file in files:
                if os.path.splitext(file)[1] == '.MP4' or os.path.splitext(file)[1] == '.mp4': 
                    filePath = os.path.join(root, file)
                    video = VideoFileClip(filePath)
                    L.append(video)
    
        final_clip = concatenate_videoclips(L)
        tmp = 'output' + camera + '.mp4'
        output_path = join(data_folder, camera, 'complete', tmp)
        final_clip.to_videofile(output_path, fps=fps, remove_temp=False)
    
    def get_nb_frame(self, data_folder, cameras, folder):
        """ get nb of frame from RS counting the nb of png files that were extracted, get nb of frames from the MP4 videos for gopro and microscope. Compute sum of frames of the segments for gotpo and microscope to compare. """

        for k in range(len(cameras)):    #for the different cameras
            camera = cameras[k]
            self.sum_frame[camera] = {}
            for j in range(len(folder)):  #segments and complete
                files = [x[2] for x in os.walk(join(data_folder, camera,folder[j]))]   #get the nam of the files of the video
                tmp = 0
                if camera == 'REALSENSE':
                    image_folder=join(data_folder, camera, 'PNG')            # file directory to access the png files (Attention: also in the function to get video from png)
                    image_files = [os.path.join(image_folder,img) for img in os.listdir(image_folder) if img.endswith(".png")]
                    # get nb of frames of the rs camera
                    rs_nb_frame = len(image_files)
                    self.nb_frames[camera] = rs_nb_frame

                else:
                    if len(files) != 0:                                                    
                        for i in range(len(files[0])):                                   
                            file = files[0][i]                                             # prend la valeur des differents fichiers a la suite (les videos)
                
                            if os.path.splitext(file)[1] == '.MP4' or os.path.splitext(file)[1] == '.mp4':   #check si bien une video
                            #print(join(data_folder, folder[j], file))
                                cap = cv2.VideoCapture(join(data_folder, camera, folder[j], file))
                                                 
                
                            if folder[j]== 'segments':                                # si on est dans le fichiers des segments on calcule la somme de tous les segments
                                self.nb_frames[file] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                tmp = tmp + self.nb_frames[file]                            # store nb of frames with file name as key
                                self.sum_frame[camera] = tmp
                            else:
                                self.nb_frames[camera] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                     
                            
            if folder[j]=='segments':      #print(file, '  nb of frames:   ', nb_frames[file] )
                print('Total nb of frames of segments for ', camera, self.sum_frame[camera])
        
    def get_abs_time_png_names(self, data_folder, camera, rs_frame):
        """ get the vector of absolute time reference from the RS png names. Use the last 32 to 4 characters of the name (corresponds to the time digits, last 4 are .png) """
        
        # file directory to access the png files (Attention: also in the function to get video from png)
        image_folder=join(data_folder, camera, 'PNG')
        image_files = [os.path.join(image_folder,img) for img in os.listdir(image_folder) if img.endswith(".png")]

        # get absolute time vector of rs from png files
        
        self.abs_time_vector[camera] = [name[-32:-4] for name in natsorted(image_files)]

        self.rs_abs_time = float(self.abs_time_vector['REALSENSE'][rs_frame]) #abs time vector from png names
        
        
    def write_csv_file_camera(self, data_folder, cameras, folder, frame, fps):
            
        for camera in cameras:
            for folder_name in folder:
                files = [x[2] for x in os.walk(join(data_folder, camera ,folder_name))]
                print(files)  
        
                if camera == 'REALSENSE':
                    rs_csv = join(data_folder,camera, 'CSV', 'complete', 'REALSENSE_abs_time.csv')
                    f = open(rs_csv, 'w') # open the file in the write mode                        #open last one
    
                    # create the csv writer
                    writer = csv.writer(f)
                    header = ['index','frequency','relative_time','abs_time']
                    # write a row to the csv file
                    writer.writerow(header)
                    rel_time = 0
                    #abs_time = rs_abs_time                                        #put the ref_abs time we got from RS as the first absolute time to write
            
                    for m in range(self.nb_frames[camera]):                            #pour toutes les frames
                        abs_time = self.abs_time_vector['REALSENSE'][m]
                        #if m >= frame[camera]:        # si on est dans les videos completes et que l-indice est plus grand que la frame avec le mvmt de ref
                        row = [m,fps[camera],rel_time,float(abs_time)]               # alors on inscrit le abs time, et a partir de la on l'incremente de la fps (en ms)
                            #abs_time = abs_time + 1/fps[camera]*1000
                        #else:
                            #row = [m, fps[camera], rel_time]                # sinon on est soit dans les segments (pas besoin absolute time), soit on est avant le mvmt de ref donc pas de abs time
                    
                        writer.writerow(row)
                        rel_time = rel_time + 1/fps[camera]                       # on incremente le rel time par la fps corespondante 
                            
                    #print(float(abs_time)-1/fps[camera]*1000)
                    f.close()        
            
                else:
                    for i in range(len(files[0])):
                        file = files[0][i] 
                        if os.path.splitext(file)[1] == '.mp4' or os.path.splitext(file)[1] == '.MP4':
            
                            self.csv_names.append(join(data_folder,camera, 'CSV',folder_name, str(file)[0:15] + '_abs_time.csv'))  #create the csv references
                            f = open(self.csv_names[-1], 'w') # open the file in the write mode                        #open last one
    
    
                            # create the csv writer
                            writer = csv.writer(f)
                            header = ['index','frequency','relative_time','abs_time']
    
                            # write a row to the csv file
                            writer.writerow(header)
                            rel_time = 0
                            abs_time = self.rs_abs_time                                        #put the ref_abs time we got from RS as the first absolute time to write
                    
                            if folder_name == 'complete':
                                for m in range((self.nb_frames[camera])):                      #camera key pour les complete csv      
                                    if m >= frame[camera]:        # si on est dans les videos completes et que l-indice est plus grand que la frame avec le mvmt de ref
                                        row = [m,fps[camera],rel_time,abs_time]               # alors on inscrit le abs time, et a partir de la on l'incremente de la fps (en ms)
                                        abs_time = abs_time + 1/fps[camera]*1000
                                    else:
                                        row = [m, fps[camera], rel_time]         # sinon on est soit dans les segments (pas besoin absolute time), soit on est avant le mvmt de ref donc pas de abs time
                                    writer.writerow(row)
                                    rel_time = rel_time + 1/fps[camera]    
                            else:
                                for m in range((self.nb_frames[file])):                        #file key pour les segmens csv
                                    row = [m, fps[camera], rel_time]
                                
                                    writer.writerow(row)
                                    rel_time = rel_time + 1/fps[camera]                       # on incremente le rel time par la fps corespondante 
                            
           
                            f.close()
            
    def get_csv_data_camera(self, data_folder, cameras):
        #reprend les donnes de csv , on peut en profiter pour les cut
        for camera in cameras:
            file = [x[2] for x in os.walk(join(data_folder, camera , 'CSV', 'complete'))]
            print(file[0][0])  
    
            directory = join(data_folder, camera , 'CSV', 'complete', file[0][0])
            print(directory)
            self.play(directory, camera)
            self.index[camera] = self.data[camera]['index']
            self.relative_time[camera] = self.data[camera]['relative_time']
            self.absolute_time[camera] = self.data[camera]['abs_time']
            
    
    def get_micro_frame_from_csv(self, data_folder):
    
        #get ref fram of microscope directly from csv file
        file = [x[2] for x in os.walk(join(data_folder, 'SEGMENTATION_CSV'))]
        print(file[0][0])  
    
        directory = join(data_folder ,'SEGMENTATION_CSV', file[0][0])
        #print(directory)
        DATA = pd.read_csv(directory)
        self.start_ref_frame_vector = DATA['Start_frame']
        self.stop_ref_frame_vector = DATA['Stop_frame']
        self.index_segment_vector = DATA['nb']
        #print(start_ref_frame)
    
   
    def export_synchro_videos(self,path_to_data_folder, data_folder, recording_session, subject, cameras, camera_ref, frame):
        
        for o in range(len(self.start_ref_frame_vector)):
            start_ref_frame = self.start_ref_frame_vector[o]
            stop_ref_frame = self.stop_ref_frame_vector[o]

            #after reading the frame in the csv. we take the abs time coresponding to the frame (using index) to find it in the other cameras
            start_ref_abs_time = self.absolute_time[camera_ref][start_ref_frame]
            stop_ref_abs_time = self.absolute_time[camera_ref][stop_ref_frame]
        
            print("start reference abs time:  ", start_ref_abs_time)  
            print("stop reference abs time:  ", stop_ref_abs_time) 
            print("----------------------")
            for camera in cameras:
                self.pos_start[camera] = []
                self.pos_stop[camera] = []
                self.rel_time_start[camera] = {}
                self.rel_time_stop[camera] = {}
                self.abs_time_start[camera] = {}
                self.abs_time_stop[camera] = {}
                if not camera in camera_ref:
                    #take closest position and absolute time in the absolute_time of the camera list to the absolute time reference, from the synchro frame (before NaN anyway)
                    [self.pos_start[camera], self.abs_time_start[camera]]= self.take_closest(self.absolute_time[camera], start_ref_abs_time, frame[camera])
                    [self.pos_stop[camera], self.abs_time_stop[camera]] = self.take_closest(self.absolute_time[camera], stop_ref_abs_time, frame[camera])
                    print(camera, "start index:       ", self.pos_start[camera], "abs time:   ", self.abs_time_start[camera])
                    print(camera, "stop index:        ", self.pos_stop[camera], "abs time:   ", self.abs_time_stop[camera])
                    
            
                    #with the position we got from abs time, take the coresp. rel time to use for video export
                    self.rel_time_start[camera] = self.relative_time[camera][self.pos_start[camera]]
                    self.rel_time_stop[camera] = self.relative_time[camera][self.pos_stop[camera]]
                    print(camera, "start index:       ", self.pos_start[camera], "rel time:   ", self.rel_time_start[camera])
                    print(camera, "stop index:       ", self.pos_stop[camera], "rel time:   ", self.rel_time_stop[camera])
                    print("----------------------")
                else:
                    #for micrsocope: we know the reference frames from the csv directly, so we just take the abs and rel time value coresponding
                    self.rel_time_start[camera] = self.relative_time[camera][start_ref_frame]
                    self.rel_time_stop[camera]  = self.relative_time[camera][stop_ref_frame]
                    #self.abs_time_start[camera] = self.absolute_time[camera][start_ref_frame]
                    #self.abs_time_stop[camera]  = self.absolute_time[camera][stop_ref_frame]
                    
                    self.abs_time_start[camera] = start_ref_abs_time
                    self.abs_time_stop[camera] = stop_ref_abs_time
                    
                    print(camera, "start index   ", start_ref_frame, "rel time:   ", self.rel_time_start[camera])
                    print(camera, "stop index   ", stop_ref_frame, "rel time:   ", self.rel_time_stop[camera])
                    print("----------------------")
                    self.pos_start[camera] = start_ref_frame
                    self.pos_stop[camera] = stop_ref_frame
            
                #export video from t1 to t2 in seconds

                t1 = self.rel_time_start[camera]
                t2 = self.rel_time_stop[camera]
    
                #name with abs time ref
                #r1 = self.abs_time_start[camera]
                #r2 = self.abs_time_stop[camera]
                #ref = str(r1)[1:7] + "_to_" + str(r2)[1:7] + ".mp4"
    
                #name with no of frame
                r1 = self.pos_start[camera]
                r2 = self.pos_stop[camera]
                ref = str(r1) + "_to_" + str(r2) + ".mp4"

                #name with rel time
                #ref = str(t1)[1:7] + "_to_" + str(t2)[1:7] + ".mp4"

                #name with rsegment nb
                r1 = self.index_segment_vector[o]
                ref = "segment_nb_" + str(r1) + ".mp4"

                file = [x[2] for x in os.walk(join(data_folder, camera , 'complete'))]
                print(file[0][0])  
                target_name = join(path_to_data_folder, recording_session, subject, camera , 'SEGMENTATION', ref)
                file_name = join(data_folder, camera, 'complete', file[0][0])
                print(target_name)
                ffmpeg_extract_subclip(file_name, t1, t2, targetname=target_name)
                
                
    def color_clip(self, size, duration, output, fps=25, color=(0,0,0)):
        ColorClip(size, color, duration=duration).write_videofile(output, fps=fps)
        return ['ok']
                
    
     #def color_clip(size, duration, output, fps=25, color=(0,0,0)):ColorClip(size, color, duration=duration).write_videofile(output, fps=fps)

    
         
    """        
    def get_experiment_list(self, data_folder):
        res = {}
        needed_files = [s + '.csv' for s in self.needed_sensors] + ['rgb.avi', 'depth.avi']
        exp_list = []
        exp_list = [x[0] for x in os.walk(data_folder) if all(item in x[2] for item in needed_files)]
        exp_list.sort()
        for exp in exp_list:
            res[exp] = exp
        return res

    def get_indexes(self, initial_guesses, idx):
        max_index = self.get_nb_frames()
        camera_index = initial_guesses['camera'][idx]
        camera_frame = self.data['camera'].iloc[camera_index]
        time = camera_frame[2]
        # extract the other sensor data (exept camera)
        indexes = {}
        indexes['camera'] = camera_index
        for s in self.sensor_list[1:]:
            index = initial_guesses[s][idx]
            frame = self.data[s].iloc[index]
            indexes[s] = index
            prev_sign = np.sign(time - frame[2])
            while abs(time - frame[2]) > 1e-3:
                sign = np.sign(time - frame[2])
                if prev_sign - sign != 0:
                    break
                index = int(index + sign * 1)
                if index < 0 or index >= self.get_nb_sensor_frames(s):
                    break
                frame = self.data[s].iloc[index]
                indexes[s] = index
                prev_sign = sign
        return indexes

    def get_window_data(self, indexes):
        start_frame = indexes['camera'][0]
        stop_frame = indexes['camera'][1]
        max_index = self.get_nb_frames()
        if start_frame < 0 or start_frame > max_index:
            print('Incorrect index, expected number between 0 and ' + str(max_index) + ' got ' + str(start_frame))
            return -1
        if stop_frame < 0 or stop_frame > max_index:
            print('Incorrect index, expected number between 0 and ' + str(max_index) + ' got ' + str(stop_frame))
            return -1
        start_indexes = self.get_indexes(indexes, 0)
        stop_indexes = self.get_indexes(indexes, 1)
        window_data = {}
        for s in self.sensor_list:
            window_data[s] = self.data[s].iloc[start_indexes[s]:stop_indexes[s]+1]
        return window_data

    def get_nb_frames(self):
        return len(self.data['camera'])

    def get_nb_sensor_frames(self, sensor):
        return self.data[sensor].count()[0]

    def init_image_list(self):
        for t in ['rgb', 'depth']:
            self.images[t] = []
            for i in range(self.get_nb_frames()):
                self.images[t].append(self.blank_image)

    def extract_images(self):
        def extract_image(video):
            _, frame = video.read()
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer

        while True:
            if self.data_changed:
                self.data_changed = False
                rgb_video = cv2.VideoCapture(join(self.exp_folder, 'rgb.avi'))
                depth_video = cv2.VideoCapture(join(self.exp_folder, 'depth.avi'))
                for i in range(self.get_nb_frames()):
                    rgb_image = extract_image(rgb_video)
                    depth_image = extract_image(depth_video)
                    with self.mutex:
                        if self.data_changed:
                            break
                        self.images['rgb'][i] = rgb_image
                        self.images['depth'][i] = depth_image
                rgb_video.release()
                depth_video.release()
            time.sleep(0.01)

    def get_image(self, video_type, frame_index):
        max_index = self.get_nb_frames()
        if frame_index < 0 or frame_index > max_index:
            print('Incorrect index, expected number between 0 and ' + str(max_index) + ' got ' + str(frame_index))
            return -1
        with self.mutex:
            image = self.images[video_type][frame_index]
        return image

    def align_relative_time(self):
        min_time = max([self.data[s]['relative_time'].iloc[0] for s in self.sensor_list])
        max_time = min([self.data[s]['relative_time'].iloc[-1] for s in self.sensor_list])

        for s in self.sensor_list:
            self.data[s] = self.data[s][np.logical_and(self.data[s]['relative_time'] - min_time > 1e-3, self.data[s]['relative_time'] - max_time < 1e-3)]
            self.data[s]['relative_time'] -= min_time

        start_camera_index = self.data['camera'].index[0]-1
        stop_camera_index = self.data['camera'].index[-1]
        self.offset = start_camera_index
        for image in ['rgb', 'depth']:
            self.images[image] = self.images[image][start_camera_index:stop_camera_index]

        
    def export(self, folder, indexes):
        export_folder = join(self.exp_folder, folder)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        start_index = indexes['camera'][0]
        stop_index = indexes['camera'][1]
        cut_camera_data = self.data['camera'].iloc[start_index:stop_index+1]
        cut_camera_data.to_csv(join(export_folder, 'camera.csv'))
        print('Camera data file exported')
        cut_data = self.get_window_data(indexes)
        # export all csv
        for key, value in cut_data.items():
            value.to_csv(join(export_folder, key + '.csv'), index=False)
            print(key + ' data file exported')
        # copy calibration file if it exists
        for i in range(1, 3):
            calibration_file = 'FingerTPS_EPFL' + str(i) + '-cal.txt'
            if os.path.exists(join(self.exp_folder, calibration_file)):
                print('calibration file ' + calibration_file + ' exported')
                copyfile(join(self.exp_folder, calibration_file), join(export_folder, calibration_file))
        self.export_video(export_folder, start_index, stop_index)
        print('Export complete')

    def export_video(self, folder, start_index, stop_index):
        for t in ['rgb', 'depth']:
            original_video = cv2.VideoCapture(join(self.exp_folder, t + '.avi'))
            cut_video = cv2.VideoWriter(join(folder, t + '.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
            for i in range(self.offset + stop_index + 1):
                _, frame = original_video.read()
                if i < self.offset + start_index:
                    continue
                cut_video.write(frame)
            print(t + ' video file exported')
            original_video.release()
            cut_video.release()
    """
    
    