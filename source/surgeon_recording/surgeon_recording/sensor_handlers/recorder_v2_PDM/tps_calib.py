import numpy as np
import os
from os.path import join
from shutil import copyfile
import csv
from sklearn.linear_model import LinearRegression
import json
import itertools
from csv import reader


class TPScalibration:
    def __init__(self, folder_path, csv_path, folder_input, subject_nb, csv_raw_data):
 
        self.folder_path = folder_path
        self.subject_nb = subject_nb
        self.csv_path = csv_path
        self.folder_input = folder_input
        self.csv_raw_data = csv_raw_data

        self.parameters_tps=[]
        self.get_parameters_tps()
        
        self.selected_fingers = [f['streaming_id'] for f in self.parameters_tps['fingers']]
        self.names_fingers = [k['label'] for k in self.parameters_tps['fingers']]

        self.data = []

        # load the calibrations
        #calib1, calib2 = self.load_calibrations()
        calib2 = self.load_calibrations()

        #self.calibrations = calib1 + calib2
        self.calibrations =  calib2
        
        self.f = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.f)
        print("calibration csv")
        self.read_tps_raw_file(self.csv_raw_data)


    def read_config_file(self, sensor_name):
        filepath = os.path.abspath(os.path.dirname(__file__))
        with open(join(filepath, '..', '..','..', 'config', 'sensor_parameters.json'), 'r') as paramfile:
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
        calib_folder = join(self.folder_path, "calib")
        print(calib_folder)

        if not os.path.exists(calib_folder):
            print("no calibration file")
            raise Exception('Exiting')
        #calibration_file1 = join(calib_folder, 'FingerTPS_EPFL1-cal.txt')
        calibration_file2 = join(calib_folder, 'FingerTPS_EPFL2-cal.txt')
        #calib1 = self.read_calibration_file(calibration_file1)
        calib2 = self.read_calibration_file(calibration_file2)
        #return calib1, calib2
        return calib2

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

    def compute_calibration_factor(self, data):
        # data are stored every two elements after removing first element
        y = np.array(data[1::2]).astype(np.float64)
        x = np.array(data[2::2]).astype(np.float64).reshape(-1, 1)
        return LinearRegression().fit(x, y)

    def read_tps_raw_file(self, raw_data_file):
        if os.path.exists(raw_data_file):
            file = open(raw_data_file, 'r')
        else:
            print("no raw data file")
            raise Exception('Exiting')
            
        # open file in read mode
        with file as read_obj:
            cnt = 0
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Iterate over each row in the csv using reader object
            for line in csv_reader:
                # row variable is a list that represents a row in csv
                for i in range(len(line)):
                    self.data.append(line[i])
                
                #first line: add the names of the calibrated fingers
                if cnt == 0:
                    for j, f in enumerate(self.selected_fingers):                        
                        self.data.append("elem " + str(f) + " calibrated " + self.names_fingers[j])
                    

                else:
                    for j, f in enumerate(self.selected_fingers):
                        # elem 0,1,2 in columns 4,5,6 and elements 6,7,8 in columns 12,13,14
                        # in the raw csv file, elements 0,1,2 are the same as 6,7,8 and elements 3,4,5 are the same as elements 9,10,11 (when we have sensors only on 0,1,2,6,7,8 channels)
                        # (not exact same value (sometimes 1 digit difference) but when we plot we see it is the same data)
                        # WARNING: not sure why, so if we add other channels we should check that we take the good columns (maybe f+3 not 6 in this case when f>6)
                        raw_value = float(line[f+3]) if f < 6 else float(line[f+6])
                        # if raw value too low it corresponds to a missing data so add an empty calibrated data
                        if raw_value < 1e-2:
                            self.data.append("")
                        else:
                            # use the calibration factors (in self.calibration) to predict the calibrated outputs
                            # put raw output if we don't have the caliration factor 
                            calibrated_value = self.calibrations[j].predict([[raw_value]])[0] if j < len(self.calibrations) else raw_value
                            self.data.append(calibrated_value)
                
                row = self.data
                self.writer.writerow(row)
                cnt = cnt +1
                self.data = []
        
       



def main():
    return

if __name__ == '__main__':
    main()