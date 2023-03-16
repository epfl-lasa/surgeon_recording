from threading import Thread, Event, Lock
import os
from os.path import join
import time
import keyboard
from subprocess import Popen, PIPE 
from shutil import copyfile

#from surgeon_recording.sensor_handlers.optitrack_handler_new import OptitrackHandlerNew
from surgeon_recording.sensor_handlers.recorder_v2_PDM.optitrack_handler_new2 import OptitrackHandlerNew2
# from surgeon_recording.sensor_handlers.recorder_v2_PDM.emg_handler_new import EMGHandler_new
from surgeon_recording.sensor_handlers.recorder_v2_PDM.emg_handler import EMGHandler
from surgeon_recording.sensor_handlers.recorder_v2_PDM.tps_calib import TPScalibration
from surgeon_recording.emg_calibration.calib_app import openApp
from surgeon_recording.sensor_handlers.recorder_v2_PDM.gopro_handler import GoProHandler


class RecorderNew():
    def __init__(self):
        self.duration = 100
        
        self.lock = ()

        # TODO : read this from file instead of input every time 
        self.folder_input = input('Name of folder : ')
        self.subject_nb = input('subject nb : ')
        self.task_input = input('run nb (ex 1) : ')

        self.folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb, self.task_input)
     
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.csv_path_optitrack1 = join(self.folder, "optitrack_stats.csv")
        self.csv_path_optitrack2 = join(self.folder, "optitrack.csv")
        self.csv_path_tps_raw = join(self.folder, "TPS_recording_raw.csv")
        self.csv_path_tps_cal = join(self.folder, "TPS_calibrated.csv")
        self.csv_path_emg = join(self.folder, "emg_duration_task.csv")
        self.csv_path_emg_cal = join(self.folder, "emg_duration_calibration.csv")
        self.csv_path_gopro = join(self.folder, "gopro_duration.csv")

    
    def start_threads(self):

        self.copy_calibration_files()

        # self.gopro_thread()

        self.stop_event = Event()
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()
        self.lock = Lock()

        time.sleep(5)

        recording_thread_tps = Thread(target=self.tps_thread)
        recording_thread_tps.start()

        time.sleep(5)

        recording_thread_emg = Thread(target=self.emg_thread)
        recording_thread_emg.start()

    def gopro_thread(self):
        # Start recording with go pro
        # WARNING: If prints 'Waking up...' in console -> CONNECT GOPRO WITH WIFI
        gp_handler = GoProHandler(self.csv_path_gopro)
        gp_handler.start_gopro()

    def optitrack_thread(self):
        is_looping = True
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

        handler_emg = EMGHandler(self.csv_path_emg)
        handler_emg.write_config_file(self.folder_input,self.subject_nb, self.task_input, "task")
        handler_emg.start_emg()
 
        while is_looping_emg is True:
            # Wait for closing signal
            
            if keyboard.is_pressed('q'):
                print('goodbye emg')
                is_looping_emg = False
                handler_emg.shutdown_emg()
                #time.sleep(5)
                #raise Exception('Exiting')

    def emg_calib(self):
        # Start emgAcquire recording
        handler_emg_calib = EMGHandler(self.csv_path_emg_cal)
        handler_emg_calib.write_config_file(self.folder_input,self.subject_nb, self.task_input, "calibration")
        handler_emg_calib.start_emg()

        # Call calibraiton app
        openApp(handler_emg_calib)

    def tps_thread(self):
        # Start WatchCapture to record TPS
        filename = "/Users/LASA/Documents/Recordings/SAHR_data_recording-master_test/bin/x64/WatchCapture.exe"
        proc = Popen([filename], stdin = PIPE, text=True)

        # Pass folder path to WatchCapture.exe
        proc.stdin.write(self.folder_input+"\n")
        proc.stdin.write(self.subject_nb+"\n")
        proc.stdin.write(self.task_input+"\n")

        # Pass configuration file number -> always 2
        proc.stdin.write("2\n")

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

            if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 5000: 
                copyfile(join(calibration_dir, calibration_file), join(destination_dir, calibration_file))
                print("OK: " + calibration_file + ' copied in config folder')
            else:
                print("WARNING: calibration file " + calibration_file+ " not copied in config folder, too old")
            
            if os.path.exists(join(destination_dir_tps, calibration_file)):
                os.remove(join(destination_dir_tps, calibration_file))

            if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 5000: # file not older than 30 minutes
                copyfile(join(calibration_dir, calibration_file), join(destination_dir_tps, calibration_file))
                print("OK: " + calibration_file + ' copied in data folder')
            else:
                print("WARNING: calibration file" + calibration_file + " not copied in data folder, too old")

    

def main():
    recorder = RecorderNew()

    # Optional EMG calibration (in case of crash)
    calibrate_emg = input("Calibrate EMG ? [y/n] \n")
    if calibrate_emg == 'y' or calibrate_emg == 'Y' or calibrate_emg == 'yes':
        recorder.emg_calib()
    else :
        print("Skipped EMG calibration. \n")
    
    input("Waiting for input : PRESS ENTER TO START. \n")
    recorder.start_threads()
    

if __name__ == '__main__':
    main()