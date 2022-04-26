import numpy as np
import time
import sys



# deifne the directory of the emgAcquireClient python_module 
emgAcquire_dir = r"C:\Users\LASA\Documents\Recordings\surgeon_recording\source\emgAcquire\python_module"
# append the path including the directory of the python_module
sys.path.append(emgAcquire_dir)
# import the module
import emgAcquireClient

class EMGHandler(object):
    def __init__(self):
        
        # create an emgClient object for acquiring the data
        self.emgClient = emgAcquireClient.emgAcquireClient(nb_channels=4)
        # initialize the node
        init_value = self.emgClient.initialize()
        self.emg_init = init_value == 0
        self.emgClient.start()
        self.emg_data = []

    

    def acquire_data(self):
        # acquire the signals from the buffer
        emg_array = self.emgClient.getSignals()
        returned_data = []

        # append the array with the new data
        if self.emg_data:
            prev_time = self.emg_data[-1][1]
            index = self.emg_data[-1][0]
        else:
            prev_time = self.start_time
            index = 0
        last_sample_time = time.time()
        dt = (last_sample_time - prev_time)/len(emg_array[0])
        for i in range(len(emg_array[0])):
            data = [index + 1]
            t = prev_time + (i+1) * dt
            data.append(t)
            # keep the updating period
            data.append(t - self.start_time)
            data = data + emg_array[:, i].tolist()
            index = data[0]
            returned_data.append(data)
        self.emg_data = returned_data
        return returned_data

   
    

    def shutdown(self):
        super().shutdown()
        if not self.simulated and self.emg_init:
            self.emgClient.shutdown()
            print("emg closed cleanly")


def main(args=None):
    emg_handler = EMGHandler()
    emg_handler.run()

    is_looping = True
    
    while is_looping:
        if time.time() - start_time > 3:
            is_looping = False
            emg_handler.opt_client.shutdown()
            #emg_handler.f.close()
    
if __name__ == '__main__':
    main()