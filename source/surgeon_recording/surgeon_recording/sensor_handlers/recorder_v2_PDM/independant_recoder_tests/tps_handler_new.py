
import zmq
import time
import numpy as np
import os
from os.path import join
from shutil import copyfile
import csv
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt

class TPSHandlerNew(object):
    def __init__(self):
        ip = "127.0.0.1"
        port = 4242
        self.selected_fingers = [0]
        self.data2 = []
        self.time_vect3 = []
        self.time_vect4 = []
        self.freq_vect3 = []
        self.count3 = 0

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

        self.csv_path = "/Users/LASA/Documents/Recordings/surgeon_recording/data/test_tps_new_recorder/test_1.csv"
        self.f = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.f)
        header = ["index", "absolute time", "relative time","cal data", "raw data"]
        self.writer.writerow(header)

    def load_calibrations():
        filepath = os.path.abspath(os.path.dirname(__file__))
        config_folder = r"C:\Users\LASA\Documents\Recordings\surgeon_recording\source\surgeon_recording\config"
        print(config_folder)
        calibration_file1 = join(config_folder, 'FingerTPS_EPFL1-cal.txt')
        print(calibration_file1)
        calibration_file2 = join(config_folder, 'FingerTPS_EPFL2-cal.txt')
        calib1 = TPSHandlerNew.read_calibration_file(calibration_file1)
        calib2 = TPSHandlerNew.read_calibration_file(calibration_file2)
        return calib1, calib2

    def read_calibration_file(calibration_file):
        # get the parameters to know which are the sensors to read
        calibration_factors = []
        if os.path.exists(calibration_file):
            file = open(calibration_file, 'r')
            lines = file.readlines()
            # only read the lines counting as selected fingers
            selected_fingers= [0]
            for i in selected_fingers:
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


    def acquire_data(self):
        absolute_time = time.time()
        data = [self.index + 1, absolute_time, absolute_time - self.start_time]
        self.count3 = self.count3 +1
        self.time_vect3.append(time.time())
        self.time_vect4.append(time.perf_counter())
        #if self.count3>1:
            #self.freq_vect3.append(1/(self.time_vect3[-1]-self.time_vect3[-2]))
        
        tmp = np.array([float(x) for x in self.data_socket.recv_string().split(',')])
      
        for i, f in enumerate(self.selected_fingers):
            raw_value = tmp[f] if f < 6 else tmp[f+3]
            if raw_value < 1e-2:
                #return []
                data.append(0)
                data.append(0)
            else:
                calibrated_value = self.calibrations[i].predict([[raw_value]])[0] if i < len(self.calibrations) else raw_value
                data.append(calibrated_value)
                data.append(raw_value)
        self.index = data[0]
        row = data
        self.writer.writerow(row)
        self.data2.append(data)

        if len(self.time_vect3) > 2 and self.time_vect3[-2] == self.time_vect3[-1]:
            print(f"Last two times equal, previous data is {self.data2[-2]}, current data is {self.data2[-1]}")

        return data


def main():
    csv_path2 = "/Users/LASA/Documents/Recordings/surgeon_recording/data/test_tps_new_recorder/test_1_time.csv"
    f2 = open(csv_path2, 'w', newline='')
    writer2 = csv.writer(f2)
    header2 = ["time with perf counter", "time with time()", "time with time but in loop", "time with counter in loop"]
    writer2.writerow(header2)
    duration = 30
    
    #freq = 10
    #dt = 1/freq

    tps_handler = TPSHandlerNew()
    
    tps_handler.index = 0
    is_looping = True
    tps_handler.start_time = time.time()
    count = 0
    
    
    time_vect2 = [time.time()]
    freq_vect1 = []

    start = time.perf_counter() 
    time_vect1 = [start]

    while is_looping:
        #time_1 = time.time()
        #print("tick")
        tps_handler.acquire_data()

        time_vect1.append(time.perf_counter())
        #t = time.perf_counter()
        time_vect2.append(time.time())
        row2 = [time_vect1[-1], time_vect2[-1],tps_handler.time_vect3[-1], tps_handler.time_vect4[-1]]
        writer2.writerow(row2)

        
        #time.sleep(dt- ((time.time() - tps_handler.start_time) % dt))

        """if time.time()-time_1 < dt:
            time.sleep(dt- ((time.time() - tps_handler.start_time) % dt))
            print("sleeping")"""

        """if time.perf_counter() - start - time_vect1[-1] < dt :
            time.sleep(dt- ((time.perf_counter() - start) % dt))
            print("sleeping")"""

        count = count +1 

        #while time.perf_counter() < start + count*dt:
            #pass

        if count > 1:
            freq_vect1.append(1/(time_vect1[-1]-time_vect1[-2]))
        
        if time.time() - tps_handler.start_time > duration:
            print("closing")
            is_looping = False
            tps_handler.data_socket.close()
            print(len(tps_handler.data2))
            print(count)
            tps_handler.f.close()
            f2.close()


    fig, ax = plt.subplots()

    ax.plot(freq_vect1[2:-1])
    #ax.set_ylim([freq-10, freq+10])

    fig, ax2 = plt.subplots()
    ax2.plot(tps_handler.freq_vect3[2:-1])

    


    plt.show()

if __name__ == '__main__':
    main()