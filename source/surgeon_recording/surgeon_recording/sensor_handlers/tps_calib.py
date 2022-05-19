import zmq
import time
import numpy as np
import os
from os.path import join
from shutil import copyfile
import csv
from sklearn.linear_model import LinearRegression
import json
import itertools


class TPScalibration:
    #def __init__(self, csv_path, folder_input, subject_nb, csv_raw_data):
    def __init__(self):
        self.folder_input = "1"
        self.subject_nb = "1"
        #self.subject_nb = subject_nb
        #self.csv_path = csv_path
        #self.folder_input = folder_input
        #self.csv_raw_data = csv_raw_data

        self.folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb)
        self.csv_raw_data  = join(self.folder, "TPS_recording_raw.csv")
        self.csv_path = join(self.folder, "TPS_calibrated.csv")

        self.parameters_tps=[]
        self.get_parameters_tps()
        
        self.selected_fingers = [f['streaming_id'] for f in self.parameters_tps['fingers']]

        self.data = []


        # load the calibrations
        calib1, calib2 = self.load_calibrations()
        self.calibrations = calib1 + calib2

        
        print(self.folder_input)
        
        

        self.f = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.f)
        header = ["index", "absolute time", "relative time","cal data", "raw data"]
        self.writer.writerow(header)

    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
            config = json.load(paramfile)
        if not sensor_name in config.keys():
            config[sensor_name] = {}
            config[sensor_name]['status'] = 'off'
        return config[sensor_name]

    def get_parameters_tps(self):
        self.parameters_tps = self.read_config_file('tps')
        if self.parameters_tps['status'] != 'off':
            self.parameters_tps.update({ 'header': list(itertools.chain.from_iterable((f['label'] + '_calibrated', f['label'] + '_raw') for f in self.parameters_tps['fingers'])) })
        return self.parameters_tps

    def load_calibrations(self):
        filepath = os.path.abspath(os.path.dirname(__file__))
        calib_folder = join("/Users/LASA/Documents/Recordings/surgeon_recording/exp_data", self.folder_input, self.subject_nb, "calib")

        print(calib_folder)
        calibration_file1 = join(calib_folder, 'FingerTPS_EPFL1-cal.txt')
        print(calibration_file1)
        calibration_file2 = join(calib_folder, 'FingerTPS_EPFL2-cal.txt')
        calib1 = self.read_calibration_file(calibration_file1)
        calib2 = self.read_calibration_file(calibration_file2)
        return calib1, calib2

    def read_calibration_file(self, calibration_file):
        # get the parameters to know which are the sensors to read
        calibration_factors = []
        if os.path.exists(calibration_file):
            file = open(calibration_file, 'r')
            lines = file.readlines()
            # only read the lines counting as selected fingers
            
            for i in self.selected_fingers:
                line = lines[i+1].split('\t')[:-1]
                # if there is calibration data
                if len(line) > 1:
                    calibration_factors.append(self.compute_calibration_factor(line))
        return calibration_factors

    def compute_calibration_factor(data):
        # data are stored every two elements after removing first element
        y = np.array(data[1::2]).astype(np.float64)
        x = np.array(data[2::2]).astype(np.float64).reshape(-1, 1)
        return LinearRegression().fit(x, y)

    def read_tps_raw_file(self, raw_data_file):

        if os.path.exists(raw_data_file):
            file = open(raw_data_file, 'r')
            lines = file.readlines()
            for i in range(len(lines)):
                self.data.append(lines[i])
                for j, f in enumerate(self.selected_fingers):
                    raw_value = lines[i][f+3] #if f < 6 else tmp[f+3]
                    if raw_value < 1e-2:
                        self.data.append(0)
                    else:
                        calibrated_value = self.calibrations[j].predict([[raw_value]])[0] if j < len(self.calibrations) else raw_value
                        self.data.append(calibrated_value)
                    row = self.data
                    self.writer.writerow(row)
        
       



def main():
    
    tps_calib = TPScalibration()
    tps_calib.read_tps_raw_file(tps_calib.csv_raw_data)
    
    

if __name__ == '__main__':
    main()