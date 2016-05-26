import glob
import pandas as pd
import os
import imageio
import sys
sys.path.append(os.path.join(os.getcwd(),'code'))

from extract_scenes import extractSceneBounds
from calculate_video_statistics import calculateRollingStats



video_path = os.path.join(os.getcwd(),'weekly_videos')
results_path = os.path.join(os.getcwd(),'results')

listOfVideos = glob.glob('weekly_videos/*.mp4')

print(listOfVideos)

for filename in listOfVideos:
    print(filename)

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

    






