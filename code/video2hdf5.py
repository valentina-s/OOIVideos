from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import seaborn

import imageio
import h5py

def video2hdf5(fname_in, fname_out, subsampleRate = 1):
    """
        This function converts a video to a hdf5 format.
        It reads the video frame by frame and adds the frames
        to an hdf5 file. The label of the dataset is 'Dataset1'.

        Parameters:
            fname_in: name of the input file (should be in a format readable by ffmpeg)
            fname_out: name of the output file (hdf5 format)
            subsampleRate: integer for subsampling the number of frames

    """
    # creating the video object
    vid = imageio.get_reader(fname_in, 'ffmpeg')

    # extracting the video dimensions
    nofFrames = len(vid)
    dim1 = vid.get_data(0).shape[0]
    dim2 = vid.get_data(0).shape[1]

    # generate the list of frame numbers we will process
    nums = list(np.arange(0,nofFrames,subsampleRate))

    # create hdf5 output file
    h5f = h5py.File(fname_out, 'w')
    h5f.create_dataset('Dataset1', (dim1,dim2,len(nums)),chunks = True)

    # read and store frame by frame
    for i in np.arange(len(nums)):
        print(nums[i])

        frame = vid.get_data(nums[i])[:,:,0]
        h5f['Dataset1'][:,:,i] = frame

    vid.close()
    h5f.close()

def main():
    """
        This script reads a video and stores it to hdf5.

    """

    import sys
    import time

    start_time = time.time()

    if len(sys.argv)>1:
        filename_in = sys.argv[1]
    else:
        raise ValueError('Provide a name for the input file.')


    if len(sys.argv)>2:
        filename_out = sys.argv[2]
    else:
        filename_out = filename_in[:-4] + '.h5'


    if len(sys.argv)>3:
        subsampleRate = sys.argv[3]
    else:
        subsampleRate = 10

    # reading sparse frames:
    video2hdf5(filename_in,filename_out,subsampleRate = subsampleRate)

    elapsed_time = time.time() - start_time
    print('Elapsed time: '+ str(elapsed_time)+'s')
    return(0)

if __name__ == '__main__':
    main()
