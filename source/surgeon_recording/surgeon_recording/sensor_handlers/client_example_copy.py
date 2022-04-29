#!/usr/bin/env python

import os
import sys
import pathlib
import numpy as np
import time
import matplotlib.pyplot as plt
import csv

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
nb_ch = 8

# create an emgClient object for acquiring the data
emgClient = emgAcquireClient.emgAcquireClient(nb_channels=nb_ch)

# create a numpy array to contain all the data
all_Data = np.array([], dtype=np.float32).reshape(8,0)

# initialize the node
init_test = emgClient.initialize()

if init_test<0:
    print("unable to initialize")
    exit()

# start the acquisition
emgClient.start()
"""
# get current time
t_time = time.time()

# array for keeping the timings
timings = np.array([], dtype=np.float)

start_time = time.time()
freq = 20
dt = 1/freq
is_looping = True
index = 0
time_vect = [start_time]
freq_vect = [0]
"""
"""duration = 10
freq = 19.7
count = 0
time_vect = [0]
freq_vect = []
dt = 1/freq
nb_point = round(duration/dt)

start = time.perf_counter()
steps = np.linspace(0, 0+(dt*nb_point),nb_point,endpoint=False)
for division in range(int(freq*duration)):
#for division in range():
    while time.perf_counter() < start + division/freq:
        pass
    emg_data = emgClient.getSignals()
    all_Data = np.hstack((all_Data, emg_data))
    count = count + 1
    #timings = np.append(timings, time.perf_counter() - t_time)
    #t_time = time.perf_counter()
    if count >1 :
        freq_vect.append(1/(time.perf_counter()-time_vect[-1]))
    time_vect.append(time.perf_counter())

elapsed = time.perf_counter() - start"""
csv_path = "/Users/LASA/Documents/Recordings/surgeon_recording/data/test_emg_new_recorder/test_1.csv"
f = open(csv_path, 'w', newline='')
writer = csv.writer(f)
header = ['index', 'timestamp', 'channel 1']
writer.writerow(header)

duration = 10
count = 0
time_vect1 = [0]
freq_vect1 = []
freq_vect2 = []

time_vect2 = [0]

is_looping = True
start_time = time.perf_counter()
time_vect1 = [start_time]
while is_looping:
    #while (time.perf_counter()-time_vect1[-1]) < 0.048:
        #pass
    emg_data = emgClient.getSignals()
    time_vect1.append(time.perf_counter())
    print(time_vect1[-1])
    time_vect2.append(time.time())
    print(time_vect2[-1])
    if count > 0:
        freq_vect1.append(1/(time_vect1[-1]-time_vect1[-2]))
        #freq_vect2.append(1/(time_vect2[-1]-time_vect2[-2]))

    all_Data = np.hstack((all_Data, emg_data))
    count = count + 1
    dt = (time_vect1[-1]-time_vect1[-2])/50
    tmp_time_vector = np.linspace(time_vect1[-2], time_vect1[-2]+(dt*50),50,endpoint=False)
    
    for index in range(len(emg_data[1])):
        row = [index, tmp_time_vector[index], emg_data[1][index]]
        writer.writerow(row)


    if time.perf_counter() - start_time > duration:
        print("stoping")
        
        is_looping = False
        f.close()

print(emg_data)

"""
while is_looping:
    
    #try:
        # acquire the signals from the buffer
    emg_data = emgClient.getSignals()
    freq_vect.append(1/(time.time()-time_vect[-1]))
        # append the array with the new data
    all_Data = np.hstack((all_Data, emg_data))

        # keep the updating period
    timings = np.append(timings, time.time() - t_time)

        # reset the timer
    t_time = time.time()
    
    time_vect.append(time.time())

    index = index + 1

    time.sleep(dt- ((time.time() - start_time) % dt))
        
    # if Ctrl+C is pressed interrupt the loop
    #except KeyboardInterrupt:
            #break

    if time.time() - start_time > 10:
        print("loop")
        is_looping = False
"""

# shutdown the acquisition node
emgClient.shutdown()

# print statistics and the size of the acquired data
#print(str(np.mean(timings)) + " \pm " + str(np.std(timings)))
print(all_Data.shape)
#print(len(timings))
print(count)
#print(freq_vect)
print("mean" + str(np.mean(freq_vect1)))

#print(f'Count {count} Elapsed {elapsed}')

fig, ax = plt.subplots()

ax.plot(freq_vect1)
#ax.set_ylim([-1000, 1000])

fig2, ax2 = plt.subplots()

ax2.plot(freq_vect2)
#ax2.set_ylim([freq-10, freq+10])

plt.show()

