import numpy as np
from generate_urls import generate_urls
from calculate_video_statistics import calculateRollingStats_fromUrl


from urllib.request import urlopen
from urllib.error import URLError

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

def alignTimelapse(aligned_urls):
    video_timelapse = []
    for url in aligned_urls:
        try:
            video_timelapse.append(io.imread(url))
        except:
            pass
    return(video_timelapse)


def saveTimelapse(video_timelapse,filename):
    import imageio
    """

    """

    writer = imageio.get_writer(filename, fps=5)

    for im in video_timelapse:
        writer.append_data(im)
    writer.close()

if __name__ == '__main__':
  import argparse
  from datetime import datetime, timedelta
  from collections import OrderedDict

  parser = argparse.ArgumentParser(description="Format is mm/yy")
  parser.add_argument('-start_date','--start_date',type=str,required=True)
  parser.add_argument('-frame','--frame',type=int,required=True)
  parser.add_argument('-end_date','--end_date',type=str,required=True)
  parser.add_argument('-sampling','--sampling',type=str,required=True)
  args = parser.parse_args()

  list_movie_urls = generate_urls(args.start_date,args.end_date,args.sampling)

  filtered_urls = [url for url in list_movie_urls if ping(url)]

  #  calculate rolling variance
  res = [calculateRollingStats_fromUrl(url,lag=3,subsampleRate=10,frame_start=3000,frame_end=7000) for url in filtered_urls]
  res_np = [np.array(r) for r in res]

  # align all time series
  offsets = []
  for i in range(1,len(res_np)):
      if res_np[i].shape != ():
          offset = sync_corr(res_np[0],res_np[i])
          offsets.append(offset)
      else:
          offsets.append(None)

  offsets = [0]+offsets
  print(offsets)
  aligned_urls = [url+'/frame/'+str(args.frame-offset*10) for url,offset in zip(filtered_urls,offsets) if offset is not None]
  print(aligned_urls)
  video_timelapse = alignTimelapse(aligned_urls)
  saveTimelapse(video_timelapse,'timelapse.mp4')
