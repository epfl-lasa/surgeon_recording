from threading import Thread, Event, Lock
import os
import sys
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

path_to_plot_module = join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_plot_module)
from data_analysis.modules.emg_utils import *
from data_analysis.modules.tps_utils import * 

class Recorder():
    def __init__(self):

        # Read data structure info from json file 
        self.filepath = os.path.abspath(os.path.dirname(__file__))
        f = open(join(self.filepath, 'config', 'data_dir_info.json'))
        data_dir_info = json.load(f)
        self.folder_input = str(data_dir_info["folder_name"])
        self.subject_nb = str(data_dir_info["subject_nb"])
        self.task_input = str(data_dir_info["run_nb"])
     
        self.folder = join(self.filepath, '..', 'exp_data', self.folder_input, self.subject_nb, self.task_input, 'sensor_test')

        print("Data folder for this recording is : \n", self.folder)

        self.update_data_paths(self.folder)

        # update folder for tps_calib
        self.folder = join(self.filepath, '..', 'exp_data', self.folder_input, self.subject_nb, self.task_input)
        
        # Set path for emg calibration to be in correct folder      
        self.csv_path_emg_cal = join(self.folder, "emg_duration_calibration.csv")
        self.csv_path_tps_raw = join(self.folder, "TPS_recording_raw.csv") # Always in this folder regardless of sensor_test (due to WatchCapture.exe)

    def update_data_paths(self, folder):
        # Set up path to csv for test recording and task recording 
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.csv_path_optitrack_stats = join(folder, "optitrack_stats.csv")
        self.csv_path_optitrack_data = join(folder, "optitrack.csv")
        self.csv_path_tps_cal = join(folder, "TPS_calibrated.csv")
        self.csv_path_emg_task = join(folder, "emg_duration_task.csv")
        self.csv_path_gopro = join(folder, "gopro_duration.csv")

    def test_sensors_and_plot(self):
        
        is_testing = True
        sensor_test = True

        self.copy_calibration_files()

        time.sleep(1)

        self.stop_event = Event()
        self.lock = Lock()
        
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()

        time.sleep(2) 

        recording_thread_tps = Thread(target=self.tps_thread, args=[sensor_test])
        recording_thread_tps.start()

        time.sleep(8)

        recording_thread_emg = Thread(target=self.emg_thread, args=[sensor_test])
        recording_thread_emg.start()

        while is_testing is True:
            # Wait for closing signal
            
            if keyboard.is_pressed('q'):
                print('Stopping recording, now plotting...')
                is_testing = False

                time.sleep(10)

                # call plot functions here 
                self.plot_emg_tps_opti(sensor_test=True)
    
    def plot_emg_tps_opti(self, sensor_test=False):
        # EMG + TPS
        emg_placement = 'Jarque-Bou'

        cleantpsDF = clean_tps(self.csv_path_tps_cal)
        if sensor_test:
            cleanemgDF = clean_emg(join(self.folder,"sensor_test", "emg_data_task.csv"), emg_placement)
        else:
            cleanemgDF = clean_emg(join(self.folder, "emg_data_task.csv"), emg_placement)  

        plot_tpsDF(cleantpsDF, title_str='Calibrated TPS', time_for_plot='relative time', nb_rec_channels=6, show_plot=False)
        start_time = get_starting_time(cleantpsDF)
        plot_emgDF(cleanemgDF, title_str='Raw EMG', time_for_plot='relative time', nb_rec_channels=16, plot_from_time=start_time)
        
        # PLOTS BOTH TOGETHER -> more compact but too small to read probably
        # time_range = [40, 440] # seconds
        # labels_for_emg = ['Extensor Digitorum L',
        #         'Flexor Digitorum Superficialis L',
        #         'Abductor Pollicis longus and extensor pollicis brevis L',
        #         'Abductor Pollicis Brevis L']

        # labels_for_tps = ['Left Index', 'Left Thumb']

        # plot_tps_emg(cleantpsDF, cleanemgDF, labels_for_tps, labels_for_emg, time_range)

        # OPTITRACK
        optiDF = pd.read_csv(self.csv_path_optitrack_data, header=0)    
        nb_frames_total = len(optiDF.index)
        nb_zero_tweezers = (optiDF['tweezers_x'] == 0).sum(axis=0)
        nb_zero_needle_holder = (optiDF['needle_holder_x'] == 0).sum(axis=0)
        print("TOTAL nb of frames : ", nb_frames_total)
        print("Missed frames tweezers : ", nb_zero_tweezers, f",  {100*nb_zero_tweezers/nb_frames_total:.2f}% " )
        print("Missed frames needle hodler : ", nb_zero_needle_holder, f", { 100*nb_zero_needle_holder/nb_frames_total:.2f}%")

        print("\n FINISHED PLOTTING-> CLOSE PLOTS TO CONTINUE\n")

    def start_threads(self):

        # update data folder path and csv paths
        self.update_data_paths(self.folder)

        time.sleep(1)

        self.copy_calibration_files()

        time.sleep(1)

        is_recording = True

        self.stop_event = Event()
        # recording_thread_gopro = Thread(target=self.gopro_thread)
        # recording_thread_gopro.start()
        self.lock = Lock()
        
        recording_thread_opti = Thread(target=self.optitrack_thread)
        recording_thread_opti.start()

        time.sleep(2)        
        recording_thread_tps = Thread(target=self.tps_thread)
        recording_thread_tps.start()

        time.sleep(8)

        recording_thread_emg = Thread(target=self.emg_thread)
        recording_thread_emg.start()

        while is_recording is True:
            # Wait for closing signal
            
            if keyboard.is_pressed('q'):
                print('Stopping recording, now plotting...')
                is_recording = False

                time.sleep(10)

                # call plot functions here 
                self.plot_emg_tps_opti()

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
        handler_opti = OptitrackHandler(self.csv_path_optitrack_stats,self.csv_path_optitrack_data )

        print("Hello optitrack")
        while is_looping is True:
            if keyboard.is_pressed('q'):
                print('Goodbye optitrack ')
                is_looping = False
                handler_opti.shutdown_optitrack()
    
    def emg_thread(self, sensor_test=False): 
        is_looping_emg = True

        handler_emg = EMGHandler(self.csv_path_emg_task)
        handler_emg.write_config_file(self.folder_input,self.subject_nb, self.task_input, "task", sensor_test)
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
        # closing the app kills EMG recording

    def tps_thread(self, sensor_test=False):
        # Start WatchCapture to record TPS
        filename = "/Users/LASA/Documents/Recordings/SAHR_data_recording-master_test/bin/x64/WatchCapture.exe"
        run([filename])

        if os.path.exists(self.csv_path_tps_raw):
            if sensor_test:
                # copy raw data to sensor_test folder for safety 
                copyfile(self.csv_path_tps_raw, join(self.folder,"sensor_test", "TPS_recording_raw.csv"))
                # make folder tps_calib in sensor_test and copy calibration files there
                if not os.path.exists(join(self.folder, "sensor_test", "tps_calib")):
                    os.makedirs(join(self.folder, "sensor_test", "tps_calib"))
                calibration_file = 'FingerTPS_EPFL2-cal.txt'
                copyfile(join(self.folder, "tps_calib", calibration_file), join(self.folder, "sensor_test", "tps_calib", calibration_file))

            calib_tps = TPScalibration(folder_path = self.folder, csv_path = self.csv_path_tps_cal, folder_input = self.folder_input, subject_nb=self.subject_nb, csv_raw_data=self.csv_path_tps_raw)
            
            if sensor_test:
                # Remove raw
                os.remove(self.csv_path_tps_raw)
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
        # if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 20000: 
        copyfile(join(calibration_dir, calibration_file), join(destination_dir, calibration_file))
        print("OK: " + calibration_file + ' copied in config folder')
        # else:
        #     print("WARNING: calibration file " + calibration_file+ " not copied in config folder, too old")
        
        if os.path.exists(join(destination_dir_tps, calibration_file)):
            os.remove(join(destination_dir_tps, calibration_file))

        # Copy to exp_data folder, inside correct run 
        # if time.time() - os.path.getmtime(join(calibration_dir, calibration_file)) < 20000: # file not older than 30 minutes
        copyfile(join(calibration_dir, calibration_file), join(destination_dir_tps, calibration_file))
        print("OK: " + calibration_file + ' copied in data folder')
        # else:
        #     print("WARNING: calibration file " + calibration_file + " not copied in data folder, too old")

def main():
    recorder = Recorder()

    # Optional EMG calibration (in case of crash)
    calibrate_emg = input("Calibrate EMG ? [y/n] \n")
    if calibrate_emg == 'y' or calibrate_emg == 'Y' or calibrate_emg == 'yes':
        recorder.emg_calib()
    else :
        print("Skipped EMG calibration. \n")

    input("Do the TPS calibration using Chameleon software now ! \n Then press Enter to continue. \n")
    test_sensors = input("Test sensors and plot ? [y/n] \n")
    if test_sensors == 'y' or test_sensors == 'Y' or test_sensors == 'yes':
        recorder.test_sensors_and_plot()
    else : 
        print("SKipped sensor testing. \n")

    print("\n Make sure you are connected to the GOPRO's wifi !! \n")
    input("Redo the TPS calibration using Chameleon software now ! \n Then press Enter to continue. \n")
    
    recorder.start_threads()
    
if __name__ == '__main__':
    main()