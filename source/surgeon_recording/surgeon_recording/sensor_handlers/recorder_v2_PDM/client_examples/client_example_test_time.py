#!/usr/bin/env python

import os
import sys
import pathlib
import numpy as np
import time
import matplotlib.pyplot as plt


duration = 10
freq = 50

#end_time = start + duration
count = 0
time_vect = [0]
freq_vect = []


# 1 - LOOP WITH COUNTER

start = time.perf_counter()
for division in range(freq*duration):
    while time.perf_counter() < start + division/freq:
        pass
    count = count + 1
    if count >1 :
        freq_vect.append(1/(time.perf_counter()-time_vect[-1]))
    time_vect.append(time.perf_counter())

    

elapsed = time.perf_counter() - start
print(f'Count {count} Elapsed {elapsed}')


# 2 -  LOOP WITHOUT COUNTER

"""start_time = time.time()
freq = 10
dt = 1/freq
is_looping = True
index = 0
time_vect = [1]
freq_vect = []
"""
"""
while is_looping:
    start_loop = time.time()
    freq_vect.append(1/(time.time()-time_vect[-1]))
 
    time_vect.append(time.time())
    index = index + 1
    end_loop = time.time()

    if time.time() - start_time > 10:
        print("loop")
        is_looping = False
    
    #print(float(time.time() - start_loop))
    #print(float(dt-(time.time() - start_loop)))
    
    if float(dt - (time.time() - start_loop)) > 0:
        #print(dt - (time.time() - start_loop))
        time.sleep(float(dt - ((time.time() - start_loop) )))
        print("loop2")
    #time.sleep(dt - ((time.time() - start_loop) ))
    #print(dt - (time.time() - start_loop))
    """


fig, ax = plt.subplots()

ax.plot(freq_vect)
ax.set_ylim([freq-10, freq+10])

plt.show()


