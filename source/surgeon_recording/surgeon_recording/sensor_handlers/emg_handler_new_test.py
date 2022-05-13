import numpy as np
import time
import sys



# deifne the directory of the emgAcquireClient python_module 
#emgAcquire_dir = r"C:\Users\LASA\Documents\Recordings\surgeon_recording\source\emgAcquire\python_module"
emgAcquire_dir = r"C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emgAcquire/python_module"

# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

class EMGHandler_new(object):
    def __init__(self):
        
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(nb_channels = 8)
        # initialize the node
        self.init_value = self.emgClient.initialize()
        #self.emg_init = init_value == 0
        self.emgClient.start()
        self.emg_data = []
        self.emg_data2 = []
        
        #self.emg_array = []
        
        #self.returned_data = []

        #self.emgClient.run()

    

    def acquire_data(self):
        print("hello")
        # acquire the signals from the buffer
        self.emg_data.append(self.emgClient.getSignals())
        emg_array = self.emgClient.getSignals()
        returned_data = []
        print(len(emg_array[0]))
        for i in range(len(emg_array[0])):
            data = [0]
            data.append(emg_array[:, i].tolist())
            index = data[0]
            returned_data.append(data)
        self.emg_data2 = returned_data

        return returned_data
    
   


def main(args=None):
    start_time = time.time()
    emg_handler = EMGHandler_new()
    #init_test = emg_handler.emgClient.initialize()
    #print(init_test)

    is_looping = True
    #emg_handler.acquire_data()

    freq = 50
    dt = 1/freq
    
    while is_looping:
        print("tick")
        emg_handler.acquire_data()
        time.sleep(dt- ((time.time() - start_time) % dt))
        time_a = time.time()
        if time_a - start_time > 10:
            print("loop")
            is_looping = False
            emg_handler.emgClient.stop()
            print(len(emg_handler.emg_data))
            emg_handler.emgClient.shutdown()
            #emg_handler.f.close()

    print(len(emg_handler.emg_data))
   # print(emg_handler.emg_data)
   # print(emg_handler.emg_data2)
    


if __name__ == '__main__':
    main()