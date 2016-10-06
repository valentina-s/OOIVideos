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

    print(subsampleRate)

    for lb,ub in zip(bounds['LB'],bounds['UB']):
        binary[round(lb/subsampleRate*10):round(ub/subsampleRate*10)] = 1




    for i in range(len(frame_idx)):
    # for i in range(100):

        print(i)


        im = vid_in.get_data(frame_idx[i])
        plt.subplot(211)
        plt.imshow(im, aspect = 'equal')
        plt.axis('off')
        plt.title('Raw Video')


        plt.subplot(212)
        plt.imshow(im*int(binary[i]), aspect = 'equal')
        plt.axis('off')
        plt.title('Static Scenes')


        # convert the plot
        fig.canvas.draw()
        fig_data = np.fromstring(fig.canvas.tostring_rgb(),dtype = np.uint8, sep='')
        fig_data = fig_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        # vid_out.append_data(fig_data.astype(np.dtype('uint8')))
        vid_out.append_data(fig_data)
        # vid_out.append_data(im)
        plt.clf()

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

    if len(sys.argv)<5:
        subsampleRate = 10
    else:
        subsampleRate = int(sys.argv[4])

    if len(sys.argv)<6:
        speedup = 10
    else:
        speedup = int(sys.argv[5])

    bounds2video(sys.argv[1],sys.argv[2],sys.argv[3],subsampleRate,speedup)
    vdisplay.stop()



if __name__ == '__main__':
    main()
