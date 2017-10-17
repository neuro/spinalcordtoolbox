#!/usr/bin/env python
#########################################################################################
#
# Test function for sct_analyze_texture script
#
# ---------------------------------------------------------------------------------------
# Copyright (c) 2017 Polytechnique Montreal <www.neuro.polymtl.ca>
# Author: charley
#
# About the license: see the file LICENSE.TXT
#########################################################################################

from pandas import DataFrame
import numpy as np
from msct_image import Image
import sct_utils as sct

def init(param_test):
    """
    Initialize class: param_test
    """
    # initialization
    default_args = ['-i t2/t2.nii.gz -m t2/t2_seg.nii.gz -feature contrast -distance 1']  # default parameters
    param_test.difference_threshold = 0.95
    param_test.fname_groundtruth = param_test.path_data + 't2/t2_contrast_1_mean_ref.nii.gz'  # file name suffix for ground truth (used for integrity testing)
    # param_test.contrast = 't2'

    # assign default params
    if not param_test.args:
        param_test.args = default_args

    return param_test


def test_integrity(param_test):
    """
    Test integrity of function
    """
    # extract name of output texture file
    file_texture = param_test.path_output + sct.add_suffix(param_test.file_input, '_contrast_1_mean')

    # open output
    try:
        im_texture = Image(file_texture)
    except:
        param_test.output += 'ERROR: Cannot open output texture file: ' + im_texture
        param_test.status = 99
        return param_test

    # open ground truth
    try:
        im_texture_ref = Image(param_test.fname_groundtruth)
    except:
        param_test.output += 'ERROR: Cannot open ground truth texture file: ' + param_test.fname_groundtruth
        param_test.status = 99
        return param_test

    # Substract generated image and image from database
    diff_im = im_texture.data - im_texture_ref.data
    cmpt_diff_vox = np.count_nonzero(diff_im)
    cmpt_tot_vox = np.count_nonzero(im_texture_ref.data)
    difference_vox = float(cmpt_tot_vox - cmpt_diff_vox) / cmpt_tot_vox

    param_test.output += 'Computed difference: ' + str(difference_vox)
    param_test.output += 'Difference threshold (if computed difference lower: fail): ' + str(param_test.difference_threshold)

    if difference_vox < param_test.difference_threshold:
        param_test.status = 99

    # transform results into Pandas structure
    param_test.results = DataFrame(index=[param_test.path_data], data={'status': param_test.status, 'output': param_test.output, 'difference_vox': difference_vox, 'duration [s]': param_test.duration})

    return param_test
