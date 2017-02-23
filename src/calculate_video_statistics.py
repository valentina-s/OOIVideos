from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import seaborn

import imageio



def calculateRollingStats(filename, lag=1, subsampleRate=1):

    # creating the video object
    vid = imageio.get_reader(filename, 'ffmpeg')

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

def calculateRollingStats_list(filename, lag=1, subsampleRate=1):

    # creating the video object
    vid = imageio.get_reader(filename, 'ffmpeg')

    # extracting the video dimensions
    nofFrames = len(vid)
    dim1 = vid.get_data(0).shape[0]
    dim2 = vid.get_data(0).shape[1]

    # generate the list of frame numbers we will process
    nums = list(np.arange(0,nofFrames,subsampleRate))

    # initializing return variables
    rolling_mean = []
    rolling_var = []

    rolling_mean = np.zeros((len(nums,)))
    rolling_variance = np.zeros((len(nums,)))


    # process first block
    block = []
    for i in np.arange(lag):
        block.append(vid.get_data(nums[i])[:,:,0])
    block_array = np.array(block)

    rolling_mean[0] = np.sum(np.mean(block_array,0))
    rolling_var[0] = np.sum(np.var(block_array,0))


    for i in np.arange(lag,len(nums)):
        print(nums[i])
        block.append(vid.get_data(nums[i])[:,:,0])
        block.pop(0)
        block_array = np.array(block)

        rolling_mean.append(np.sum(np.mean(block_array,0)))
        rolling_var.append(np.sum(np.var(block_array,0)))

    vid.close()

    return(rolling_mean, rolling_var)

def calculateRollingStats_fromUrl(movie_url, lag=3, subsampleRate=10, frame_start=0, frame_end=-1):

    """
        calculateRollingStats_fromUrl calculates rolling variance from a video at an url.

        Inputs:
            movie_url
            lag
            subsampleRate
            frame_start
            frame_end

    """

    from skimage import io
    import json

    import sys


    if sys.version_info >= (3,0):
      from urllib.request import urlopen
      from urllib.error import HTTPError, URLError
    else:
      from urllib2 import urlopen
      from urllib2 import HTTPError, URLError


    try:
        response = urlopen(movie_url)
        # extracting the video dimensions
        header = json.loads(response.read().decode())
        nofFrames = header['NumFrames']
    except:
        return(None)


    if frame_end == -1:
        frame_end = nofFrames
        print(frame_end)

    # generate the list of frame numbers we will process
    nums = list(np.arange(frame_start,frame_end,subsampleRate))

    list_urls = [movie_url+'/frame/'+str(num) for num in nums]

    # initializing return variables
    rolling_var = []


    # process first block
    block = []
    for i in np.arange(lag):
        try:
            image = io.imread(list_urls[i])[:,:,0]
        except:
            return(None)
        block.append(image)

    block_array = np.array(block)
    rolling_var.append(np.sum(np.var(block_array,0)))


    # process all other blocks

    for i in np.arange(lag,len(nums)):
        try:
            image = io.imread(list_urls[i])[:,:,0]
        except:
            return(None)

        block.append(image)
        block.pop(0)
        block_array = np.array(block)

        rolling_var.append(np.sum(np.var(block_array,0)))


    return(rolling_var)

def createRollingStatsVideo(rolling_mean, rolling_var, videoname, subsampleRate, speedup):


    """
        calculateRollingStats(filename, lag=1,subsampleRate=1)

        Inputs:
        ------

        filename:      name of file
        lag:           the lag of the rolling mean (after subsampling)
        subsampleRate: the video is read at rate subsampleRate, and the statistics are calculated on the sparser sequence.

        Outputs:
        -------
        (rolling_mean, rolling_variance): tuple of lists


    """


    imageio.plugins.ffmpeg.download()
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




def main():
    """
        This script reads a video and calculates rolling statistics and outputs
        them to a .csv file.

    """
    import pandas as pd
    import sys
    import time

    start_time = time.time()

    if len(sys.argv)>1:
        filename_in = sys.argv[1]
    else:
        filename_in = 'opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_02_CAMHDA301-20160102T210000Z.mp4'

    if len(sys.argv)<2:
        filename_out = 'RollingVariance_' + filename_in[-20:-4] + '.csv'
    else:
        filename_out = argv[2]

    video_path = os.path.join(os.getcwd(),'OOIVideos')
    results_path = os.path.join(os.getcwd(),'results')

    date_stamp = filename_in[-16:-4]


    # reading sparse frames:
    rolling_mean, rolling_var = calculateRollingStats(os.path.join(video_path,filename_in),lag = 3,subsampleRate = 10)

    # uncomment to create a video
    # createRollingStatsVideo(rolling_mean,rolling_var,os.path.join(results_path,videoname), subsampleRate=10, speedup=10)

    # write variance to a .csv
    pd.DataFrame(rolling_var).to_csv(os.path.join(results_path,filename_out), index = None, header = None)

    elapsed_time = time.time() - start_time
    print('Elapsed time: '+ str(elapsed_time)+'s')

if __name__ == '__main__':
    main()
