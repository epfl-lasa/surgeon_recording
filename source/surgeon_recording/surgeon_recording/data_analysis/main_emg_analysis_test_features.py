from modules import emg_utils as myfct
from modules.emg_analysis_test_features import Emg_analysis_features
import matplotlib.pyplot as plt
import pandas as pd

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


# myfct.plot_emgDF(cecile.normDF)
# ax = cecile.normDF.plot.bar(rot = 0)
# ax = cecile.normDF.plot.bar(x = cecile.labels_list, y = cecile.mavDF, rot = 0)

plotdata = pd.DataFrame({"mav Cécile" : [cecile.mavDF.to_numpy()[0]], 
                         "mav Torstein" : [torstein.mavDF.to_numpy()[0]]}, index = [str(cecile.labels_list[2:])])
plotdata.plot(kind="bar")

cecile.normDF.reset_index().plot(x= str(cecile.labels_list[2:]), y=[torstein.mavDF, cecile.mavDF], kind="bar", rot = 0)
plt.title("Mince Pie Consumption 18/19")
plt.xlabel("Family Member")
plt.ylabel("Pies Consumed")

cecile.mavDF.plot.bar(rot = 0)