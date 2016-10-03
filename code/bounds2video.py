from __future__ import division
import imageio
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# trying xvfbwrapper to run headless
import xvfbwrapper as xvfb




def bounds2video(bounds_file,video_in, video_out, subsampleRate, speedup):
    """
        This function reads a .csv file with bound and creates a split video based on them.
    """

    # reading the bounds
    bounds = pd.read_csv(bounds_file, index_col = None)

    fig = plt.figure(figsize = (15,10))

    # setting up the video reader and writer
    vid_in = imageio.get_reader(video_in,'ffmpeg')
    vid_out = imageio.get_writer(video_out,fps = 30/subsampleRate*speedup)

    # create a binary indicator for where the scenes are
    frame_idx = np.arange(0,len(vid_in),subsampleRate)
    binary = np.zeros((len(frame_idx),))


    for lb,ub in zip(bounds['LB'],bounds['UB']):
        binary[lb:ub] = 1




    #for i in range(len(frame_idx)):
    for i in range(20):

        print(i)


        im = vid_in.get_data(frame_idx[i])
        plt.subplot(211)
        plt.imshow(im*binary[i], aspect = 'equal')
        plt.axis('off')


        plt.subplot(212)
        plt.imshow(im*(1-binary[i]), aspect = 'equal')
        plt.axis('off')


        # convert the plot
        fig.canvas.draw()
        fig_data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        fig_data = fig_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        vid_out.append_data(fig_data.astype(np.dtype('uint8')))
        # vid_out.append_data(im)

    vid_in.close()
    vid_out.close()

def main():
    import sys
    import imageio
    import pandas as pd
    import matplotlib.pyplot as plt
    from xvfbwrapper import Xvfb

    plt.ioff()

    # with Xvfb() as xvfb:
    # plt.ioff()
    vdisplay = Xvfb()
    vdisplay.start()
    bounds2video(sys.argv[1],sys.argv[2],sys.argv[3],10,10)
    vdisplay.stop()
    import os
    # os.system('(sleep 5 && kill -9 %d) &' % vdisplay.proc.pid)


if __name__ == '__main__':
    main()
