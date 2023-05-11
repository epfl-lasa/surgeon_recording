from threading import Thread, Event, Lock
import os
from os.path import join
import time
import keyboard
import json
from subprocess import Popen, PIPE, check_output, run
from shutil import copyfile

# Import from sensor handlers and emg_calibration_app
from sensor_handlers.optitrack_handler import OptitrackHandler
from sensor_handlers.emg_handler import EMGHandler
from sensor_handlers.tps_calib import TPScalibration

from emg_calibration_app.calib_app import openApp
from sensor_handlers.gopro_handler import GoProHandler


class Recorder():
    def __init__(self):

        # Read data structure info from json file 
        filepath = os.path.abspath(os.path.dirname(__file__))
        f = open(join(filepath, 'config', 'data_dir_info.json'))
        data_dir_info = json.load(f)
        self.folder_input = str(data_dir_info["folder_name"])
        self.subject_nb = str(data_dir_info["subject_nb"])
        self.task_input = str(data_dir_info["run_nb"])
     
        self.folder = join(filepath, '..', 'exp_data', self.folder_input, self.subject_nb, self.task_input)

        print("Data folder for this recording is : \n", self.folder)

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

        # self.copy_calibration_files()

        time.sleep(1)

        self.stop_event = Event()
        # recording_thread_gopro = Thread(target=self.gopro_thread)
        # recording_thread_gopro.start()
        self.lock = Lock()
        
        # recording_thread_opti = Thread(target=self.optitrack_thread)
        # recording_thread_opti.start()

        # time.sleep(2)        
        recording_thread_tps = Thread(target=self.tps_thread)
        recording_thread_tps.start()

        time.sleep(8)

        recording_thread_emg = Thread(target=self.emg_thread)
        recording_thread_emg.start()


    def gopro_thread(self):
        # Start recording with go pro
        # WARNING: If prints 'Waking up...' in console -> CONNECT GOPRO WITH WIFI
        
        # Check wifi network
        devices = check_output(['netsh', 'wlan', 'show', 'network'])
        devices = devices.decode('ascii')
        devices = devices.replace("\r", "")
        print(devices)
        gp_wifi_name = "GP25728977"

        # Error message to ensure user connects gopro through wifi 
        if gp_wifi_name not in devices:
            input("\n \n Laptop's WIFI must be connected on GP25728977 -> Do this then press Enter to continue \n")

        gp_handler = GoProHandler(self.csv_path_gopro)
        gp_handler.start_gopro()

        print("Hello gopro")
        is_looping = True
        while is_looping is True:
            if keyboard.is_pressed('q'):
                print('Goodbye gopro ')
                is_looping = False
                gp_handler.shutdown_gopro()

    def optitrack_thread(self):
        is_looping = True
        handler_opti = OptitrackHandler(self.csv_path_optitrack1,self.csv_path_optitrack2 )

        print("Hello optitrack")
        while is_looping is True:
            if keyboard.is_pressed('q'):
                print('Goodbye optitrack ')
                is_looping = False
                handler_opti.shutdown_optitrack()
    
    def emg_thread(self): 
        is_looping_emg = True

        handler_emg = EMGHandler(self.csv_path_emg)
        handler_emg.write_config_file(self.folder_input,self.subject_nb, self.task_input, "task")
        handler_emg.start_emg()
 
        while is_looping_emg is True:
            # Wait for closing signal
            
            if keyboard.is_pressed('q'):
                print('Goodbye emg')
                is_looping_emg = False
                handler_emg.shutdown_emg()

    def emg_calib(self):
        # Start emgAcquire recording
        handler_emg_calib = EMGHandler(self.csv_path_emg_cal)
        handler_emg_calib.write_config_file(self.folder_input,self.subject_nb, self.task_input, "calibration")
        handler_emg_calib.start_emg()

        # Call calibration app
        openApp(handler_emg_calib)

    def tps_thread(self):
        # Start WatchCapture to record TPS
        filename = "/Users/LASA/Documents/Recordings/SAHR_data_recording-master_test/bin/x64/WatchCapture.exe"
        run([filename])

        if os.path.exists(self.csv_path_tps_raw):
            calib_tps = TPScalibration(folder_path = self.folder, csv_path = self.csv_path_tps_cal, folder_input = self.folder_input, subject_nb=self.subject_nb, csv_raw_data=self.csv_path_tps_raw)

        else:
            print("WARNING: CALIBRATION NOT OK (raw file not found)")

    def copy_calibration_files(self):
        
        calibration_dir = r'C:\Program Files\Pressure Profile Systems\Chameleon TVR\setup'
        destination_dir = join(os.path.dirname(__file__), 'config')

        destination_dir_tps = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb, self.task_input, "tps_calib")
        if not os.path.exists(destination_dir_tps):
            os.makedirs(destination_dir_tps)
      
        calibration_file = 'FingerTPS_EPFL2-cal.txt'
        # first remove old calibration files
        if os.path.exists(join(destination_dir, calibration_file)):
            os.remove(join(destination_dir, calibration_file))

        # Copy to config folder 
        if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 2000: 
            copyfile(join(calibration_dir, calibration_file), join(destination_dir, calibration_file))
            print("OK: " + calibration_file + ' copied in config folder')
        else:
            print("WARNING: calibration file " + calibration_file+ " not copied in config folder, too old")
        
        if os.path.exists(join(destination_dir_tps, calibration_file)):
            os.remove(join(destination_dir_tps, calibration_file))

        # Copy to exp_data folder, inside correct run 
        if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 2000: # file not older than 30 minutes
            copyfile(join(calibration_dir, calibration_file), join(destination_dir_tps, calibration_file))
            print("OK: " + calibration_file + ' copied in data folder')
        else:
            print("WARNING: calibration file " + calibration_file + " not copied in data folder, too old")

def main():
    recorder = Recorder()

    # Optional EMG calibration (in case of crash)
    calibrate_emg = input("Calibrate EMG ? [y/n] \n")
    if calibrate_emg == 'y' or calibrate_emg == 'Y' or calibrate_emg == 'yes':
        recorder.emg_calib()
    else :
        print("Skipped EMG calibration. \n")
    
    # TODO : Add start_test which will : 
    # start tps+emg+optitrack for 1 min
    # then plot everything when user press q (same as start_threads)


    print("\n Make sure you are connected to the GOPRO's wifi !! \n")
    input("Do the TPS calibration using Chameleon software now ! \n Then press Enter to continue. \n")
    
    recorder.start_threads()
    

if __name__ == '__main__':
    main()