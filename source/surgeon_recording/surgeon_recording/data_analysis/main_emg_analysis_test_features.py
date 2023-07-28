from modules import emg_utils as myfct
from modules.emg_analysis_test_features import Emg_analysis_features
import matplotlib.pyplot as plt
import pandas as pd
from textwrap import wrap

S1 = Emg_analysis_features(data_dir = r'E:/Surgeon_Skill_Assessment/Data_Cluj_June_2023/S_4_090623/TSK_1/TRL_1/', 
                               file_calibration = 'emg_data_calibration.csv', 
                               file_mydata = 'emg_data_task.csv', 
                               start_idx = 89, 
                               end_idx = 147,
                               )

medianDF = S1.median(S1.normDF)

# Plot DataFrame 1
for channel in S1.normDF.columns:
    plt.plot(S1.normDF.index, S1.normDF[channel], label=f'normDF - {channel}')

# Plot DataFrame 2
for channel in medianDF.columns:
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
# # plotmedian = pd.DataFrame({"normDF" : S1.normDF.values.tolist()[0], "median S1" : S1.median.values.tolist()[0]}, index = S1.labels_list[2:])
# plotmedian = pd.DataFrame({"normDF" : S1.normDF.values.tolist(), 
#                            "median S1" : S1.median.values.tolist()}, 
#                            index = S1.labels_list[2:])

# ax = plotmedian.plot.bar(rot=0)
# ax.set_title("Mean absolute value", fontsize = 25)
# ax.set_xlabel("Muscles", fontsize = 20)
# ax.set_ylabel("mavDF", fontsize = 20)

# #to wrap text on xlabels
# labels = [ '\n'.join(wrap(l, 10)) for l in S1.labels_list[2:]] 
# ax.set_xticklabels(labels, rotation=45, fontsize = 15)



