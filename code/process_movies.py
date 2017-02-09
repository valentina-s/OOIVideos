import glob
import pandas as pd
import os
import imageio
import sys
sys.path.append(os.path.join(os.getcwd(),'code'))

from extract_scenes import extractSceneBounds
from calculate_video_statistics import calculateRollingStats

folder_name = 'weekly_videos'

video_path = os.path.join(os.getcwd(),folder_name)
results_path = os.path.join(os.getcwd(),'results')


print(listOfVideos)

def video2bounds(filename,results_path):

    filename_out_var = 'RollingVariance_' + filename[-20:-4] + '.csv'

    filename_out_bounds = 'Bounds_' + filename[-20:-4] + '.csv'

    # reading sparse frames:
    rolling_mean, rolling_var = calculateRollingStats(filename,lag = 3,subsampleRate = 10)

    # save variance

    pd.DataFrame(rolling_var).to_csv(os.path.join(results_path,filename_out_var), index = None, header = None)

    # extract scenes
    bounds = extractSceneBounds(rolling_var)

    # write scene bounds in two column csv
    pd.DataFrame(bounds,columns = ['LB','UB']).to_csv(os.path.join(os.getcwd(),filename_out_bounds), index = None)

    return(bounds)


if __name__ == '__main__':
    import sys
    folder_name = sys[1]
    results_path = sys[2]

    ## maybe do a name if it is possible




    listOfVideos = glob.glob(folder_name+'/*.mp4')
    print(listOfVideos)

    e = concurrent.futures.ProcessPoolExecutor(max_workers=4)
    #all_bounds = e.map(video2bounds,listOfVideos)


#TODO add option for all files in subfolders in a path,
# and all files in a  subfolder of a bucket path (I could even allow Google Cloud/ AWS bucket)
