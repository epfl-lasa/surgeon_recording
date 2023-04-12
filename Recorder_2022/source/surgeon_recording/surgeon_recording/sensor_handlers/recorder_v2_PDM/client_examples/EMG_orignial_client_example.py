#!/usr/bin/env python

import os
import sys
import pathlib
import numpy as np
import time
import matplotlib.pyplot as plt


# directory of the emgAcquireClient python_module 
#if sys.platform == 'linux':
#    emgAquire_dir = str(pathlib.Path().absolute()) + "/../python_module"
#else:
#    emgAquire_dir = str(pathlib.Path().absolute()) + "\\..\\python_module"

emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)

# import the module
import emgAcquireClient


# define number of channels to acquire
nb_ch = 6

# create an emgClient object for acquiring the data
emgClient = emgAcquireClient.emgAcquireClient(nb_channels=nb_ch)

# create a numpy array to contain all the data
all_Data = np.array([], dtype=np.float32).reshape(6,0)

# initialize the node
init_test = emgClient.initialize()

if init_test<0:
    print("unable to initialize")
    exit()

# start the acquisition
emgClient.start()

# get current time
t_time = time.time()

# array for keeping the timings
timings = np.array([], dtype=np.float)
freq_vect = []

while True:

    try:
        # acquire the signals from the buffer
        emg_data = emgClient.getSignals()

        # append the array with the new data
        all_Data = np.hstack((all_Data, emg_data))

        # keep the updating period
        timings = np.append(timings, time.time() - t_time)
        freq_vect.append(1/timings[-1])

        # reset the timer
        t_time = time.time()
        
    # if Ctrl+C is pressed interrupt the loop
    except KeyboardInterrupt:
            break

# shutdown the acquisition node
emgClient.shutdown()

# print statistics and the size of the acquired data
print(str(np.mean(timings)) + " \pm " + str(np.std(timings)))
print(all_Data.shape)


fig, ax = plt.subplots()

ax.plot(timings)
#ax.set_ylim([-1000, 1000])

plt.show()


