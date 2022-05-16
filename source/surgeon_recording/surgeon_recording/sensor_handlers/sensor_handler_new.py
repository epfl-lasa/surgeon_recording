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

#from surgeon_recording.sensor_handlers.optitrack_handler_new import OptitrackHandlerNew
from surgeon_recording.sensor_handlers.optitrack_handler_new2 import OptitrackHandlerNew2
from surgeon_recording.sensor_handlers.emg_handler_new import EMGHandler_new


class RecorderNew():
    def __init__(self):
        self.duration = 100
        
        self.lock = ()
        self.folder_input = input('Name of folder')
        self.subject_nb = input('subject nb')

        #self.folder = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder"
        self.folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder", self.folder_input, self.subject_nb)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        #self.csv_path_optitrack = "/Users/LASA/Documents/Recordings/surgeon_recording/data/new_recorder/optitrack_1.csv"
        self.csv_path_optitrack1 = join(self.folder, "optitrack2_stats.csv")
        self.csv_path_optitrack2 = join(self.folder, "optitrack2_2.csv")

        self.csv_path_emg1 = join(self.folder, "emg.csv")

    

    def start_threads(self):

        #self.stop_event = Event()
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()
        self.lock = Lock()

        recording_thread_emg = Thread(target=self.emg_thread)
        recording_thread_emg.start()

        time.sleep(10)

        recording_thread_tps = Thread(target=self.tps_thread)
        recording_thread_tps.start()


    def optitrack_thread(self):
        is_looping = True
        start_time_loop = time.time()
        #handler_opti = OptitrackHandlerNew(self.csv_path_optitrack)
        handler_opti = OptitrackHandlerNew2(self.csv_path_optitrack1,self.csv_path_optitrack2 )

        
        while is_looping is True:

            #handler_opti.write_optitrack_data()
            """if time.time() - start_time_loop > self.duration:
                is_looping = False
                handler_opti.shutdown_optitrack()"""

            """try:
                pass

            except KeyboardInterrupt:
                is_looping = False
                handler_opti.shutdown_optitrack()
                print("Raising SystemExit optitrack thread")
                raise SystemExit"""

            if keyboard.is_pressed('q'):
                print('goodbye optitrack ')
                is_looping = False
                handler_opti.shutdown_optitrack()
                raise Exception('Exiting')

    
    def emg_thread(self): 
        is_looping_emg = True
        start_time_loop_emg= time.time()
        handler_emg = EMGHandler_new(self.csv_path_emg1)

        while is_looping_emg is True:
            handler_emg.acquire_data_emg()
            """if time.time() - start_time_loop_emg > self.duration:
                is_looping_emg = False
                handler_emg.shutdown_emg()"""

            """try:
                #handler_emg.acquire_data_emg()
                pass

            except KeyboardInterrupt:
                is_looping_emg = False
                handler_emg.shutdown_emg()
                print("Raising SystemExit emg tread")
                raise SystemExit"""

            

            if keyboard.is_pressed('q'):
                print('goodbye emg')
                is_looping_emg = False
                handler_emg.shutdown_emg()
                raise Exception('Exiting')

    def tps_thread(self): 
        filename = "/Users/LASA/Documents/Recordings/SAHR_data_recording/bin/x64/WatchCapture.exe"
        proc = subprocess.run([filename])

    




def main():
    recorder = RecorderNew()
    recorder.start_threads()
    
if __name__ == '__main__':
    main()