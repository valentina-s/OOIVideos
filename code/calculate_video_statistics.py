from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import seaborn

import imageio



def calculateRollingStats(filename, lag=1, subsampleRate=1):

    # creating the video object
    vid = imageio.get_reader(os.path.join(video_path,filename), 'ffmpeg')

    # extracting the video dimensions
    nofFrames = len(vid)
    dim1 = vid.get_data(0).shape[0]
    dim2 = vid.get_data(0).shape[1]

    # generate the list of frame numbers we will process
    nums = list(np.arange(0,nofFrames,subsampleRate))

    # initializing return variables
    rolling_mean = []
    rolling_var = []


    # process first block
    block = []
    for i in np.arange(lag):
        block.append(vid.get_data(nums[i])[:,:,0])
    block_array = np.array(block)
    rolling_mean.append(np.sum(np.mean(block_array,0)))
    rolling_var.append(np.sum(np.var(block_array,0)))

    for i in np.arange(lag,len(nums)):
        print(nums[i])
        block.append(vid.get_data(nums[i])[:,:,0])
        block.pop(0)
        block_array = np.array(block)

        rolling_mean.append(np.sum(np.mean(block_array,0)))
        rolling_var.append(np.sum(np.var(block_array,0)))

    vid.close()

    return(rolling_mean, rolling_var)

def createRollingStatsVideo(rolling_mean, rolling_var, videoname, subsampleRate, speedup):

    fig = plt.figure(figsize = (15,5))
    vid = imageio.get_writer(videoname,fps = 30/subsampleRate*speedup)

    for i in range(len(rolling_mean)):
        plt.subplot(211)
        plt.plot(np.arange(0,len(rolling_mean[:i]))*subsampleRate/30/60,rolling_mean[:i],'r')
        plt.xlim((0,len(rolling_mean)*subsampleRate/30/60))
        plt.ylim((0,max(rolling_mean)))
        plt.title('Rolling Average')


        plt.subplot(212)
        plt.plot(np.arange(0,len(rolling_var[:i]))*subsampleRate/30/60,rolling_var[:i],'b')
        plt.xlim((0,len(rolling_var)*subsampleRate/30/60))
        plt.ylim((0,max(rolling_var)))
        plt.title('Rolling Variance')
        plt.xlabel('Time (min)')

        plt.canvas.draw()

        fig_data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        vid.append_data(fig_data)

    vid.close()



video_path = os.path.join(os.getcwd(),'..','OOIVideos')
# just reading sparse frames:
filename = 'opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_02_CAMHDA301-20160102T210000Z.mp4'
rolling_mean1, rolling_var1 = calculateRollingStats(os.path.join(video_path,filename),lag = 3,subsampleRate = 10)
# createRollingStatsVideo(rolling_mean,rolling_var,os.path.join(results_path,videoname), subsampleRate=10, speedup=10)
