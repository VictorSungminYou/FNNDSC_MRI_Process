''' Creates a mask of the brain from the raw files 

input: A directory with all the mri scans 

output: 3 sub directories in the current directory: Raw, Masks, Brain, 
all raw images are moved to the raw folder

note: The input directory cannot be named "Raw"


'''
import os
import glob
import argparse
import shutil
import numpy as np
import nibabel as nib

from helper_functions import timeit_decorator, create_folder

parser = argparse.ArgumentParser(' === Fetal masking script for fetal pipeline === ')

parser.add_argument('-i','--input','--input_folder',
                     action='store',
                     dest='inp',
                     type=str,
                     required=True,
                     help='Input MR file name (\'.nii or .nii.gz\') or folder name')

parser.add_argument('--raw_folder',
                    action='store',
                    dest='raw',
                    type=str,
                    default='raw',
                    help='Folder to store raw MRI files (default=raw)')

parser.add_argument('--masks_folder',
                    action='store',
                    dest='mask',
                    type=str,
                    default='masks',
                    help='Folder to store the masks created (default=masks)')

parser.add_argument('--brains_folder',
                    action='store',
                    dest='brain',
                    type=str,
                    default='brain',
                    help='Folder to store the brain extractions (default=brain)')

parser.add_argument('--remask', 
                    action='store_true', 
                    help='Option for remasking. If given, skip brain masking and apply masking using masks at mask_folder')

parser.add_argument('--verbose',
                    action='store',
                    dest='ver',
                    type=int,
                    default=0,
                    help='Output path')


args = parser.parse_args()

input_fol = args.inp
raw_fol = args.raw
mask_fol = args.mask
brain_fol = args.brain
remask_flag = args.remask
VERB_TEXT = '' if args.ver else '>/dev/null 2>&1'

print("input folder ", input_fol)

@timeit_decorator
def singularity():

    # Updated Mask - Melqui
    # os.system('singularity run --no-home -B ./' + input_fol + '/' + raw_fol
    #         + ':/data /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/brain_mask.sif /data; '
    #         + VERB_TEXT)

    # Old mask - Sofia
    # os.system('singularity run --no-home -B ./' + input_fol + '/' + raw_fol
    #         + ':/data /neuro/labs/grantlab/research/MRI_processing/sofia.urosa/mask_project/singularity/brain_masking.sif /data;')

    # Old old mask - Hyukjin
    os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brain_mask2 --target-dir ./'+input_fol+'/' + raw_fol)

    os.system('mv ' + input_fol + '/' + raw_fol + '/*mask.nii ' + input_fol + '/' + mask_fol)

# Binalize mask
@timeit_decorator
def Binalize_mask():
    mask_list = glob.glob(input_fol+'/'+mask_fol+'/*mask.nii')
    for file in mask_list:
        if not file.endswith('~'):
            #Apply fslmaths for the binarization of the file
            #print(f"Binarizing mask: {file}")
            os.system('fslmaths ' + file + ' -thr ' +'0.001 ' + '-bin ' + file)

            #We remove the original file
            os.remove(file)

            #Decompress the new binarized file
            gzip_file = file + '.gz'
            #print(f"Unizpping mask: {gzip_file}")
            if os.path.exists(gzip_file):
                os.system('gunzip ' + gzip_file)

@timeit_decorator
def mask_cropping():
    for i,img in enumerate(img_list):
        vol = nib.load(img)
        vol_data = vol.get_fdata()
        if np.max(vol_data)>0.01:
            os.system('mri_mask ' + img_list[i].replace(mask_fol + '/',raw_fol + '/')
                    .replace('_mask.nii','.nii') + ' ' + img_list[i] + '  '
                    + img_list[i].replace(mask_fol + '/',brain_fol + '/')
                    .replace('_mask.nii','_brain.nii'))


#Move raw scans into 'raw' folder from data dir
if not os.path.exists(raw_fol):
    #Check for Raw folder (create if doesn't exist and move nii files inside)

    raw_folder = os.path.join(input_fol, raw_fol)
    create_folder(raw_folder)
    for nii_file in glob.glob(input_fol+'/*.nii'):
        shutil.move(nii_file, raw_folder)

# Checking for Masks folder (create if doesn't exist)
masks_folder = os.path.join(input_fol, mask_fol)
create_folder(masks_folder)

# Checking for Brain folder (create if doesn't exist)
brain_folder = os.path.join(input_fol, brain_fol)
create_folder(brain_folder)

if remask_flag:
    print("[Info] Skip mask generation and perform Re-Masking ...")
    img_list= np.asarray(sorted(glob.glob(input_fol+'/'+mask_fol+'/*mask.nii')))
    Binalize_mask()
    mask_cropping()

else:
    # # # # # # # # # # #
    # Automatic masking #
    # # # # # # # # # # #
    COW_TEXT = "fet_mask_new.py \n -Starting Masking ..."
    os.system(f'cowsay -c tux -t "{COW_TEXT}"')
    singularity()

    # # # # # # # # # # # # # #
    # Mask cropping --> brain/#
    # # # # # # # # # # # # # #
    img_list= np.asarray(sorted(glob.glob(input_fol+'/'+mask_fol+'/*mask.nii')))
    Binalize_mask()
    mask_cropping()

    print(" == Masking done == ")
