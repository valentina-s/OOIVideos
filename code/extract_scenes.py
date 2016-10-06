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
    # the assumption is that the first scene is static and binary=1

    binary = np.array(np.array(measure).ravel()<thresh).astype('int')
    diff = binary[1:] - binary[:-1]
    # I am adding one since the first one will always be zero
    lower_bound = list(np.where(diff == 1)[0]+1)

    if binary[0]==1:
        lower_bound.insert(0,0)

    # I am adding one since the first one will always be zero.
    upper_bound = list(np.where(diff == -1)[0]+1)
    if binary[-1] == 1:
        upper_bound.append(len(binary)-1)


    # wrapping the final result as a list as zip in Python 3 is not an iterator
    return(list(zip(lower_bound,upper_bound)))

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
