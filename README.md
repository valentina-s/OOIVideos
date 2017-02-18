#### Processing of OOI Videos.

To extract scenes based on rolling statistics (using only variance)

python code/calculate_video_statistics.py opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_02_CAMHDA301-20160102T210000Z.mp4

python code/extract_scenes.py results/RollingVariance_20160102T210000Z.csv results/bounds.csv

----
### Create a time lapse within a period of time by aligning rolling covariances (Serial version)

#### Setup:
It might be needed to first run:

```{bash}
    sudo apt-get install python-tk
```

Then
```{bash}
git clone https://github.com/valentina-s/OOIVideos

virtualenv timelapse
source timelapse/activate/bin
pip install -r timelapse_requirements.txt
cd src
```

#### Run:
```{bash}
time python align_timelapse.py --start_date 2016/05/01 --end_date 2016/05/05 --sampling DAILY --frame 5000 --subsampleRate 100 --interval 2
```

The final result is stored in a `timeseries.mp4` file.
