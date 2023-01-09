from goprocam import GoProCamera, constants
import time
import numpy as np

gopro = GoProCamera.GoPro(constants.gpcontrol)

gopro.overview()

time_start = time.time()
gopro.shoot_video(10)

time_end = time.time()

print("Start Time : ")
time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_start))
print("End Time : ")
time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_end))

# Save time recordings
save_path = "/Users/LASA/Documents/gopro_rec_time.txt"
to_save = [time_start, time_end]
np.savetxt(save_path, to_save)

## TODO : Check go pro time corresponds to REal Sense time 
## cna extract png frames from RS cam with :
## rs-convert -i 'path_to_file' -p 'path_to_png'
