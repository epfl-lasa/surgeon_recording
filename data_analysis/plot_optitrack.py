from modules.optitrack_utils import * 

data_dir = 'exp_data/260423/1/2/'
path_to_opti = data_dir + 'optitrack.csv'

plot_optitrack_csv(path_to_opti)

# tweezerDF, needle_holderDF = clean_optitrack(path_to_opti)
# plot_optitrackDF(tweezerDF, needle_holderDF)

optiDF = pd.read_csv(path_to_opti, header=0)

nb_frames_total = len(optiDF.index)

nb_zero_tweezers = (optiDF['tweezers_x'] == 0).sum(axis=0)

nb_zero_needle_holder = (optiDF['needle_holder_x'] == 0).sum(axis=0)

print("TOTAL nb of frames : ", nb_frames_total)
print("Missed frames tweezers : ", nb_zero_tweezers, f",  {100*nb_zero_tweezers/nb_frames_total:.2f}% " )
print("Missed frames needle hodler : ", nb_zero_needle_holder, f", { 100*nb_zero_needle_holder/nb_frames_total:.2f}%")