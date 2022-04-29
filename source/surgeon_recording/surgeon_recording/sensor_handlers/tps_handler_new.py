import zmq
import time
import numpy as np
import os
from os.path import join
from shutil import copyfile
import itertools
from sklearn.linear_model import LinearRegression
from surgeon_recording.sensor_handlers.sensor_handler import SensorHandler

class TPSHandlerNew(object):
    def __init__(self, parameters):
        ip = "127.0.0.1"
        port = 4242
        self.selected_fingers = [0]

        # load the calibrations
        calib1, calib2 = TPSHandlerNew.load_calibrations()
        self.calibrations = calib1 + calib2

        
        # socket for receiving sensor data
        print("socket initializing")
        context = zmq.Context()
        self.data_socket = context.socket(zmq.SUB)
        self.data_socket.setsockopt(zmq.CONFLATE, 1)
        self.data_socket.connect("tcp://%s:%s" % (ip, port))
        self.data_socket.setsockopt( zmq.SUBSCRIBE, b"" )
        print("socket initialized")

    def load_calibrations():
        filepath = os.path.abspath(os.path.dirname(__file__))
        config_folder = join(filepath, '..', '..', 'config')
        calibration_file1 = join(config_folder, 'FingerTPS_EPFL1-cal.txt')
        calibration_file2 = join(config_folder, 'FingerTPS_EPFL2-cal.txt')
        calib1 = TPSHandlerNew.read_calibration_file(calibration_file1)
        calib2 = TPSHandlerNew.read_calibration_file(calibration_file2)
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
                    calibration_factors.append(TPSHandlerNew.compute_calibration_factor(line))
        return calibration_factors

    def compute_calibration_factor(data):
        # data are stored every two elements after removing first element
        y = np.array(data[1::2]).astype(np.float64)
        x = np.array(data[2::2]).astype(np.float64).reshape(-1, 1)
        return LinearRegression().fit(x, y)


    """def setup_recording(self, recording_folder, start_time):
        super().setup_recording(recording_folder, start_time)
        # copy the calibration files
        filepath = os.path.abspath(os.path.dirname(__file__))
        config_folder = join(filepath, '..', '..', 'config')
        for i in range(1, 3):
            filename = 'FingerTPS_EPFL' + str(i) + '-cal.txt'
            calibration_file = join(config_folder, filename)
            if os.path.exists(calibration_file):
                copyfile(calibration_file, join(recording_folder, filename))"""


    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        if not self.simulated:
            tmp = np.array([float(x) for x in self.data_socket.recv_string().split(',')])
        else:
            tmp = self.generate_fake_data(12)
        for i, f in enumerate(self.selected_fingers):
            raw_value = tmp[f] if f < 6 else tmp[f+3]
            if raw_value < 1e-2:
                return []
            calibrated_value = self.calibrations[i].predict([[raw_value]])[0] if i < len(self.calibrations) else raw_value
            data.append(calibrated_value)
            data.append(raw_value)
        self.index = data[0]
        return data

    """def shutdown(self):
        super().shutdown()
        if not self.simulated:
            self.data_socket.close()
        print('tps closed cleanly')"""


def main(args=None):
    
    print(a)
if __name__ == '__main__':
    main()