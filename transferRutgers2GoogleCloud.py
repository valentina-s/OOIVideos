from bs4 import BeautifulSoup
import sys
if sys.version_info >= (3,0):
  from urllib.request import urlopen
else:
  from urllib2 import urlopen
if sys.version_info >= (3,0):
  from urllib.error import HTTPError, URLError
  from urllib.parse import urlparse, urljoin
else :
  from urllib2 import HTTPError, URLError
  from urlparse import urlparse, urljoin
import os.path, errno
import shutil
import subprocess as subprocess
if sys.version_info >= (3,0):
  from concurrent.futures import *

from itertools import islice
import ssl

# Crawl a Thredds server and generate a list of all movie files

def domainof(url):
  parts = urlparse(url)
  domain = '{uri.scheme}://{uri.netloc}'.format(uri=parts)
  return domain

def moviecrawl_html(url):
  '''
      This function crawls throught the html at the url,
      and extracts text fields containing '.mp4',
      thus generating a list of the filenames in this dir.
  '''

  domain = domainof(url)
  response = urlopen(url,context = ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), "html.parser")

  # create a list .mp4 filenames in this directory
  movienames = []
  for item in soup.find_all(text=True):
    if 'mp4' in item:
      yield url+'/'+item

def getlocalpath(url, localroot="."):
    # Return the local path derived from the url
    parts = urlparse(url)
    file_name = parts.path

    path, basefile = os.path.split(file_name)
    loc = os.path.abspath(localroot)
    remote = os.path.normpath("." + path)
    localfiledir = os.path.join(loc,remote)
    # create the directory tree idempotently
    mkdir_p(localfiledir)
    local_file_name = os.path.join(localfiledir, basefile)
    return local_file_name

def download(url, local_file_name):
    # download url to local_File_name, return true if successful
    try:
        response = urlopen(url,context = ssl._create_unverified_context())

        CHUNK = 16 * 1024
        with open(local_file_name, 'wb') as f:
          while True:
            chunk = response.read(CHUNK)
            if not chunk: break
            f.write(chunk)
          f.close()

        return True
    #handle errors
    except HTTPError as e:
        print("HTTP Error:",e.code , url)
    except URLError as e:
        print("URL Error:",e.reason , url)

    return False

def mkdir_p(path):
    # create a directory tree idempotently, like mkdir -p
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def delete(filepath):
  os.remove(filepath)

def getgooglename(localfile):
  prefix = os.path.commonprefix([os.getcwd(), localfile])
  relativepath = localfile[len(prefix)+1:]
  googlepath = relativepath.replace("/", "_")
  return googlepath

def uploadtoGoogle(localfile, folderid="0Bxkqjvq_AAi_bVU0bDFocFl0SG8"):
  # upload a file to Google drive using gdcp.  Assumes gdcp is installed and configured
  googlepath = getgooglename(localfile)
  subprocess.call(["gdcp", "upload", "-p", folderid, "-t", googlepath, localfile])
  return googlepath

def googleexists(googlepath, folderid="0Bxkqjvq_AAi_bVU0bDFocFl0SG8"):
  # Checks existence.  Dangerous -- returns true if filename is a substring of any existing filename
  proc = subprocess.Popen(["gdcp", "list", "--id", folderid], stdout=subprocess.PIPE)
  result = proc.stdout.read()
  return googlepath in result

def fetch(url, localroot="."):
  # Download a url, upload it to Google drive, delete local copy
  localfile = getlocalpath(url, localroot)
  gname = getgooglename(localfile)
  if not googleexists(gname):
    print("downloading ", url)
    downloaded = download(url, localfile)
    if downloaded:
      print("uploading", localfile)
      uploadtoGoogle(localfile, gname)
      print("cleaning up")
      delete(localfile)
      return googlename
  else:
    print("....already uploaded ", localfile)


def batched_executor(f, iterable, pool, batch_size):
  it = iter(iterable)
  # Submit the first batch of tasks.
  futures = set(pool.submit(f, x) for x in islice(it, batch_size))
  while futures:
    done, futures = wait(futures, return_when=FIRST_COMPLETED)
    # Replenish submitted tasks up to the number that completed.
    futures.update(pool.submit(f, x) for x in islice(it, len(done)))
    for result in done: yield result

def transload(rooturl):
  # Crawl the ooi OPeNDAP pages, download files, move to Google drive
  N = 5
  with ThreadPoolExecutor(max_workers=N) as pool:
    for result in batched_executor(fetch, moviecrawl_html(url), pool, N):
      yield result

def test():
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/02/10/CAMHDA301-20160210T180000Z.mp4"
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/catalog.xml"
  url = "https://rawdata.oceanobservatories.org/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04"
  for url in moviecrawl_html(url):
    local_file_name = getlocalpath(url,'/media/7AA2E24AA2E20A89/ooifetched_videos')
    #local_file_name = '/media/7AA2E24AA2E20A89/ooifetched_videos'+local_file_name
    if not os.path.exists(local_file_name):
      download(url, local_file_name)
#    uploadtoGoogle(local_file_name)
  #print googleexists("opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_01_CAMHDA301-20160101T000000Z.mp4")
def  download_month(month,year):
    url = "https://rawdata.oceanobservatories.org/files/RS03ASHS/PN03B/06-CAMHDA301/"+str(year)+'{:02d}'.format(month)
    from dateutil import rrule
    from datetime import datetime
    import subprocess

    date_start = '2016'+'{:02d}'.format(month)+'01'
    date_end = '2016'+'{:02d}'.format(month+1)+'01'

    dates = [dt.strftime('%Y/%m/%d') for dt in rrule.rrule(rrule.DAILY,
                      dtstart=datetime.strptime(date_start, '%Y%m%d'),
                      until=datetime.strptime(date_end, '%Y%m%d'))][:-1]

    # looping through each day of the month
    for date in dates:
        url = "https://rawdata.oceanobservatories.org/files/RS03ASHS/PN03B/06-CAMHDA301/"+date
        i = 1
        for url in moviecrawl_html(url):
            print(url)
            # download to local file


            local_file_name = getlocalpath(url,'../temp_storage/fetched_ooivideos')

            #local_file_name = '/media/7AA2E24AA2E20A89/ooifetched_videos'+local_file_name
            # if not os.path.exists(local_file_name):
            #if i==1 or not os.path.exists(local_file_name):

            #if i==1:# if I want to download only one file
            download(url, local_file_name)
            print(local_file_name)
            i = i+1
            # uploading to google drive
            # subprocess.Popen("echo Starting Upload to Google Cloud", shell=True, stderr=subprocess.PIPE)
            # subprocess.Popen("touch temp.txt", shell=True, stderr=subprocess.PIPE)
            # subprocess.Popen("mkdir test_dir", shell=True, stderr=subprocess.PIPE)
            # command = "gsutil cp -r /media/7AA2E24AA2E20A89/fetched_ooivideos  gs://ooivideos-test-bucket/temp_dir"
            # command = "gsutil cp -r test_dir gs://ooivideos-test-bucket/temp_dir"
            # subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)

        command = "gsutil -m cp -r ../temp_storage/fetched_ooivideos/*  gs://ooivideos-test-bucket/temp_dir/"
        # command = "gsutil cp -r test_dir gs://ooivideos-test-bucket/temp_dir"
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        _, p_stderr = p.communicate()
        # removing from local disk
        subprocess.Popen('rm -r ../temp_storage/fetched_ooivideos/*',shell=True, stderr=subprocess.PIPE,stdout=subprocess.PIPE)










if __name__ == '__main__':
  import argparse
  from datetime import datetime, timedelta
  from collections import OrderedDict

  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/catalog.xml"

  parser = argparse.ArgumentParser(description="Format is mm/yy")
  parser.add_argument('-start_month','--start_month',type=str,required=False)
  parser.add_argument('-end_month','--end_month',type=str,required=False)
  parser.add_argument('-month','--month',type=str,required=False)
  args = parser.parse_args()


  # transfer files by months
  if args.month:
      m = datetime.strptime(args.month, "%m/%Y").strftime(r"%m-%Y")
      print('Downloading month ', m)
      download_month(int(m[:2]),int(m[2:]))

  elif args.start_month is not None and args.end_month is not None:
      #start_month = int(args.start_month[:2])
      #end_month = int(args.end_month[:2])
      dates = [args.start_month,args.end_month]
      start, end = [datetime.strptime(_, "%m/%Y") for _ in dates]
      listOfMonths = OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys()
      for m in listOfMonths:
          print('Downloading month ', m)
          download_month(int(m[:2]), int(m[2:]))
  else:
      print('You should supply either a --month argument or --start_date and --end_date arguments.')



  #for googlefile in transload(url):
  #  pass
