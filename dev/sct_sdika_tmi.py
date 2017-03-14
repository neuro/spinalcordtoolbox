# ****************************      IMPORT      *****************************************  
# Utils Imports
import pickle
import os
import nibabel as nib #### A changer en utilisant Image
import shutil
import numpy as np
from math import sqrt
from collections import Counter
import random
import json
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import pandas as pd
from scipy.stats import ttest_rel, ttest_ind
# SCT Imports
from msct_image import Image
import sct_utils as sct
from sct_sdika import plot_comparison_classifier_oneline
# ***************************************************************************************

# ****************************      UTILS FUNCTIONS      ********************************

def create_folders_local(folder2create_lst):
    """
    
      Create folders if not exist
    
          Inputs:
              - folder2create_lst [list of string]: list of folder paths to create
          Outputs:
              -
    
    """           
    
    for folder2create in folder2create_lst:
        if not os.path.exists(folder2create):
            os.makedirs(folder2create)


def partition_resol(path_local, cc):

    fname_pkl_out = path_local + 'resol_dct_' + cc + '.pkl'
    # if not os.path.isfile(fname_pkl_out):
    path_dataset_pkl = path_local + 'dataset_lst_' + cc + '.pkl'
    dataset = pickle.load(open(path_dataset_pkl, 'r'))
    dataset_subj_lst = [f.split('.img')[0].split('_'+cc)[0] for f in dataset]
    dataset_path_lst = [path_local + 'input_nii_' + cc + '/' + f.split('.img')[0]+'.nii.gz' for f in dataset]

    resol_dct = {'sag': [], 'ax': [], 'iso': []}
    in_plane_ax, in_plane_iso, in_plane_sag = [], [], []
    thick_ax, thick_iso, thick_sag = [], [], []
    for img_path, img_subj in zip(dataset_path_lst, dataset_subj_lst):
        img = Image(img_path)

        resol_lst = [round(dd) for dd in img.dim[4:7]]
        if resol_lst.count(resol_lst[0]) == len(resol_lst):
            resol_dct['iso'].append(img_subj)
            in_plane_iso.append(img.dim[4])
            in_plane_iso.append(img.dim[5])
            thick_iso.append(img.dim[6])
        elif resol_lst[1]<resol_lst[0]:
            resol_dct['sag'].append(img_subj)
            in_plane_sag.append(img.dim[5])
            in_plane_sag.append(img.dim[6])
            thick_sag.append(img.dim[4])
        else:
            resol_dct['ax'].append(img_subj)
            in_plane_ax.append(img.dim[4])
            in_plane_ax.append(img.dim[5])
            thick_ax.append(img.dim[6])

        del img

    print '\n ax'
    print len(resol_dct['ax'])
    if len(resol_dct['ax']):
        print min(in_plane_ax), max(in_plane_ax)
        print min(thick_ax), max(thick_ax)
        print thick_ax
    print '\n iso'
    print len(resol_dct['iso'])
    if len(resol_dct['iso']):
        print min(in_plane_iso), max(in_plane_iso)
        print min(thick_iso), max(thick_iso)
    print '\n sag'
    print len(resol_dct['sag'])
    if len(resol_dct['sag']):
        print min(in_plane_sag), max(in_plane_sag)
        print min(thick_sag), max(thick_sag)

        # pickle.dump(resol_dct, open(fname_pkl_out, "wb"))
    # else:
    #     with open(fname_pkl_out) as outfile:    
    #         resol_dct = pickle.load(outfile)
    #         outfile.close()

    # return resol_dct

# ***************************************************************************************



# ****************************      STEP 0 FUNCTIONS      *******************************

def find_img_testing(path_large, contrast, path_local):
    """
    
      Explore a database folder (path_large)...
      ...and extract path to images for a given contrast (contrast)
    
          Inputs:
              - path_large [string]: path to database
              - contrast [string]: contrast of interest ('t2', 't1', 't2s')
          Outputs:
              - path_img [list of string]: list of image path
              - path_seg [list of string]: list of segmentation path
    
    """   

    center_lst, pathology_lst, path_img, path_seg = [], [], [], []
    for subj_fold in os.listdir(path_large):
        path_subj_fold = path_large + subj_fold + '/'

        if os.path.isdir(path_subj_fold):
            contrast_fold_lst = [contrast_fold for contrast_fold in os.listdir(path_subj_fold) 
                                                    if os.path.isdir(path_subj_fold+contrast_fold+'/')]
            contrast_fold_lst_oI = [contrast_fold for contrast_fold in contrast_fold_lst 
                                                    if contrast_fold==contrast or contrast_fold.startswith(contrast+'_')]
            
            # If this subject folder contains a subfolder related to the contrast of interest
            if len(contrast_fold_lst_oI):

                # Depending on the number of folder of interest:
                if len(contrast_fold_lst_oI)>1:
                    # In our case, we prefer axial images when available
                    ax_candidates = [tt for tt in contrast_fold_lst_oI if 'ax' in tt]
                    if len(ax_candidates):
                        contrast_fold_oI = ax_candidates[0]
                    else:
                        contrast_fold_oI = contrast_fold_lst_oI[0]                                               
                else:
                    contrast_fold_oI = contrast_fold_lst_oI[0]

                # For each subject and for each contrast, we want to pick only one image
                path_contrast_fold = path_subj_fold+contrast_fold_oI+'/'

                # If segmentation_description.json is available
                if os.path.exists(path_contrast_fold+'segmentation_description.json'):

                    with open(path_contrast_fold+'segmentation_description.json') as data_file:    
                        data_seg_description = json.load(data_file)
                        data_file.close()

                    # If manual segmentation of the cord is available
                    if len(data_seg_description['cord']):

                        # Extract data information from the dataset_description.json
                        with open(path_subj_fold+'dataset_description.json') as data_file:    
                            data_description = json.load(data_file)
                            data_file.close()

                        path_img_cur = path_contrast_fold+contrast_fold_oI+'.nii.gz'
                        path_seg_cur = path_contrast_fold+contrast_fold_oI+'_seg_manual.nii.gz'
                        if os.path.exists(path_img_cur) and os.path.exists(path_seg_cur):
                            path_img.append(path_img_cur)
                            path_seg.append(path_seg_cur)
                            center_lst.append(data_description['Center'])
                            pathology_lst.append(data_description['Pathology'])
                        else:
                            print '\nWARNING: file lacks: ' + path_contrast_fold + '\n'


    img_patho_lstoflst = [[i.split('/')[-3].split('.nii.gz')[0].split('_t2')[0], p] for i,p in zip(path_img,pathology_lst)]
    img_patho_dct = {}
    for ii_pp in img_patho_lstoflst:
        if not ii_pp[1] in img_patho_dct:
            img_patho_dct[ii_pp[1]] = []
        img_patho_dct[ii_pp[1]].append(ii_pp[0])
    if '' in img_patho_dct:
        for ii in img_patho_dct['']:
            img_patho_dct['HC'].append(ii)
        del img_patho_dct['']
    if u'NC' in img_patho_dct:
        for ii in img_patho_dct[u'NC']:
            img_patho_dct['HC'].append(ii)
        del img_patho_dct[u'NC']
    print img_patho_dct.keys()
    fname_pkl_out = path_local + 'patho_dct_' + contrast + '.pkl'
    pickle.dump(img_patho_dct, open(fname_pkl_out, "wb"))

    # Remove duplicates
    center_lst = list(set(center_lst))
    center_lst = [center for center in center_lst if center != ""]
    # Remove HC and non specified pathologies
    pathology_lst = [patho for patho in pathology_lst if patho != "" and patho != "HC" and patho != "NC"]
    pathology_dct = {x:pathology_lst.count(x) for x in pathology_lst}

    print '\n\n***************Contrast of Interest: ' + contrast + ' ***************'
    print '# of Subjects: ' + str(len(path_img))
    print '# of Centers: ' + str(len(center_lst))
    print 'Centers: ' + ', '.join(center_lst)
    print 'Pathologies:'
    print pathology_dct
    print '\n'

    return path_img, path_seg

def transform_nii_img(img_lst, path_out):
    """
    
      List .nii images which need to be converted to .img format
      + set same orientation RPI
      + set same value format (int16)
    
          Inputs:
              - img_lst [list of string]: list of path to image to transform
              - path_out [string]: path to folder where to save transformed images
          Outputs:
              - path_img2convert [list of string]: list of image paths to convert
    
    """   

    path_img2convert = []
    for img_path in img_lst:
        path_cur = img_path
        path_cur_out = path_out + '_'.join(img_path.split('/')[5:7]) + '.nii.gz'
        if not os.path.isfile(path_cur_out):
            shutil.copyfile(path_cur, path_cur_out)
            sct.run('sct_image -i ' + path_cur_out + ' -type int16 -o ' + path_cur_out)
            sct.run('sct_image -i ' + path_cur_out + ' -setorient RPI -o ' + path_cur_out)
            # os.system('sct_image -i ' + path_cur_out + ' -type int16 -o ' + path_cur_out)
            # os.system('sct_image -i ' + path_cur_out + ' -setorient RPI -o ' + path_cur_out)
        path_img2convert.append(path_cur_out)

    return path_img2convert

def transform_nii_seg(seg_lst, path_out, path_gold):
    """
    
      List .nii segmentations which need to be converted to .img format
      + set same orientation RPI
      + set same value format (int16)
      + set same header than related image
      + extract centerline from '*_seg_manual.nii.gz' to create gold standard
    
          Inputs:
              - seg_lst [list of string]: list of path to segmentation to transform
              - path_out [string]: path to folder where to save transformed segmentations
              - path_gold [string]: path to folder where to save gold standard centerline
          Outputs:
              - path_segs2convert [list of string]: list of segmentation paths to convert
    
    """

    path_seg2convert = []
    for seg_path in seg_lst:
        path_cur = seg_path
        path_cur_out = path_out + '_'.join(seg_path.split('/')[5:7]) + '_seg.nii.gz'
        if not os.path.isfile(path_cur_out):
            shutil.copyfile(path_cur, path_cur_out)
            os.system('sct_image -i ' + path_cur_out + ' -setorient RPI -o ' + path_cur_out)

        path_cur_ctr = path_cur_out.split('.')[0] + '_centerline.nii.gz'
        if not os.path.isfile(path_cur_ctr):
            os.chdir(path_out)
            os.system('sct_process_segmentation -i ' + path_cur_out + ' -p centerline -ofolder ' + path_out)
            os.system('sct_image -i ' + path_cur_ctr + ' -type int16')
            path_input_header = path_cur_out.split('_seg')[0] + '.nii.gz'
            os.system('sct_image -i ' + path_input_header + ' -copy-header ' + path_cur_ctr)

        path_cur_gold = path_gold + '_'.join(seg_path.split('/')[5:7]) + '_centerline_gold.nii.gz'
        if not os.path.isfile(path_cur_gold) and os.path.isfile(path_cur_ctr):
            shutil.copyfile(path_cur_ctr, path_cur_gold)

        if os.path.isfile(path_cur_out):
            path_seg2convert.append(path_cur_out)
        if os.path.isfile(path_cur_ctr):
            path_seg2convert.append(path_cur_ctr)

    return path_seg2convert

def convert_nii2img(path_nii2convert, path_out):
    """
    
      Convert .nii images to .img format
    
          Inputs:
              - path_nii2convert [list of string]: list of path to images to convert
              - path_out [string]: path to folder where to save converted images
          Outputs:
              - fname_img [list of string]: list of converted images (.img format) paths
    
    """ 

    fname_img = []
    for img in path_nii2convert:
        path_cur = img
        path_cur_out = path_out + img.split('.')[0].split('/')[-1] + '.img'
        if not img.split('.')[0].split('/')[-1].endswith('_seg') and not img.split('.')[0].split('/')[-1].endswith('_seg_centerline'):
            fname_img.append(img.split('.')[0].split('/')[-1] + '.img')
        if not os.path.isfile(path_cur_out):
            os.system('sct_convert -i ' + path_cur + ' -o ' + path_cur_out)

    return fname_img

def prepare_dataset(path_local, cc, path_sct_testing_large):

    path_local_gold = path_local + 'gold_' + cc + '/'
    path_local_input_nii = path_local + 'input_nii_' + cc + '/'
    path_local_input_img = path_local + 'input_img_' + cc + '/'
    folder2create_lst = [path_local_input_nii, path_local_input_img, path_local_gold]
    create_folders_local(folder2create_lst)

    with open(path_local + 'path_' + cc + '.pkl') as outfile:    
        data_pd = pickle.load(outfile)
        outfile.close()

    path_fname_img = [pp+'.nii.gz' for pp in data_pd.path_sct.values.tolist()]
    path_fname_seg = [pp+'_seg_manual.nii.gz' for pp in data_pd.path_sct.values.tolist()]

    path_img2convert = transform_nii_img(path_fname_img, path_local_input_nii)
    path_seg2convert = transform_nii_seg(path_fname_seg, path_local_input_nii, path_local_gold)
    print len(path_seg2convert)
    # path_imgseg2convert = path_img2convert + path_seg2convert
    # fname_img_lst = convert_nii2img(path_imgseg2convert, path_local_input_img)

    # data_pd['path_loc'] = fname_img_lst
    # print data_pd

    # data_pd.to_pickle(path_local + 'path_' + cc + '.pkl')



# ****************************      STEP 0 FUNCTIONS      *******************************

def panda_dataset(path_local, cc, path_large):

  info_dct = {'subj_name': [], 'patho': [], 'resol': [], 'center': []}
  path_dct = {'subj_name': [], 'path_sct': []}
  for subj_fold in os.listdir(path_large):
    path_subj_fold = path_large + subj_fold + '/'
    if os.path.isdir(path_subj_fold):
        contrast_fold_lst = [contrast_fold for contrast_fold in os.listdir(path_subj_fold) 
                                                if os.path.isdir(path_subj_fold+contrast_fold+'/')]
        contrast_fold_lst_oI = [contrast_fold for contrast_fold in contrast_fold_lst 
                                                if contrast_fold==cc or contrast_fold.startswith(cc+'_')]
        
        # If this subject folder contains a subfolder related to the contrast of interest
        if len(contrast_fold_lst_oI):
            # Depending on the number of folder of interest:
            if len(contrast_fold_lst_oI)>1:
                # In our case, we prefer axial images when available
                ax_candidates = [tt for tt in contrast_fold_lst_oI if 'ax' in tt]
                if len(ax_candidates):
                    contrast_fold_oI = ax_candidates[0]
                else:
                    sup_candidates = [tt for tt in contrast_fold_lst_oI if 'sup' in tt]
                    if len(sup_candidates):
                      contrast_fold_oI = sup_candidates[0]
                    else:
                      contrast_fold_oI = contrast_fold_lst_oI[0]                                               
            else:
                contrast_fold_oI = contrast_fold_lst_oI[0]

            # For each subject and for each contrast, we want to pick only one image
            path_contrast_fold = path_subj_fold+contrast_fold_oI+'/'

            # If segmentation_description.json is available
            if os.path.exists(path_contrast_fold+'segmentation_description.json'):

                with open(path_contrast_fold+'segmentation_description.json') as data_file:    
                    data_seg_description = json.load(data_file)
                    data_file.close()

                # If manual segmentation of the cord is available
                if len(data_seg_description['cord']):

                    path_dct['subj_name'].append(subj_fold + '_' + contrast_fold_oI)
                    info_dct['subj_name'].append(subj_fold + '_' + contrast_fold_oI)
                    path_dct['path_sct'].append(path_contrast_fold + contrast_fold_oI)

                    # Extract data information from the dataset_description.json
                    with open(path_subj_fold+'dataset_description.json') as data_file:    
                        data_description = json.load(data_file)
                        data_file.close()

                    info_dct['center'].append(str(data_description['Center']))
                    if str(data_description['Pathology']) == '' or str(data_description['Pathology']) == 'NC':
                        info_dct['patho'].append('HC')
                    else:
                        info_dct['patho'].append(str(data_description['Pathology']))
                    info_dct['resol'].append('todo')


  info_pd = pd.DataFrame.from_dict(info_dct)
  path_pd = pd.DataFrame.from_dict(path_dct)

  hc_lst = info_pd[info_pd.patho=='HC'].subj_name.values.tolist()
  data_lst = info_pd.subj_name.values.tolist()
  lambda_rdn = 0.23
  random.shuffle(hc_lst, lambda: lambda_rdn)
  if cc == 't1':
    training_lst = hc_lst[:int(len(hc_lst)*0.4)]
  else:
    training_lst = hc_lst[:int(len(hc_lst)*0.2)]

  info_pd['train_test'] = ['test' for i in range(len(data_lst))]
  for s in training_lst:
      info_pd.loc[info_pd.subj_name==s,'train_test'] = 'train'

  print info_pd

  info_pd.to_pickle(path_local + 'info_' + cc + '.pkl')
  path_pd.to_pickle(path_local + 'path_' + cc + '.pkl')

def prepare_train(path_local, path_outdoor, cc, nb_img):

    path_outdoor_cur = path_outdoor + 'input_img_' + cc + '/'

    path_local_res_img = path_local + 'output_img_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_nii = path_local + 'output_nii_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_pkl = path_local + 'output_pkl_' + cc + '_'+ str(nb_img) + '/'
    path_local_train = path_local + 'input_train_' + cc + '_'+ str(nb_img) + '/'
    folder2create_lst = [path_local_train, path_local_res_img, path_local_res_nii, path_local_res_pkl]

    with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
        data_pd = pickle.load(outfile)
        outfile.close()

    valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()
    test_lst = data_pd[data_pd.valid_test == 'test']['subj_name'].values.tolist()

    with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
        data_dct = pickle.load(outfile)
        outfile.close()

    valid_data_lst, test_data_lst = [], []
    for dd in data_dct:
      ok_bool = 0
      for vv in valid_lst:
        if vv in dd and not ok_bool:
          valid_data_lst.append(dd)
          ok_bool = 1
      for tt in test_lst:
        if tt in dd and not ok_bool:
          test_data_lst.append(dd)
          ok_bool = 1

    print '\nExperiment: '
    print '... contrast: ' + cc
    print '... nb image used for training: ' + str(nb_img) + '\n'
    print '... nb image used for validation: ' + str(len(valid_lst)-nb_img) + '\n'
    print '... nb image used for testing: ' + str(len(test_lst)) + '\n'

    nb_img_valid = len(valid_lst)
    nb_sub_train = int(float(nb_img_valid)/(50))+1
    path_folder_sub_train = []
    for i in range(nb_sub_train):
        path2create = path_local_train + str(i).zfill(3) + '/'
        path_folder_sub_train.append(path2create)
        folder2create_lst.append(path2create)

    create_folders_local(folder2create_lst)

    train_lst = []
    while len(train_lst)<nb_img_valid:
      random.shuffle(valid_data_lst)
      for j in range(0, len(valid_data_lst), nb_img):
          s = valid_data_lst[j:j+nb_img]
          s = [ss.split('.')[0] for ss in s]
          if len(train_lst)<nb_img_valid:
            if len(s)==nb_img:
              train_lst.append(s)
          else:
            break     

    if os.listdir(path2create) == []: 
        for i, tt in enumerate(train_lst):
            stg, stg_seg = '', ''
            for tt_tt in tt:
                stg += path_outdoor_cur + tt_tt + '\n'
                stg_seg += path_outdoor_cur + tt_tt + '_seg' + '\n'
            path2save = path_folder_sub_train[int(float(i)/50)]
            with open(path2save + str(i).zfill(3) + '.txt', 'w') as text_file:
                text_file.write(stg)
                text_file.close()
            with open(path2save + str(i).zfill(3) + '_ctr.txt', 'w') as text_file:
                text_file.write(stg_seg)
                text_file.close()

    return path_local_train, valid_data_lst


def send_data2ferguson(path_local, pp_ferguson, cc, nb_img, data_lst, path_train, optiC_bool=False):
    """
    
      MAIN FUNCTION OF STEP 1
      Prepare training strategy and save it in 'ferguson_config.pkl'
      + send data to ferguson
      + send training files to ferguson
      + send training strategy to ferguson
    
          Inputs:
              - path_local [string]: working folder
              - path_ferguson [string]: ferguson working folder
              - cc [string]: contrast of interest
              - nb_img [int]: nb of images for training
          Outputs:
              - 
    
    """
    pickle_ferguson = {
                        'contrast': cc,
                        'nb_image_train': nb_img,
                        'valid_subj': data_lst,
                        'path_ferguson': pp_ferguson,
                        'svm_hog_alone': optiC_bool
                        }
    path_pickle_ferguson = path_local + 'ferguson_config.pkl'
    output_file = open(path_pickle_ferguson, 'wb')
    pickle.dump(pickle_ferguson, output_file)
    output_file.close()

    os.system('scp -r ' + path_train + ' ferguson:' + pp_ferguson)
    os.system('scp ' + path_pickle_ferguson + ' ferguson:' + pp_ferguson)


# ****************************      STEP 2 FUNCTIONS      *******************************

def pull_img_convert_nii_remove_img(path_local, path_ferguson, cc, nb_img):

    path_ferguson_res = path_ferguson + 'output_img_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_img = path_local + 'output_img_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_nii = path_local + 'output_nii_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_time = path_local + 'output_time_' + cc + '_'+ str(nb_img) + '/'
    create_folders_local([path_local_res_img, path_local_res_nii, path_local_res_time])
    create_folders_local([path_local_res_img, path_local_res_nii])

    # Pull .img results from ferguson
    os.system('scp -r ferguson:' + path_ferguson_res + ' ' + '/'.join(path_local_res_img.split('/')[:-2]) + '/')

    # Convert .img to .nii
    # Remove .img files
    for f in os.listdir(path_local_res_img):
        if not f.startswith('.'):
            path_res_cur = path_local_res_nii + f + '/'
            path_res_cur_time = path_local_res_time + f + '/'
            create_folders_local([path_res_cur, path_res_cur_time])
            if not os.path.exists(path_res_cur):
                os.makedirs(path_res_cur)

            training_subj = f.split('__')

            if os.path.isdir(path_local_res_img+f):
                for ff in os.listdir(path_local_res_img+f):
                    if ff.endswith('_ctr.hdr'):

                        path_cur = path_local_res_img + f + '/' + ff
                        path_cur_out = path_res_cur + ff.split('_ctr')[0] + '_centerline_pred.nii.gz'
                        img = nib.load(path_cur)
                        nib.save(img, path_cur_out)

                    elif ff.endswith('.txt'):
                        shutil.copyfile(path_local_res_img + f + '/' + ff, path_res_cur_time + ff)
                    elif ff == 'time.txt':
                        os.rename(path_local_res_img + f + '/time.txt', path_local_res_nii + f + '/time.txt')

                os.system('rm -r ' + path_local_res_img + f)

# ******************************************************************************************

# ****************************      STEP 3 FUNCTIONS      *******************************

def _compute_stats(img_pred, img_true, img_seg_true):
    """
        -> mse = Mean Squared Error on distance between predicted and true centerlines
        -> maxmove = Distance max entre un point de la centerline predite et de la centerline gold standard
        -> zcoverage = Pourcentage des slices de moelle ou la centerline predite est dans la sc_seg_manual
    """

    stats_dct = {
                    'mse': None,
                    'maxmove': None,
                    'zcoverage': None
                }


    count_slice, slice_coverage = 0, 0
    mse_dist = []
    for z in range(img_true.dim[2]):

        if np.sum(img_true.data[:,:,z]):
            x_true, y_true = [np.where(img_true.data[:,:,z] > 0)[i][0] 
                                for i in range(len(np.where(img_true.data[:,:,z] > 0)))]
            x_pred, y_pred = [np.where(img_pred.data[:,:,z] > 0)[i][0]
                                for i in range(len(np.where(img_pred.data[:,:,z] > 0)))]
           
            xx_seg, yy_seg = np.where(img_seg_true.data[:,:,z]==1.0)
            xx_yy = [[x,y] for x, y in zip(xx_seg,yy_seg)]
            if [x_pred, y_pred] in xx_yy:
                slice_coverage += 1

            x_true, y_true = img_true.transfo_pix2phys([[x_true, y_true, z]])[0][0], img_true.transfo_pix2phys([[x_true, y_true, z]])[0][1]
            x_pred, y_pred = img_pred.transfo_pix2phys([[x_pred, y_pred, z]])[0][0], img_pred.transfo_pix2phys([[x_pred, y_pred, z]])[0][1]

            dist = ((x_true-x_pred))**2 + ((y_true-y_pred))**2
            mse_dist.append(dist)

            count_slice += 1

    if len(mse_dist):
        stats_dct['mse'] = sqrt(sum(mse_dist)/float(count_slice))
        stats_dct['maxmove'] = sqrt(max(mse_dist))
        stats_dct['zcoverage'] = float(slice_coverage*100.0)/count_slice

    return stats_dct

def _compute_stats_file(fname_ctr_pred, fname_ctr_true, fname_seg_true, folder_out, fname_out):

    img_pred = Image(fname_ctr_pred)
    img_true = Image(fname_ctr_true)
    img_seg_true = Image(fname_seg_true)

    stats_file_dct = _compute_stats(img_pred, img_true, img_seg_true)

    create_folders_local([folder_out])

    pickle.dump(stats_file_dct, open(fname_out, "wb"))


def compute_dataset_stats(path_local, cc, nb_img):
    """
        MAIN FUNCTION OF STEP 3
        Compute validation metrics for each subjects
        + Save avg results in a pkl file for each subject
        + Save results in a pkl for each tuple (training subj, testing subj)

        Inputs:
              - path_local [string]: working folder
              - cc [string]: contrast of interest
              - nb_img [int]: nb of images for training
        Outputs:
              - 

    """
    path_local_nii = path_local + 'output_nii_' + cc + '_'+ str(nb_img) + '/'
    path_local_res_pkl = path_local + 'output_pkl_' + cc +'/'
    create_folders_local([path_local_res_pkl])
    path_local_res_pkl = path_local_res_pkl + str(nb_img) + '/'
    create_folders_local([path_local_res_pkl])
    path_local_gold = path_local + 'gold_' + cc + '/'
    path_local_seg = path_local + 'input_nii_' + cc + '/'

    for f in os.listdir(path_local_nii):
        if not f.startswith('.'):
            path_res_cur = path_local_nii + f + '/'
            print path_res_cur
            folder_subpkl_out = path_local_res_pkl + f + '/'

            for ff in os.listdir(path_res_cur):
                if ff.endswith('_centerline_pred.nii.gz'):
                    subj_name_cur = ff.split('_centerline_pred.nii.gz')[0]
                    fname_subpkl_out = folder_subpkl_out + 'res_' + subj_name_cur + '.pkl'

                    if not os.path.isfile(fname_subpkl_out):
                        path_cur_pred = path_res_cur + ff
                        path_cur_gold = path_local_gold + subj_name_cur + '_centerline_gold.nii.gz'
                        path_cur_gold_seg = path_local_seg + subj_name_cur + '_seg.nii.gz'

                        _compute_stats_file(path_cur_pred, path_cur_gold, path_cur_gold_seg, folder_subpkl_out, fname_subpkl_out)

# ******************************************************************************************

# ****************************      STEP 4 FUNCTIONS      *******************************

def find_id_extr_df(df, mm):

  if 'zcoverage' in mm:
    return [df[mm].max(), df[df[mm] == df[mm].max()]['id'].values.tolist()[0], df[mm].min(), df[df[mm] == df[mm].min()]['id'].values.tolist()[0]]
  else:
    return [df[mm].min(), df[df[mm] == df[mm].min()]['id'].values.tolist()[0], df[mm].max(), df[df[mm] == df[mm].max()]['id'].values.tolist()[0]]

def panda_trainer(path_local, cc):

    path_folder_pkl = path_local + 'output_pkl_' + cc + '/'

    for fold in os.listdir(path_folder_pkl):
      path_nb_cur = path_folder_pkl + fold + '/'
      
      if os.path.isdir(path_nb_cur) and fold != '0' and fold != '666' and fold != '11':
        print 'fold'
        fname_out_cur = path_folder_pkl + fold + '.pkl'
        metric_fold_dct = {'id': [], 'maxmove_moy': [], 'mse_moy': [], 'zcoverage_moy': [],
                          'maxmove_med': [], 'mse_med': [], 'zcoverage_med': []}

        for tr_subj in os.listdir(path_nb_cur):

            path_cur = path_nb_cur + tr_subj + '/'

            if os.path.isdir(path_cur):
              metric_fold_dct['id'].append(tr_subj)

              metric_cur_dct = {'maxmove': [], 'mse': [], 'zcoverage': []}
              for file in os.listdir(path_cur):
                if file.endswith('.pkl'):
                  with open(path_cur+file) as outfile:    
                    metrics = pickle.load(outfile)
                    outfile.close()
                  
                  for mm in metrics:
                    if mm in metric_cur_dct:
                      metric_cur_dct[mm].append(metrics[mm])

              metric_fold_dct['maxmove_med'].append(np.median(metric_cur_dct['maxmove']))
              metric_fold_dct['mse_med'].append(np.median(metric_cur_dct['mse']))
              metric_fold_dct['zcoverage_med'].append(np.median(metric_cur_dct['zcoverage']))

              metric_fold_dct['maxmove_moy'].append(np.mean(metric_cur_dct['maxmove']))
              metric_fold_dct['mse_moy'].append(np.mean(metric_cur_dct['mse']))
              metric_fold_dct['zcoverage_moy'].append(np.mean(metric_cur_dct['zcoverage']))

            metric_fold_pd = pd.DataFrame.from_dict(metric_fold_dct)
            metric_fold_pd.to_pickle(fname_out_cur)


        print '\nBest Trainer:'
        for mm in metric_fold_dct:
            if mm != 'id':
              find_id_extr_df(metric_fold_pd, mm)
              print '... ' + mm + ' : ' + find_id_extr_df(metric_fold_pd, mm)[1] + ' ' + str(find_id_extr_df(metric_fold_pd, mm)[0])

        print metric_fold_pd

def test_trainers_best(path_local, cc, mm, pp_ferg):

    path_folder_pkl = path_local + 'output_pkl_' + cc + '/'
    dct_tmp = {}
    for nn in os.listdir(path_folder_pkl):
        file_cur = path_folder_pkl + str(nn) + '.pkl'

        if os.path.isfile(file_cur):

          if nn != '0' and nn != '666':

            with open(file_cur) as outfile:    
              data_pd = pickle.load(outfile)
              outfile.close()

            if len(data_pd[data_pd[mm+'_med']==find_id_extr_df(data_pd, mm+'_med')[0]]['id'].values.tolist())>1:
              mm_avg = mm + '_moy'
            else:
              mm_avg = mm + '_med'

            val_best, fold_best = find_id_extr_df(data_pd, mm_avg)[0], find_id_extr_df(data_pd, mm_avg)[1]

            if mm == 'zcoverage':
                len_fail = len(data_pd[data_pd[mm+'_med']<= 90]['id'].values.tolist())
                len_sucess = len(data_pd[data_pd[mm+'_med']> 90]['id'].values.tolist())
                len_tot = len(data_pd['id'].values.tolist())
                print 'Percentage of trainer tel que avg. > 90% : ' + str(round(len_sucess*100.0/len_tot,2))

            elif mm == 'mse':
                len_fail = len(data_pd[data_pd[mm+'_med'] > 2]['id'].values.tolist())
                len_sucess = len(data_pd[data_pd[mm+'_med'] < 2]['id'].values.tolist())
                print len_sucess, len_fail 
                len_tot = len(data_pd['id'].values.tolist())
                print 'Percentage of trainer tel que avg. < 2 mm : ' + str(round(len_sucess*100.0/len_tot,2))

            print val_best, fold_best
            dct_tmp[nn] = [fold_best]

    path_input_train = path_local + 'input_train_' + cc + '_11/'
    path_input_train_best = path_input_train + '000/'

    create_folders_local([path_input_train, path_input_train_best])

    for nn in dct_tmp:
        path_input = path_local + 'input_train_' + cc + '_' + str(nn) + '/'
        for fold in os.listdir(path_input):
          if os.path.isfile(path_input + fold + '/' + str(dct_tmp[nn][0]).zfill(3) + '.txt'):
            file_in = path_input + fold + '/' + str(dct_tmp[nn][0]).zfill(3) + '.txt'
            file_seg_in = path_input + fold + '/' + str(dct_tmp[nn][0]).zfill(3) + '_ctr.txt'

            file_out = path_input_train_best + '0_' + str(nn).zfill(3) + '.txt'
            file_seg_out = path_input_train_best + '0_' + str(nn).zfill(3) + '_ctr.txt'        

            shutil.copyfile(file_in, file_out)
            shutil.copyfile(file_seg_in, file_seg_out)

    with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
      data_pd = pickle.load(outfile)
      outfile.close()

    valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()
    test_lst = data_pd[data_pd.valid_test == 'test']['subj_name'].values.tolist()

    with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
      data_dct = pickle.load(outfile)
      outfile.close()

    valid_data_lst, test_data_lst = [], []
    for dd in data_dct:
        ok_bool = 0
        for tt in test_lst:
          if tt in dd and not ok_bool:
            test_data_lst.append(dd)
            ok_bool = 1
        for vv in valid_lst:
          if vv in dd and not ok_bool:
            valid_data_lst.append(dd)
            ok_bool = 1

    send_data2ferguson(path_local, pp_ferg, cc, 11, test_data_lst, path_input_train)

# ******************************************************************************************


def plot_comparison_clf(path_local, clf_lst, nbimg_cc_dct, folder_name):

    classifier_name_lst = clf_lst
    path_output = path_local + 'plot_comparison/'
    create_folders_local([path_output])

    fname_out_pkl = path_output + '_'.join(classifier_name_lst) + '.pkl'

    dct_tmp = {'mse': [], 'zcoverage': [], 'resol': [], 'patho': [], 
            'contrast': [], 'classifier': [], 'classifier_constrast': [], 'id': []}

    for cc in nbimg_cc_dct:

        nb_img = nbimg_cc_dct[cc]
        path_pkl_sdika = path_local + 'output_pkl_' + cc + '/' + folder_name + '/0_' + str(nb_img).zfill(3) + '/res_'
        if clf_lst[0] == 'Hough':
            path_pkl_compare = path_local + 'propseg_pkl_' + cc + '/res_' + cc + '_'
        else:
            path_pkl_compare = path_local + 'output_pkl_' + cc + '/1111/0_111/res_'
     
        with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
          subj_lst = pickle.load(outfile)
          outfile.close()

        with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
          data_pd = pickle.load(outfile)
          outfile.close()

        valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()

        subj_lst = [t.split('.img')[0] for t in subj_lst]

        for classifier_path, classifier_name in zip([path_pkl_compare, path_pkl_sdika], classifier_name_lst):
            for subj in subj_lst:
                fname_pkl_cur = classifier_path + subj + '.pkl'
                if os.path.isfile(fname_pkl_cur) and not subj.split('_'+cc)[0] in valid_lst:
                    with open(fname_pkl_cur) as outfile:    
                        mm_cur = pickle.load(outfile)
                        outfile.close()
                    dct_tmp['id'].append(subj.split('_'+cc)[0])
                    dct_tmp['classifier'].append(classifier_name)
                    dct_tmp['resol'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['resol'].values.tolist()[0])
                    dct_tmp['patho'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['patho'].values.tolist()[0])
                    dct_tmp['classifier_constrast'].append(classifier_name+'_'+cc)
                    dct_tmp['contrast'].append(cc)
                    if mm_cur['zcoverage'] is None or mm_cur['zcoverage'] == 0.0:
                        dct_tmp['zcoverage'].append(0.0)
                        dct_tmp['mse'].append(None)
                    else:
                        dct_tmp['zcoverage'].append(mm_cur['zcoverage'])
                        dct_tmp['mse'].append(mm_cur['mse'])
                elif not subj.split('_'+cc)[0] in valid_lst and not classifier_name=='OptiC':
                    dct_tmp['zcoverage'].append(0.0)
                    dct_tmp['mse'].append(None)
                    dct_tmp['id'].append(subj.split('_'+cc)[0])
                    dct_tmp['classifier'].append(classifier_name)
                    dct_tmp['resol'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['resol'].values.tolist()[0])
                    dct_tmp['patho'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['patho'].values.tolist()[0])
                    dct_tmp['classifier_constrast'].append(classifier_name+'_'+cc)
                    dct_tmp['contrast'].append(cc)

    pd_2plot = pd.DataFrame.from_dict(dct_tmp)

    order_lst = []
    for clf_nn in clf_lst:
        for contr in ['t2', 't1', 't2s']:
            order_lst.append(clf_nn+'_'+contr)

    for mm_name in ['mse', 'zcoverage']:
        print '*****' + mm_name

        if mm_name != 'zcoverage':
            y_lim_min, y_lim_max = 0.01, 30
        else:
            y_lim_min, y_lim_max = 0, 101

        sns.set(style="whitegrid", palette="Set1", font_scale=1.3)
        palette_swarm = dict(ok = (0.2,0.2,0.2), no = 'firebrick')
        fig, axes = plt.subplots(1, 1, sharey='col', figsize=(24, 8))
        fig.subplots_adjust(left=0.05, bottom=0.05)
        if clf_lst[0] == 'Hough':
            color_dct = dict(Hough = 'darkorange', OptiC = 'c')
            palette_violon = dict(Hough_t2='gold', Hough_t1='royalblue', Hough_t2s='mediumvioletred', 
                          OptiC_t2='khaki', OptiC_t1='cornflowerblue', OptiC_t2s='pink')
        else:
            color_dct = dict(SVM = 'darkorange', OptiC = 'c')
            palette_violon = dict(SVM_t2='gold', SVM_t1='royalblue', SVM_t2s='mediumvioletred', 
                          OptiC_t2='khaki', OptiC_t1='cornflowerblue', OptiC_t2s='pink')
        a = plt.subplot(1, 1, 1)
        sns.violinplot(x='classifier_constrast', y=mm_name, data=pd_2plot, order=order_lst,
                              inner="quartile", cut=0, scale="count",
                              sharey=True,  palette=palette_violon)

        a_swarm = sns.swarmplot(x='classifier_constrast', y=mm_name, data=pd_2plot, 
                                order=order_lst, size=3,
                                color=(0.2,0.2,0.2))
        # a_swarm.legend_.remove()

        a.set_ylim([y_lim_min,y_lim_max])
        plt.yticks(size=30)
        a.set_ylabel('')    
        a.set_xlabel('')

        # plt.show()
        fig.tight_layout()
        fig.savefig(path_output + '_'.join(classifier_name_lst) + '_' + mm_name + '.png')
        plt.close()


        val_tot_ttest = [[],[]]
        for cccc in ['t2', 't1', 't2s']:
            val_ttest = []
            ziii = 0
            for ccllff in clf_lst:
                print '\n\n' + cccc + ' ' + ccllff
                values = pd_2plot[(pd_2plot.classifier_constrast==ccllff+'_'+cccc)][mm_name].values.tolist()
                values = [v for v in values if str(v)!='nan']

                stg = '\nMean: ' + str(round(np.mean(values),2))
                stg += '\nStd: ' + str(round(np.std(values),2))

                if mm_name != 'zcoverage':
                    stg += '\nMax: ' + str(round(np.max(values),2))
                else:
                    stg += '\nMin: ' + str(round(np.min(values),2))

                print stg
                print len(values)
                val_ttest.append(values)
                for vvv in values:
                    val_tot_ttest[ziii].append(vvv)
                ziii+=1
            print ttest_ind(val_ttest[0], val_ttest[1])[1]

        print ttest_ind(val_tot_ttest[0], val_tot_ttest[1])[1]



def plot_comparison_clf_patho(path_local, clf_lst, nbimg_cc_dct, folder_name):

    classifier_name_lst = clf_lst
    path_output = path_local + 'plot_comparison/'
    create_folders_local([path_output])

    dct_tmp = {'mse': [], 'zcoverage': [], 'resol': [], 'patho': [], 
            'contrast': [], 'classifier': [], 'classifier_patho': [], 'id': []}

    for cc in nbimg_cc_dct:

        nb_img = nbimg_cc_dct[cc]
        path_pkl_sdika = path_local + 'output_pkl_' + cc + '/' + folder_name + '/0_' + str(nb_img).zfill(3) + '/res_'
        if clf_lst[0] == 'Hough':
            path_pkl_compare = path_local + 'propseg_pkl_' + cc + '/res_' + cc + '_'
        else:
            path_pkl_compare = path_local + 'output_pkl_' + cc + '/1111/0_111/res_'
     
        with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
          subj_lst = pickle.load(outfile)
          outfile.close()

        with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
          data_pd = pickle.load(outfile)
          outfile.close()

        with open(path_local + 'patho_dct_' + cc + '.pkl') as outfile:    
          patho_dct = pickle.load(outfile)
          outfile.close()

        valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()

        subj_lst = [t.split('.img')[0] for t in subj_lst]

        for classifier_path, classifier_name in zip([path_pkl_compare, path_pkl_sdika], classifier_name_lst):
            for subj in subj_lst:
                fname_pkl_cur = classifier_path + subj + '.pkl'
                if os.path.isfile(fname_pkl_cur) and not subj.split('_'+cc)[0] in valid_lst:
                    with open(fname_pkl_cur) as outfile:    
                        mm_cur = pickle.load(outfile)
                        outfile.close()
                    dct_tmp['id'].append(subj.split('_'+cc)[0])
                    dct_tmp['classifier'].append(classifier_name)
                    dct_tmp['resol'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['resol'].values.tolist()[0])
                    hc_patient = data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['patho'].values.tolist()[0]
                    if hc_patient == 'patient':
                        for disease in patho_dct: 
                            if subj.split('_'+cc)[0] in patho_dct[disease]:
                                if str(disease)=='MS':
                                    dct_tmp['patho'].append('MS')
                                elif str(disease)=='CSM':
                                    dct_tmp['patho'].append('DCM')
                                else:
                                    dct_tmp['patho'].append('other')

                        if len(dct_tmp['patho']) != len(dct_tmp['resol']):
                            if '_MS_' in subj.split('_'+cc)[0]:
                                dct_tmp['patho'].append('MS')
                            elif 'sct_' in subj.split('_'+cc)[0] or '20150910_joshua' in subj.split('_'+cc)[0]:
                                dct_tmp['patho'].append('hc')                            
                            else:
                                dct_tmp['patho'].append(hc_patient)
                    else:
                        dct_tmp['patho'].append(hc_patient)
                    dct_tmp['classifier_patho'].append(classifier_name+'_'+hc_patient)
                    dct_tmp['contrast'].append(cc)
                    if mm_cur['zcoverage'] is None or mm_cur['zcoverage'] == 0.0:
                        dct_tmp['zcoverage'].append(0.0)
                        dct_tmp['mse'].append(None)
                    else:
                        dct_tmp['zcoverage'].append(mm_cur['zcoverage'])
                        dct_tmp['mse'].append(mm_cur['mse'])
                elif not subj.split('_'+cc)[0] in valid_lst and not classifier_name=='OptiC':
                    dct_tmp['zcoverage'].append(0.0)
                    dct_tmp['mse'].append(None)
                    dct_tmp['id'].append(subj.split('_'+cc)[0])
                    dct_tmp['classifier'].append(classifier_name)
                    dct_tmp['resol'].append(data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['resol'].values.tolist()[0])
                    hc_patient = data_pd[(data_pd.subj_name == subj.split('_'+cc)[0])]['patho'].values.tolist()[0]
                    if hc_patient == 'patient':
                        for disease in patho_dct: 
                            if subj.split('_'+cc)[0] in patho_dct[disease]:
                                if str(disease)=='MS':
                                    dct_tmp['patho'].append('MS')
                                elif str(disease)=='CSM':
                                    dct_tmp['patho'].append('DCM')
                                else:
                                    dct_tmp['patho'].append('other')

                        if len(dct_tmp['patho']) != len(dct_tmp['resol']):
                            if '_MS_' in subj.split('_'+cc)[0]:
                                dct_tmp['patho'].append('MS')
                            elif 'sct_' in subj.split('_'+cc)[0] or '20150910_joshua' in subj.split('_'+cc)[0]:
                                dct_tmp['patho'].append('hc')                            
                            else:
                                dct_tmp['patho'].append(hc_patient)
                    else:
                        dct_tmp['patho'].append(hc_patient)
                    dct_tmp['classifier_patho'].append(classifier_name+'_'+hc_patient)
                    dct_tmp['contrast'].append(cc)

    pd_res = pd.DataFrame.from_dict(dct_tmp)

    def make_stg(d):
        stg = 'Mean = ' + str(round(np.mean(d),2))
        stg += '\nStd = ' + str(round(np.std(d),2))
        return stg

    for m in ['zcoverage', 'mse']:
        print '\n\nMetric: ' + m

        for p in ['patient', 'hc']:
            if p == 'patient':
                print m
                data_patho_compare = pd_res[(pd_res.patho!='hc') & (pd_res.classifier==clf_lst[0])][m].values.tolist()
                print len(data_patho_compare)
                data_patho_compare = [d for d in data_patho_compare if str(d) != 'nan']
                print len(data_patho_compare)
                data_patho_optic = pd_res[(pd_res.patho!='hc') & (pd_res.classifier==clf_lst[1])][m].values.tolist()        
            else:
                data_patho_compare = pd_res[(pd_res.patho=='hc') & (pd_res.classifier==clf_lst[0])][m].values.tolist()
                data_patho_compare = [d for d in data_patho_compare if str(d) != 'nan']
                data_patho_optic = pd_res[(pd_res.patho=='hc') & (pd_res.classifier==clf_lst[1])][m].values.tolist()

            print '... for ' + p + ' (n_compare=' + str(len(data_patho_compare)) + ', n_optic=' + str(len(data_patho_optic)) + ')'
            print '... ... Mean_Compare = '+str(round(np.mean(data_patho_compare),2))
            print '... ... Mean_OptiC = '+str(round(np.mean(data_patho_optic),2))
            print '... ... Std_Compare = '+str(round(np.std(data_patho_compare),2))
            print '... ... Std_OptiC = '+str(round(np.std(data_patho_optic),2))
            print '... ... min_Compare = '+str(round(np.min(data_patho_compare),2))
            print '... ... min_OptiC = '+str(round(np.min(data_patho_optic),2))
            print '... ... max_Compare = '+str(round(np.max(data_patho_compare),2))
            print '... ... max_OptiC = '+str(round(np.max(data_patho_optic),2))
            print '... ... t-test p-value = '+str(ttest_ind(data_patho_optic, data_patho_compare)[1])

        # if m == 'zcoverage':
        #     y_lim_min, y_lim_max = 0, 101
        #     y_stg_loc = y_lim_min + 25
        # else:
        #     y_lim_min, y_lim_max = 0, 25
        #     y_stg_loc = y_lim_min + 20

        # order_lst = []
        # for clf_nn in clf_lst:
        #     for pppp in ['hc', 'patient']:
        #         order_lst.append(clf_nn+'_'+pppp)

        # sns.set(style="whitegrid", palette="Set1", font_scale=1.3)
        # palette_swarm = dict(MS = 'forestgreen', DCM = 'darkblue', other='m', hc=(0.2,0.2,0.2))
        # if clf_lst[0] == 'Hough':
        #     palette_violon = dict(Hough_hc='orange', Hough_patient='c',  
        #                           OptiC_hc='peachpuff', OptiC_patient='paleturquoise')
        # else:
        #     palette_violon = dict(SVM_hc='orange', SVM_patient='c',  
        #                           OptiC_hc='peachpuff', OptiC_patient='paleturquoise')           
        # fig, axes = plt.subplots(1, 1, sharey='col', figsize=(16, 8))
        # fig.subplots_adjust(left=0.05, bottom=0.05)

        # a = plt.subplot(1, 1, 1)
        # sns.violinplot(x='classifier_patho', y=m, data=pd_res, order=order_lst,
        #                         inner="quartile", cut=0, scale="count",
        #                         sharey=True,  palette=palette_violon)

        # a_swarm = sns.swarmplot(x='classifier_patho', y=m, data=pd_res, 
        #                           order=order_lst, size=3,
        #                           hue='patho', palette=palette_swarm)
        # a_swarm.legend_.remove()
        # a.set_ylabel('')
        # a.set_xlabel('')
        # a.set_ylim([y_lim_min,y_lim_max])
        # plt.yticks(size=30)

        # plt.show()
        # fig.tight_layout()
        # fig.savefig(path_output + 'patho_' + '_'.join(classifier_name_lst) + '_' + m + '.png')
        # plt.close()

def prepare_svmhog(path_local, cc, pp_ferg, nb_img):

    with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
        data_pd = pickle.load(outfile)
        outfile.close()

    valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()
    test_lst = data_pd[data_pd.valid_test == 'test']['subj_name'].values.tolist()

    with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
        data_dct = pickle.load(outfile)
        outfile.close()

    valid_data_lst, test_data_lst = [], []

    for dd in data_dct:
        ok_bool = 0
        for tt in test_lst:
          if tt in dd and not ok_bool:
            test_data_lst.append(dd)
            ok_bool = 1
        for vv in valid_lst:
          if vv in dd and not ok_bool:
            valid_data_lst.append(dd)
            ok_bool = 1

    path_local_train = path_local + 'input_train_' + cc + '_'+ str(nb_img) + '/'
    print valid_data_lst
    send_data2ferguson(path_local, pp_ferg, cc, 1, valid_data_lst, path_local_train, True)

def prepare_svmhog_test(path_local, cc, pp_ferg, mm):

    path_folder_pkl = path_local + 'output_pkl_' + cc + '/111/'
    file_cur = path_local + 'output_pkl_' + cc + '/111.pkl'
    if os.path.isfile(file_cur):

        with open(file_cur) as outfile:    
            data_pd = pickle.load(outfile)
            outfile.close()

        if len(data_pd[data_pd[mm+'_med']==find_id_extr_df(data_pd, mm+'_med')[0]]['id'].values.tolist())>1:
            mm_avg = mm + '_moy'
        else:
            mm_avg = mm + '_med'

        fold_best = find_id_extr_df(data_pd, mm_avg)[1]

    path_input_train_old = path_local + 'input_train_' + cc + '_1/'

    path_input_train = path_local + 'input_train_' + cc + '_111/'
    path_input_train_best = path_input_train + '000/'
    create_folders_local([path_input_train, path_input_train_best])

    for fold in os.listdir(path_input_train_old):
        if os.path.isfile(path_input_train_old + fold + '/' + str(fold_best).zfill(3) + '.txt'):
            file_in = path_input_train_old + fold + '/' + str(fold_best).zfill(3) + '.txt'
            file_seg_in = path_input_train_old + fold + '/' + str(fold_best).zfill(3) + '_ctr.txt'
            print file_in, file_seg_in
            file_out = path_input_train_best + '0_' + str(111).zfill(3) + '.txt'
            file_seg_out = path_input_train_best + '0_' + str(111).zfill(3) + '_ctr.txt'        
            print file_out, file_seg_out
            shutil.copyfile(file_in, file_out)
            shutil.copyfile(file_seg_in, file_seg_out)



    with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
        data_pd = pickle.load(outfile)
        outfile.close()

    valid_lst = data_pd[data_pd.valid_test == 'train']['subj_name'].values.tolist()
    test_lst = data_pd[data_pd.valid_test == 'test']['subj_name'].values.tolist()

    with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
        data_dct = pickle.load(outfile)
        outfile.close()

    valid_data_lst, test_data_lst = [], []
    for dd in data_dct:
        ok_bool = 0
        for tt in test_lst:
            if tt in dd and not ok_bool:
                test_data_lst.append(dd)
                ok_bool = 1
        for vv in valid_lst:
            if vv in dd and not ok_bool:
                valid_data_lst.append(dd)
                ok_bool = 1

    send_data2ferguson(path_local, pp_ferg, cc, 111, test_data_lst, path_input_train, True)


def compute_dice(path_local, nb_img=1):

    res_concat = []
    for cc in ['t2', 't1', 't2s']:
        path_seg_out = path_local + 'output_svm_propseg_' + cc + '/'
        path_seg_out = path_local + 'output_svm_propseg_' + cc + '/'
        path_seg_out_propseg = path_local + 'output_propseg_' + cc + '/'
        path_data = path_local + 'input_nii_' + cc + '/'
        path_seg_out_cur = path_seg_out + str(nb_img) + '/'
        path_seg_out_propseg = path_local + 'output_propseg_' + cc + '/'

        fname_out_pd = path_seg_out + str(nb_img) + '.pkl'

        if not os.path.isfile(fname_out_pd):
            with open(path_local + 'test_valid_' + cc + '.pkl') as outfile:    
                train_test_pd = pickle.load(outfile)
                outfile.close()

            res_pd = train_test_pd[train_test_pd.valid_test=='test'][['patho', 'resol', 'subj_name']]
            subj_name_lst = res_pd.subj_name.values.tolist()
            res_pd['contrast'] = [cc for i in range(len(subj_name_lst))]

            res_pd['dice_svm'] = [0.0 for i in range( len(subj_name_lst))]
            # res_pd[' '] = [' ' for i in range(len(subj_name_lst))]
            for file in os.listdir(path_seg_out_cur):
                if file.endswith('.nii.gz'):
                    file_src = path_seg_out_cur+file
                    file_dst = path_data + file
                    subj_id = file.split('_'+cc)[0]
                    file_dice = path_seg_out_cur+subj_id+'.txt'
                    if not os.path.isfile(file_dice):
                        os.system('sct_dice_coefficient -i ' + file_src + ' -d ' + file_dst + ' -o ' + file_dice)
                    text = open(file_dice, 'r').read()
                    print 'svm'
                    if len(text.split('= '))>1:
                        print float(text.split('= ')[1])
                        res_pd.loc[res_pd.subj_name==subj_id,'dice_svm'] = float(text.split('= ')[1])
                    else:
                        os.system('sct_register_multimodal -i ' + file_src + ' -d ' + file_dst + ' -identity 1 -ofolder ' + path_seg_out_cur)
                        file_src_reg = file_src.split('.nii.gz')[0] + '_src_reg.nii.gz'
                        os.system('sct_dice_coefficient -i ' + file_src_reg + ' -d ' + file_dst + ' -o ' + file_dice)
                        text = open(file_dice, 'r').read()
                        if len(text.split('= '))>1:
                            res_pd.loc[res_pd.subj_name==subj_id,'dice_svm'] = float(text.split('= ')[1])

            res_pd['dice_propseg'] = [0.0 for i in range(len(subj_name_lst))]
            for file in os.listdir(path_seg_out_propseg):
                if file.endswith('_seg.nii.gz'):
                    file_src = path_seg_out_propseg+file
                    file_dst = path_data + file
                    subj_id = file.split('_'+cc)[0]
                    file_dice = path_seg_out_propseg+subj_id+'.txt'
                    if not os.path.isfile(file_dice):
                        os.system('sct_dice_coefficient -i ' + file_src + ' -d ' + file_dst + ' -o ' + file_dice)
                    text = open(file_dice, 'r').read()
                    print 'propseg'
                    if len(text.split('= '))>1:
                        print float(text.split('= ')[1])
                        res_pd.loc[res_pd.subj_name==subj_id,'dice_propseg'] = float(text.split('= ')[1])
                    else:
                        os.system('sct_register_multimodal -i ' + file_src + ' -d ' + file_dst + ' -identity 1 -ofolder ' + path_seg_out_propseg)
                        file_src_reg = file_src.split('.nii.gz')[0] + '_src_reg.nii.gz'
                        os.system('sct_dice_coefficient -i ' + file_src_reg + ' -d ' + file_dst + ' -o ' + file_dice)
                        text = open(file_dice, 'r').read()
                        res_pd.loc[res_pd.subj_name==subj_id,'dice_svm'] = float(text.split('= ')[1])

            res_pd = res_pd[res_pd.dice_svm != 0.0]
            res_pd.to_pickle(fname_out_pd)

        else:
            with open(fname_out_pd) as outfile:    
                res_pd = pickle.load(outfile)
                outfile.close()

        res_concat.append(res_pd)

        stg_propseg = 'Mean = ' + str(round(np.mean(res_pd.dice_propseg.values.tolist()),2))
        stg_propseg += '\nStd = ' + str(round(np.std(res_pd.dice_propseg.values.tolist()),2))
        stg_propseg += '\nMedian = ' + str(round(np.median(res_pd.dice_propseg.values.tolist()),2))
        stg_svm = 'Mean = ' + str(round(np.mean(res_pd.dice_svm.values.tolist()),2))
        stg_svm += '\nStd = ' + str(round(np.std(res_pd.dice_svm.values.tolist()),2))
        stg_svm += '\nMedian = ' + str(round(np.median(res_pd.dice_svm.values.tolist()),2))
        stg_svm += '\nMin = ' + str(round(np.min(res_pd.dice_svm.values.tolist()),2))
        stg_svm += '\nttest = ' + str(ttest_ind(res_pd.dice_propseg.values.tolist(), 
                                        res_pd.dice_svm.values.tolist())[1])
        
        print '\n\n' + cc
        print '\nOptiC:'
        print stg_svm
        print '\nPropSeg:'
        print stg_propseg
        # print len(res_pd.dice_svm.values.tolist())
        # print res_pd[res_pd.dice_svm<0.50]


    # res_tot = pd.concat(res_concat)
    # print res_tot
    # stg_propseg = 'Mean = ' + str(round(np.mean(res_tot.dice_propseg.values.tolist()),2))
    # stg_propseg += '\nStd = ' + str(round(np.std(res_tot.dice_propseg.values.tolist()),2))
    # stg_propseg += '\nMedian = ' + str(round(np.median(res_tot.dice_propseg.values.tolist()),2))
    # stg_svm = 'Mean = ' + str(round(np.mean(res_tot.dice_svm.values.tolist()),2))
    # stg_svm += '\nStd = ' + str(round(np.std(res_tot.dice_svm.values.tolist()),2))
    # stg_svm += '\nMedian = ' + str(round(np.median(res_tot.dice_svm.values.tolist()),2))
    # stg_svm += '\nMin = ' + str(round(np.min(res_tot.dice_svm.values.tolist()),2))
    
    # print '\nOptiC:'
    # print stg_svm
    # print '\nPropSeg:'
    # print stg_propseg

    # stg_propseg = 'Mean = ' + str(round(np.mean(res_tot[res_tot.patho=='patient'].dice_propseg.values.tolist()),2))
    # stg_propseg += '\nStd = ' + str(round(np.std(res_tot[res_tot.patho=='patient'].dice_propseg.values.tolist()),2))
    # stg_propseg += '\nMedian = ' + str(round(np.median(res_tot[res_tot.patho=='patient'].dice_propseg.values.tolist()),2))
    # stg_svm = 'Mean = ' + str(round(np.mean(res_tot[res_tot.patho=='patient'].dice_svm.values.tolist()),2))
    # stg_svm += '\nStd = ' + str(round(np.std(res_tot[res_tot.patho=='patient'].dice_svm.values.tolist()),2))
    # stg_svm += '\nMedian = ' + str(round(np.median(res_tot[res_tot.patho=='patient'].dice_svm.values.tolist()),2))
    # stg_svm += '\nMin = ' + str(round(np.min(res_tot[res_tot.patho=='patient'].dice_svm.values.tolist()),2))
    
    # print '\nOptiC:'
    # print stg_svm
    # print '\nPropSeg:'
    # print stg_propseg

    # y_lim_min, y_lim_max = -0.01, 1.01
    # sns.set(style="whitegrid", palette="Set1", font_scale=1.3)
    # fig, axes = plt.subplots(1, 2, sharey='col', figsize=(24, 8))
    # fig.subplots_adjust(left=0.05, bottom=0.05)
    # order_lst=['t2', 't1', 't2s']

    # for ii, dd in enumerate(['dice_propseg', 'dice_svm']):
    #     if dd == 'dice_propseg':
    #         palette_violon = dict(t2='gold', t1='royalblue', t2s='mediumvioletred')
    #     else:
    #         palette_violon = dict(t2='khaki', t1='cornflowerblue', t2s='pink')
    #     a = plt.subplot(1, 2, ii+1)
    #     sns.violinplot(x='contrast', y=dd, data=res_tot, order=order_lst,
    #                           inner="quartile", cut=0, scale="count",
    #                           sharey=True,  palette=palette_violon)

    #     a_swarm = sns.swarmplot(x='contrast', y=dd, data=res_tot, 
    #                             order=order_lst, size=3,
    #                             color=(0.2,0.2,0.2))
    #     # a_swarm.legend_.remove()

    #     a.set_ylim([y_lim_min,y_lim_max])
    #     plt.yticks(size=30)
    #     a.set_ylabel('')    
    #     a.set_xlabel('')

    # plt.show()
    # fig.tight_layout()
    # fig.savefig(path_local + 'plot_comparison/propseg_dice.png')
    # plt.close()

def computation_time(path_local, cc):

    path_time = path_local + 'output_time_' + cc + '_11/'
    path_dim = path_time+'dim.pkl'

    if not os.path.isfile(path_dim):
        with open(path_local + 'dataset_lst_' + cc + '.pkl') as outfile:    
            subj_lst = pickle.load(outfile)
            outfile.close()

        dct_dim = {'id': [], 'nz': []}
        for ii in subj_lst:
            img = Image(path_local + 'input_nii_' + cc + '/' + ii.split('.img')[0] + '.nii.gz')
            dct_dim['id'].append(ii.split('.img')[0])
            dct_dim['nz'].append(img.dim[2])
            del img

        dim_pd = pd.DataFrame.from_dict(dct_dim)
        dim_pd.to_pickle(path_time+'dim.pkl')
    else:
        with open(path_dim) as outfile:    
            dim_pd = pickle.load(outfile)
            outfile.close()

    dct_dim = dim_pd.to_dict(orient='list')

    dct_tmp = {'nb_train': [], 'mean': [], 'std': []}
    for fold_nb in os.listdir(path_time):
        if os.path.isdir(path_time+fold_nb):
            dct_tmp['nb_train'].append(fold_nb.split('0_0')[1])
            mean_per_slice_lst = []
            for subj, nz in zip(dct_dim['id'], dct_dim['nz']):
                time_file = path_time+fold_nb+'/'+subj+'.txt'
                if os.path.isfile(time_file):
                    tps_img = float(open(time_file, 'r').read())
                    mean_per_slice_lst.append(tps_img/nz)
                    dct_tmp['mean'].append(np.mean(mean_per_slice_lst))
                    dct_tmp['std'].append(np.std(mean_per_slice_lst))

    print dct_tmp
    time_pd = pd.DataFrame.from_dict(dct_tmp)
    print time_pd
    time_pd.to_pickle(path_time+'time.pkl')

# ******************************************************************************************

def readCommand(  ):
    "Processes the command used to run from the command line"
    parser = argparse.ArgumentParser('Sdika Pipeline')
    parser.add_argument('-ofolder', '--output_folder', help='Output Folder', required = False)
    parser.add_argument('-c', '--contrast', help='Contrast of Interest', required = True)
    parser.add_argument('-n', '--nb_train_img', help='Nb Training Images', required = False)
    parser.add_argument('-s', '--step', help='Prepare (step=0) or Push (step=1) or Pull (step 2) or Compute metrics (step=3) or Display results (step=4)', 
                                        required = False)
    arguments = parser.parse_args()
    return arguments


USAGE_STRING = """
  USAGE:      python sct_sdika.py -ofolder '/Users/chgroc/data/data_sdika/' <options>
  EXAMPLES:   (1) python sct_sdika.py -ofolder '/Users/chgroc/data/data_sdika/' -c t2
                  -> Run Sdika Algorithm on T2w images dataset...
              (2) python sct_sdika.py -ofolder '/Users/chgroc/data/data_sdika/' -c t2 -n 3
                  -> ...Using 3 training images...
              (3) python sct_sdika.py -ofolder '/Users/chgroc/data/data_sdika/' -c t2 -n 3 -s 1
                  -> ...s=0 >> Prepare dataset
                  -> ...s=1 >> Push data to Ferguson
                  -> ...s=2 >> Pull data from Ferguson
                  -> ...s=3 >> Evaluate Sdika algo by computing metrics
                  -> ...s=4 >> Display results
                 """

if __name__ == '__main__':

    # Read input
    parse_arg = readCommand()

    if not parse_arg.output_folder:
        print USAGE_STRING
    else:
        path_local_sdika = parse_arg.output_folder
        create_folders_local([path_local_sdika])

        # Extract config
        # with open(path_local_sdika + 'config.pkl') as outfile:    
        #     config_file = pickle.load(outfile)
        #     outfile.close()
        # fname_local_script = config_file['fname_local_script']
        path_ferguson = '/home/neuropoly/code/spine-ms/'
        path_sct_testing_large = '/Volumes/Public_JCA/sct_testing/large/'

        # Format of parser arguments
        contrast_of_interest = str(parse_arg.contrast)

        if not parse_arg.step:
            step = 0
        else:
            step = int(parse_arg.step)         

        # Panda DATASET
        if not step:
            panda_dataset(path_local_sdika, contrast_of_interest, path_sct_testing_large)
            prepare_dataset(path_local_sdika, contrast_of_interest, path_sct_testing_large)


        # if not step:
        #     # if not os.path.isfile(path_local_sdika+'resol_dct_'+contrast_of_interest+'.pkl'):
        #     partition_resol(path_local_sdika, contrast_of_interest)

        #     # Prepare [contrast] data
        #     # prepare_dataset(path_local_sdika, [contrast_of_interest], path_sct_testing_large)
            
        #     # Send Script to Ferguson Station
        #     # os.system('scp ' + fname_local_script + ' ferguson:' + '/home/neuropoly/code/spine-ms/')

        # elif step == 1:
        #     panda_dataset(path_local_sdika, contrast_of_interest)
        #     path_local_train_cur, valid_data_lst = prepare_train(path_local_sdika, '/home/neuropoly/code/spine-ms/', 
        #                                             contrast_of_interest, nb_train_img)
        #     # Send Data to Ferguson station
        #     send_data2ferguson(path_local_sdika, '/home/neuropoly/code/spine-ms/', contrast_of_interest, 
        #                         nb_train_img, valid_data_lst, path_local_train_cur)

        # elif step == 2:
        #     # Pull Results from ferguson
        #     pull_img_convert_nii_remove_img(path_local_sdika, path_ferguson, contrast_of_interest, nb_train_img)

        # elif step == 3:
        #     # Compute metrics / Evaluate performance of Sdika algorithm
        #     compute_dataset_stats(path_local_sdika, contrast_of_interest, nb_train_img)

        # elif step == 4:
        #     panda_trainer(path_local_sdika, contrast_of_interest)
        #     test_trainers_best(path_local_sdika, contrast_of_interest, 'mse', path_ferguson)

        # elif step == 5:
        #     # Pull Testing Results from ferguson
        #     pull_img_convert_nii_remove_img(path_local_sdika, path_ferguson, contrast_of_interest, 11)
        
        # elif step == 6:
        #     # Compute metrics / Evaluate performance of Sdika algorithm
        #     compute_dataset_stats(path_local_sdika, contrast_of_interest, 11)
        
        # elif step == 7:
        #     clf_lst = ['Hough', 'OptiC']
        #     nbimg_cc_dct = {'t2': 1, 't1': 1, 't2s': 1}
        #     # plot_comparison_clf(path_local_sdika, clf_lst, nbimg_cc_dct, '11')
        #     plot_comparison_clf_patho(path_local_sdika, clf_lst, nbimg_cc_dct, '11')

        # elif step == 8:
        #     prepare_svmhog(path_local_sdika, contrast_of_interest, '/home/neuropoly/code/spine-ms/', nb_train_img)

        # elif step == 9:
        #     create_folders_local([path_local_sdika+'output_img_'+contrast_of_interest+'_111/', 
        #                             path_local_sdika+'output_nii_'+contrast_of_interest+'_111/'])
        #     pull_img_convert_nii_remove_img(path_local_sdika, '/home/neuropoly/code/spine-ms/', 
        #                                         contrast_of_interest, 111)

        # elif step == 10:
        #     compute_dataset_stats(path_local_sdika, contrast_of_interest, 111)

        # elif step == 11:
        #     panda_trainer(path_local_sdika, contrast_of_interest)
        #     prepare_svmhog_test(path_local_sdika, contrast_of_interest, '/home/neuropoly/code/spine-ms/', 'mse')

        # elif step == 12:
        #     create_folders_local([path_local_sdika+'output_img_'+contrast_of_interest+'_1111/', 
        #         path_local_sdika+'output_nii_'+contrast_of_interest+'_1111/'])
        #     pull_img_convert_nii_remove_img(path_local_sdika, '/home/neuropoly/code/spine-ms/', 
        #                             contrast_of_interest, 1111)
        
        # elif step == 13:
        #     compute_dataset_stats(path_local_sdika, contrast_of_interest, 1111)
        
        # elif step == 14:
        #     clf_lst = ['SVM', 'OptiC']
        #     nbimg_cc_dct = {'t2': 1, 't1': 1, 't2s': 1}
        #     plot_comparison_clf(path_local_sdika, clf_lst, nbimg_cc_dct, '11')
        #     # plot_comparison_clf_patho(path_local_sdika, clf_lst, nbimg_cc_dct, '11')

        # elif step == 15:
        #     compute_dice(path_local_sdika)
        
        # elif step == 16:
        #     computation_time(path_local_sdika, contrast_of_interest)