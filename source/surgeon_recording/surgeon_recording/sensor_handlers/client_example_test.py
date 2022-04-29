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

#emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
#sys.path.append(emgAcquire_dir)

# import the module
#import emgAcquireClient


# define number of channels to acquire
#nb_ch = 6

# create an emgClient object for acquiring the data
#mgClient = emgAcquireClient.emgAcquireClient(nb_channels=nb_ch)

# create a numpy array to contain all the data
#all_Data = np.array([], dtype=np.float32).reshape(6,0)

# initialize the node
#init_test = emgClient.initialize()

#if init_test<0:
    #print("unable to initialize")
    #exit()

# start the acquisition
#emgClient.start()

# get current time
#t_time = time.time()

# array for keeping the timings
#timings = np.array([], dtype=np.float)

"""start_time = time.time()
freq = 10
dt = 1/freq
is_looping = True
index = 0
time_vect = [1]
freq_vect = []
"""
duration = 10
freq = 50

#end_time = start + duration
count = 0
time_vect = [0]
freq_vect = []

start = time.perf_counter()
for division in range(freq*duration):
    #print(freq_vect)
    while time.perf_counter() < start + division/freq:
        pass
    count = count + 1
    if count >1 :
        freq_vect.append(1/(time.perf_counter()-time_vect[-1]))
    time_vect.append(time.perf_counter())

    

elapsed = time.perf_counter() - start
print(f'Count {count} Elapsed {elapsed}')


"""
while is_looping:
    start_loop = time.time()
    print(time.time()-time_vect[-1])
    freq_vect.append(1/(time.time()-time_vect[-1]))
 
    time_vect.append(time.time())
    
    index = index + 1

    end_loop = time.time()


    if time.time() - start_time > 10:
        print("loop")
        is_looping = False
    
    print("a")
    print(float(time.time() - start_loop))
    print(float(dt-(time.time() - start_loop)))
    if float(dt - (time.time() - start_loop)) > 0:
        #print(dt - (time.time() - start_loop))
        time.sleep(float(dt - ((time.time() - start_loop) )))
        print("loop2")
    #time.sleep(dt - ((time.time() - start_loop) ))
    #print(dt - (time.time() - start_loop))
    """

# shutdown the acquisition node
#emgClient.shutdown()

# print statistics and the size of the acquired data
#print(str(np.mean(timings)) + " \pm " + str(np.std(timings)))
#print(all_Data.shape)
#print(len(timings))
#print(index)
#print(freq_vect)

fig, ax = plt.subplots()

ax.plot(freq_vect)
ax.set_ylim([freq-10, freq+10])

plt.show()


