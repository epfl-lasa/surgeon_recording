from importlib.abc import ResourceReader
import numpy as np
import zmq
import csv
from threading import Thread, Event, Lock
import os
from os.path import join
import time
import json
import keyboard
import subprocess
from shutil import copyfile

#from surgeon_recording.sensor_handlers.optitrack_handler_new import OptitrackHandlerNew
from surgeon_recording.sensor_handlers.recorder_v2_PDM.optitrack_handler_new2 import OptitrackHandlerNew2
from surgeon_recording.sensor_handlers.recorder_v2_PDM.emg_handler_new import EMGHandler_new
from surgeon_recording.sensor_handlers.recorder_v2_PDM.tps_calib import TPScalibration


class RecorderNew():
    def __init__(self):
        self.duration = 100
        
        self.lock = ()
        self.folder_input = input('Name of folder')
        self.subject_nb = input('subject nb')
        self.task_input = input('run nb (ex 1)')

        #self.folder = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder"
        self.folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb, self.task_input)

     
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        #self.csv_path_optitrack = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder/optitrack_1.csv"
        self.csv_path_optitrack1 = join(self.folder, "optitrack_stats.csv")
        self.csv_path_optitrack2 = join(self.folder, "optitrack.csv")
        self.csv_path_tps_raw = join(self.folder, "TPS_recording_raw.csv")
        self.csv_path_tps_cal = join(self.folder, "TPS_calibrated.csv")
        self.csv_path_emg1 = join(self.folder, "emg.csv")
        self.csv_path_emg_cal = join(self.folder, "emg.csv")

        self.copy_calibration_files()

    

    def start_threads(self):

        self.stop_event = Event()
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()
        self.lock = Lock()

        time.sleep(5)

        recording_thread_tps = Thread(target=self.tps_thread)
        recording_thread_tps.start()

        time.sleep(25)

        recording_thread_emg = Thread(target=self.emg_thread)
        recording_thread_emg.start()


    def optitrack_thread(self):
        is_looping = True
        start_time_loop = time.time()
        #handler_opti = OptitrackHandlerNew(self.csv_path_optitrack)
        handler_opti = OptitrackHandlerNew2(self.csv_path_optitrack1,self.csv_path_optitrack2 )

        print("Hello optitrack")
        while is_looping is True:
            if keyboard.is_pressed('q'):
                print('goodbye optitrack ')
                is_looping = False
                handler_opti.shutdown_optitrack()
                #time.sleep(5)
                #raise Exception('Exiting')

    
    def emg_thread(self): 
        is_looping_emg = True
        handler_emg = EMGHandler_new(self.csv_path_emg1)

        while is_looping_emg is True:
            handler_emg.acquire_data_emg()
            
            if keyboard.is_pressed('q'):
                print('goodbye emg')
                is_looping_emg = False
                handler_emg.shutdown_emg()
                #time.sleep(5)
                #raise Exception('Exiting')
    
    def emg_calib(self):
        is_looping_emg = True
        print("Starting EMG Calibration, press 'q' when finished")
        handler_emg = EMGHandler_new(self.csv_path_emg_cal)

        while is_looping_emg is True:
            handler_emg.acquire_data_emg()
            
            if keyboard.is_pressed('q'):
                print('Stopped emg Calibration')
                is_looping_emg = False
                handler_emg.shutdown_emg()
                time.sleep(5)
                #raise Exception('Exiting')

    def tps_thread(self): 
        filename = "/Users/LASA/Documents/Recordings/SAHR_data_recording-master_test/bin/x64/WatchCapture.exe"
        proc = subprocess.run([filename])

        if os.path.exists(self.csv_path_tps_raw):
            calib_tps = TPScalibration(folder_path = self.folder, csv_path = self.csv_path_tps_cal, folder_input = self.folder_input, subject_nb=self.subject_nb, csv_raw_data=self.csv_path_tps_raw)

        else:
            print("WARNING: CALIBRATION NOT OK (raw file not found")



    def copy_calibration_files(self):
        
        calibration_dir = r'C:\Program Files\Pressure Profile Systems\Chameleon TVR\setup'
        destination_dir = join('source', 'surgeon_recording', 'config')

        destination_dir_tps = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb, self.task_input, "calib")
        if not os.path.exists(destination_dir_tps):
            os.makedirs(destination_dir_tps)
      
        for i in range(1, 3):
            calibration_file = 'FingerTPS_EPFL' + str(i) + '-cal.txt'
            # first remove old calibration files
            if os.path.exists(join(destination_dir, calibration_file)):
                os.remove(join(destination_dir, calibration_file))

            if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 2000: 
                copyfile(join(calibration_dir, calibration_file), join(destination_dir, calibration_file))
                print("OK: " + calibration_file + ' copied in config folder')
            else:
                print("WARNING: calibration file " + calibration_file+ " not copied in config folder, too old")
            
            if os.path.exists(join(destination_dir_tps, calibration_file)):
                os.remove(join(destination_dir_tps, calibration_file))

            if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 2000: # file not older than 10 minutes
                copyfile(join(calibration_dir, calibration_file), join(destination_dir_tps, calibration_file))
                print("OK: " + calibration_file + ' copied in data folder')
            else:
                print("WARNING: calibration file" + calibration_file + " not copied in data folder, too old")

    

    

def main():
    recorder = RecorderNew()
    recorder.emg_calib()
    recorder.start_threads()
    

if __name__ == '__main__':
    main()