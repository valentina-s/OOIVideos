#### Processing of OOI Videos.

To extract scenes based on rolling statistics (using only variance)

python code/calculate_video_statistics.py opendap_hyrax_large_format_RS03ASHS-PN03B-06-CAMHDA301_2016_01_02_CAMHDA301-20160102T210000Z.mp4

python code/extract_scenes.py results/RollingVariance_20160102T210000Z.csv results/bounds.csv
