import numpy as np
from generate_urls import generate_urls
from calculate_video_statistics import calculateRollingStats_fromUrl

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import sys


if sys.version_info >= (3,0):
  from urllib.request import urlopen
  from urllib.error import HTTPError, URLError
else:
  from urllib2 import urlopen
  from urllib2 import HTTPError, URLError




def ping(url):
    try:
        urlopen(url)
        return True         # URL Exist
    except (ValueError):
        return False        # URL not well formatted
    except (URLError):
        return False        # URL don't seem to be alive

# function to determine offset for alignment
def sync_corr(signal1, signal2):
    """
        Find maximum offset between signal1 and signal2.
    """
    from scipy import signal
    l = len(signal1)
    cc = signal.fftconvolve(np.abs(signal1),np.abs(signal2[::-1]), mode='full')
    # finding the maximum correlation
    offset = cc.argmax() + l - len(cc)
    return(offset)

def readTimelapse(urls):
    """
        readTimelapse reads a sequence of frames from urls
    """
    from skimage import io

    video_timelapse = []
    for url in urls:
        try:
            video_timelapse.append(io.imread(url))
        except:
            pass
    return(video_timelapse)


def saveTimelapse(video_timelapse,filename):
    """
        saveTimelapse converts a video (list of frames) into an .mp4 video
    """
    import imageio

    imageio.plugins.ffmpeg.download()

    writer = imageio.get_writer(filename, fps=1)

    for im in video_timelapse:
        writer.append_data(im)
    writer.close()

if __name__ == '__main__':
  """
    Example Usage:

    python align_timelapse.py --start_date 2016/05/01 --end_date 2016/05/05 --sampling DAILY --frame 5000 --subsampleRate 100 --interval 2 --pool-type thread --pool-size 4

  """

  import argparse
  from datetime import datetime, timedelta
  from collections import OrderedDict

  parser = argparse.ArgumentParser(description="Format is mm/yy")
  parser.add_argument('-start_date','--start_date',type=str,required=True)
  parser.add_argument('-frame','--frame',type=int,required=True)
  parser.add_argument('-end_date','--end_date',type=str,required=True)
  parser.add_argument('-sampling','--sampling',type=str,required=True)
  parser.add_argument('-subsampleRate','--subsampleRate',type=int,required=False)
  parser.add_argument('-interval','--interval',type=int,required=False)
  parser.add_argument('-pool-type','--poolType',type=str,required=False)
  parser.add_argument('-pool-size','--poolSize',type=int,required=False)
  parser.add_argument('-movie_name','--movie_name',type=str,required=False)

  args = parser.parse_args()
  if args.interval is not None:
      interval = args.interval
  else:
      interval = 1

  if args.subsampleRate is not None:
      subsampleRate = args.subsampleRate
  else:
      subsampleRate = 10
  # generate a list of urls based on the parameters
  list_movie_urls = generate_urls(args.start_date,args.end_date,args.sampling,interval)

  # drop urls which are not responsive
  filtered_urls = [url for url in list_movie_urls if ping(url)]


  #  calculate rolling variance for each url
  #res = [calculateRollingStats_fromUrl(url,lag=3,subsampleRate=args.subsampleRate,frame_start=3000,frame_end=7000) for url in filtered_urls]

  import functools

  if args.poolSize is not None and args.poolType is not None:

      if args.poolType=='thread':
          e = ThreadPoolExecutor(args.poolSize)
          res = e.map(functools.partial(calculateRollingStats_fromUrl,\
          subsampleRate = subsampleRate,frame_window=2000),filtered_urls)
          e.shutdown(wait=False)

      elif args.poolType=='process':
          e = ProcessPoolExecutor(args.poolSize)
          res = e.map(functools.partial(calculateRollingStats_fromUrl,\
          subsampleRate = subsampleRate,frame_window=2000,filtered_urls)
          e.shutdown(wait=False)

  else:
      res = map(functools.partial(calculateRollingStats_fromUrl,\
      subsampleRate = subsampleRate,frame_window=2000),filtered_urls)

  res = list(res)

  res_np = [np.array(r) for r in res]

  ## cashing curves
  import pickle
  with open('temp.pickle','wb') as temp:
      pickle.dump(res_np,temp)

  # extract offsets of misalignment
  offsets = []
  for i in range(1,len(res_np)):
      if res_np[i].shape != ():
          offset = sync_corr(res_np[0],res_np[i])
          offsets.append(offset)
      else:
          offsets.append(None)

  offsets = [0]+offsets
  print(offsets)

  # aligning the urls
  aligned_urls = [url+'/frame/'+str(args.frame-offset*subsampleRate) for url,offset in zip(filtered_urls,offsets) if offset is not None]


  # extracting frames for the timelapse
  video_timelapse = readTimelapse(aligned_urls)

  # saving the video
  if args.movie_name is not None:
      saveTimelapse(video_timelapse,args.movie_name)
  else:
      saveTimelapse(video_timelapse,'timelapse-'+args.start_date.replace('/','')+'-'+args.end_date.replace('/','')+'-frame'+str(args.frame)+'.mp4')
