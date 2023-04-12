from modules import emg_utils as myfct
from modules.emg_analysis_test_features import Emg_analysis_features
import matplotlib.pyplot as plt
import pandas as pd
from textwrap import wrap

cecile = Emg_analysis_features(data_dir = r'../emg_recordings/13-01-2023/', 
                               file_calibration = 'calib_cecile/mydata.csv', 
                               file_mydata = 'cecile_task_2/cecile_task_2/mydata.csv', 
                               start_idx = 89, 
                               end_idx = 147,
                               )

torstein = Emg_analysis_features(data_dir = r'../emg_recordings/12-01-2023/', 
                               file_calibration = 'torstein_calib_half/mydata.csv', 
                               file_mydata = 'torstein_task_2/mydata.csv', 
                               start_idx = 76,
                               end_idx =  124,
                               )

cecile.all_features(cecile.normDF, cecile.normDF.shape[0])
torstein.all_features(torstein.normDF, torstein.normDF.shape[0])

#plot mavDFs
plt.figure()
plotmav = pd.DataFrame({"mav Cécile" : cecile.mavDF.values.tolist()[0], 
                         "mav Torstein" : torstein.mavDF.values.tolist()[0]}, index = cecile.labels_list[2:])

ax = plotmav.plot.bar(rot=0)
ax.set_title("Mean absolute value", fontsize = 25)
ax.set_xlabel("Muscles", fontsize = 20)
ax.set_ylabel("mavDF", fontsize = 20)

#to wrap text on xlabels
labels = [ '\n'.join(wrap(l, 10)) for l in cecile.labels_list[2:]] 
ax.set_xticklabels(labels, rotation=45, fontsize = 15)



