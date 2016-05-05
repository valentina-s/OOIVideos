from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError, URLError
from urlparse import urlparse, urljoin
import os.path, errno
import shutil
import subprocess32 as subprocess
from concurrent.futures import *
from itertools import islice
import ssl

# Crawl a Thredds server and generate a list of all movie files

def domainof(url):
  parts = urlparse(url)
  domain = '{uri.scheme}://{uri.netloc}'.format(uri=parts)
  return domain

def moviecrawl(url):
  # Walk a Thredds directory and generate a list of all .mov and .mp4 files
  domain = domainof(url)
  response = urlopen(url,context = ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), "html.parser")

  # yield all movie urls on this page, if any
  for ds in soup.find_all("thredds:dataset"):
    movurl = domain + ds[u'id']
    if "mov" in movurl:
        yield movurl
    if "mp4" in movurl:
        yield movurl

  for ds in soup.find_all("thredds:dataset"):
    base = ds[u'id']
    for c in ds.find_all("thredds:catalogref"):
      newurl = urljoin(urljoin(domain,base), c[u'xlink:href'])
      for movieurl in moviecrawl(newurl):
        yield movieurl

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
            movienames.append(item)

    return(movienames)


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
    except HTTPError, e:
        print "HTTP Error:",e.code , url
    except URLError, e:
        print "URL Error:",e.reason , url

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
    print "downloading ", url
    downloaded = download(url, localfile)
    if downloaded:
      print "uploading", localfile
      uploadtoGoogle(localfile, gname)
      print "cleaning up"
      delete(localfile)
      return googlename
  else:
    print "....already uploaded ", localfile


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
    for result in batched_executor(fetch, moviecrawl(url), pool, N):
      yield result

def test():
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/02/10/CAMHDA301-20160210T180000Z.mp4"
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/catalog.xml"

  for url in moviecrawl(url):
    local_file_name = getlocalpath(url)
    if not os.path.exists(local_file_name):
      download(url)
    uploadtoGoogle(local_file_name)
  #print googleexists("opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_01_CAMHDA301-20160101T000000Z.mp4")

if __name__ == '__main__':
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/catalog.xml"
  test()
  #for googlefile in transload(url):
  #  pass
