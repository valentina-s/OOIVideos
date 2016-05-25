""" Calculate scene bounds by thresholding a 1D measure.
"""
import numpy as np

def extractSceneBounds(measure, thresh = '2median'):
    """
        This function extracts the bounds of the scenes.


        Inputs
        ------
            measure: 1D ndarray
            thresh: the default is 2*median, user can provide a value
            #TODO allow for a user defined function

        Outputs
        -------
            list of tuples: starting and ending time point for each scene

    Note: how to treat timestamps if they are in the csv file?
          for now saving frame numbers assuming no subsampling

    """
    if thresh == '2median':
        thresh = 2*np.median(measure)

    binary = np.array(np.array(measure)<thresh).astype('int')
    diff = binary[1:] - binary[:-1]
    upper_bound = np.where(diff == 1)[0]
    lower_bound = np.where(diff == -1)[0]

    return(zip(list(lower_bound),list(upper_bound)))

def main():
    """
        This script reads a 1D measure, which stores some property of a video
        file over time, thresholds it to detect static scenes and stores their
        bounds into a csv file of the form:
        LB  | UB
        ---------
        ... | ...
        ... | ...

        Inputs
        -----
        argv[1] name of .csv file containing the measure as a single column
        argv[2] name of output .csv file containing the static scene bounds

        Usage
        -----
        > python extract_scenes.py filename_in filename_out

    """

    import sys
    import os
    import pandas as pd
    filename_in = sys.argv[1]
    filename_out = sys.argv[2]

    print(os.getcwd())

    try:
        measure = pd.read_csv(os.path.join(os.getcwd(),filename_in), index_col = None)
    except IOError:
        print ("Could not read file:", os.path.join(os.getcwd(),filename_in))

    # extract scenes
    bounds = extractSceneBounds(measure)


    # write output in two column csv
    pd.DataFrame(bounds,columns = ['LB','UB']).to_csv(os.path.join(os.getcwd(),filename_out), index = None)


if __name__ == '__main__':
    main()
