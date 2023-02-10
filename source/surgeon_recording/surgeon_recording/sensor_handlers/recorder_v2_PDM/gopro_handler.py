from goprocam import GoProCamera, constants
import time
import numpy as np

# ######
#
# Handler to gopro and save time on start for synchronisation 
#
# ######

class GoProHandler:
    def __init__(self, csv_path):

        # path of csv file to write start and end time
        self.csv_path_gopro_time = csv_path
        self.start_time = time.time() #in case of early close
        self.gopro = GoProCamera.GoPro() # connect go pro -> needs to be connected on computer wifi first !

    def start_gopro(self):
        # Start recording wiht go pro and save exact time 
        self.gopro.shutter(constants.start)
        self.start_time = time.time()
        time_to_save = [['Start time', self.start_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))]]
        np.savetxt(self.csv_path_gopro_time, time_to_save, delimiter =", ", fmt ='% s')
        
    def shutdown_gopro(self):
        # Stop recording with gopro and save exact time
        self.gopro.shutter(constants.stop)
        end_time = time.time()
        time_to_save = [['Start time', self.start_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))], 
                        ['End time', end_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))], 
                        ['Duration', end_time-self.start_time, 'seconds']]
        np.savetxt(self.csv_path_gopro_time, time_to_save, delimiter =", ", fmt ='% s')
        print("gopro closed cleanly")
     