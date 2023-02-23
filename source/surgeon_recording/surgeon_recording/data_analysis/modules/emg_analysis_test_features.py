#IMPORTS 
from emg_utils import * 
import scipy.signal as sp
import numpy as np
import pandas as pd


class Emg_analysis_features:
    def __init__(self, 
                 data_dir, 
                 file_calibration, 
                 file_mydata, 
                 start_idx, 
                 end_idx, 
                 idx_label_studied = 15,
                 SR = 1500, 
                 emg_placement = 'Jarque-Bou'):
        self.data_dir = data_dir
        self.path_to_calibration = data_dir + file_calibration
        self.path_to_mydata = data_dir + file_mydata
        self.t_start = start_idx * SR
        self.t_end = end_idx * SR
        self.SR = SR
        self.emg_placement = emg_placement
        self.idx_label_studied = idx_label_studied
        
        self.filtering()
        self.init_extraction()
        
    
    #FILTERING
    def filtering(self):
        cleanemg_calib = clean_emg(self.path_to_calibration, self.emg_placement)   
        cleanemgDF = clean_emg(self.path_to_mydata, self.emg_placement)   
        
        #Butterworth
        butt_calib = butterworth_filter(cleanemg_calib)
        butt = butterworth_filter(cleanemgDF)
        
        #Interpolation and rectification
        interp_calib = interpolate_clean_emg(butt_calib, t_start=0)
        interp_calib = abs(interp_calib) #rectify 
        interpDF = interpolate_clean_emg(butt, t_start=50)
        interpDF = abs(interpDF) # rectify
        
        #Amplitude normalization
        self.normDF = normalization(interpDF, interp_calib)
        
        return self.normDF
    
    #FEATURE EXTRACTION
    def init_extraction(self):
        self.labels_list = self.normDF.columns.values.tolist() #takes all the names of the columns into a list
        self.label_studied = self.normDF.columns.values.tolist()[self.idx_label_studied]
    
        #select one knot in normDF
        self.norm2 = self.normDF.copy()
        for label in self.labels_list[2:]:
            self.norm2[label] = self.normDF[label].iloc[self.t_start : self.t_end]
        
        self.norm2= self.norm2.dropna(how="any")
        # plot_emgDF(norm2, title_str='Normalized EMG - Torstein')
        
        return self.labels_list, self.label_studied, self.norm2
    
    
    #FEATURE EXTRACTION
    # Integrated EMG - pre-activation index for muscle activity
    def iemg(self, df) :
        iemgDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            iemgDF[label] = [abs(df[label]).sum()]
        self.iemgDF = iemgDF
        return iemgDF
        
    #Mean absolute value
    def mav(self, df, window_length) :
        mavDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            mavDF[label] = [(1/self.window_length)*abs(df[label]).sum()]
        self.mavDF = mavDF
        return mavDF
    
    #Single square integral (SSI) - energy of the EMG signal
    def ssi(self, df) :
        ssiDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            ssiDF[label] = [(abs(df[label])**2).sum()]
        self.ssiDF = ssiDF
        return ssiDF
        
    #Variance - Power of EMG
    def var(self, df, window_length) :
        varDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            varDF[label] = [(1/(self.window_length-1))*(df[label]**2).sum()]
        self.varDF = varDF
        return varDF
        
    #Root Mean Square - amplitude modulated Gaussian random process where the RMS is related to the constant force, and the non-fatigue constractions of the muscles
    def rms(self, df) :
        rmsDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            rmsDF[label] = [((df[label]**2).mean()) **0.5]
        self.rmsDF = rmsDF
        return rmsDF
        
    #Waveform Length - cumulative length of the waveform over the segment
    def wl(self, df) :
        wlDF = pd.DataFrame(columns = self.labels_list[2:])
        for label in self.labels_list[2:]:
            wlDF[label]= [abs(df[label].diff()).sum()]
        self.wlDF = wlDF
        return wlDF
        
    #Power spectrum density of the normalized dataframe
    def psd(self, df) :
        psdDF = pd.DataFrame(columns= self.labels_list[2:])
        f = pd.DataFrame(columns= self.labels_list[2:])
        RMSamplitude = []
        for label in self.labels_list[2:]:
            f[label], psdDF[label] = sp.periodogram(df[label], self.SR, 'flattop', scaling='spectrum')
        
            # The peak height in the power spectrum is an estimate of the RMS amplitude.
            RMSamplitude.append(np.sqrt(psdDF[label].max()))
        self.f = f
        self.psdDF = psdDF
        self.RMSamplitude = RMSamplitude
        return (f, psdDF, RMSamplitude)
    
    #Frequency median - the frequency where the power spectrum is divided into two equal parts
    def fmd(self, df) :
        fmdDF =  pd.DataFrame(columns=self.labels_list[2:])
        for label in self.labels_list[2:]:
            fmdDF[label] = [(self.psdDF[label].sum())*0.5]
        self.fmdDF = fmdDF
        return fmdDF
        
    #Frequency mean - average of the frequency
    def fmn(self, df) :
        fmnDF = pd.DataFrame(columns=self.labels_list[2:])
        for label in self.labels_list[2:]:
            fmnDF[label] = [(self.psdDF[label]*self.f[label]).sum() / self.psdDF[label].sum()]
        self.fmnDF = fmnDF
        return fmnDF 
    
    #Function that call every feature 
    def all_features(self, df, window_length):
        iemgDF = self.iemg(df)
        mavDF = self.mav(df, window_length)
        ssiDF = self.ssi(df)
        varDf = self.var(df, window_length)
        rmsDF = self.rms(df)
        wlDF = self.wl(df)
        f, psdDF, RMSamplitude = self.psd(df)
        fmdDF = self.fmd(df)
        fmnDF = self.fmn(df)
        return iemgDF, mavDF, ssiDF, varDf, rmsDF, wlDF, f, psdDF, RMSamplitude, fmdDF, fmnDF