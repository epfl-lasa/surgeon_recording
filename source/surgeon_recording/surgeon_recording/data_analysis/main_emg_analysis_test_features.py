from modules import emg_utils as myfct
from modules.emg_analysis_test_features import Emg_analysis_features
import matplotlib.pyplot as plt
import pandas as pd
from textwrap import wrap

S7 = Emg_analysis_features(data_dir = r'/home/cecile/Documents/', 
                               file_calibration = 'emg_data_calibration.csv', 
                               file_mydata = 'emg_data_task.csv', 
                               start_idx = 100, 
                               end_idx = 200,
                               )

normDF = S7.normDF
medianDF = S7.median(S7.normDF, window_length=S7.normDF.shape[0])

# Plot DataFrame 1
for channel in S7.normDF.columns:
    plt.plot(S7.normDF.index, S7.normDF[channel], label=f'normDF - {channel}')

# Plot DataFrame 2
for channel in medianDF.columns:
    print('column m= ', channel)
    print('shape m= ', medianDF.index,[channel].shape)
    plt.plot(medianDF.index,[channel], label=f'medianDF - {channel}', linestyle='dashed')

# Customize the plot as needed
plt.xlabel('Index')
plt.ylabel('EMG data')
plt.title('Normalized EMG values of subject 1')
plt.legend()
plt.grid(True)

plt.show()


# #plot mavDFs
# plt.figure()
# # plotmav = pd.DataFrame({"mav Cécile" : cecile.mavDF.values.tolist()[0], 
# #                          "mav Torstein" : torstein.mavDF.values.tolist()[0]}, index = cecile.labels_list[2:])
# # plotmedian = pd.DataFrame({"normDF" : S7.normDF.values.tolist()[0], "median S7" : S7.median.values.tolist()[0]}, index = S7.labels_list[2:])
# plotmedian = pd.DataFrame({"normDF" : S7.normDF.values.tolist(), 
#                            "median S7" : S7.median.values.tolist()}, 
#                            index = S7.labels_list[2:])

# ax = plotmedian.plot.bar(rot=0)
# ax.set_title("Mean absolute value", fontsize = 25)
# ax.set_xlabel("Muscles", fontsize = 20)
# ax.set_ylabel("mavDF", fontsize = 20)

# #to wrap text on xlabels
# labels = [ '\n'.join(wrap(l, 10)) for l in S7.labels_list[2:]] 
# ax.set_xticklabels(labels, rotation=45, fontsize = 15)



