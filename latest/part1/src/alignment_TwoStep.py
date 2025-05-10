''' Alignment '''
import os
import argparse
import math
import concurrent.futures
import subprocess
import nibabel as nib
import numpy as np
from numpy import zeros

from helper_functions import timeit_decorator,get_parent_path, create_folder

parser = argparse.ArgumentParser('=== Fetal alignment script for fetal pipeline ===')

parser.add_argument('-i','--input','--input_fol',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input folder name')

# Arguments from parser place into variable args
args = parser.parse_args()
input_fol = args.inp

##Moving recon.nii to recon_segmentation folder
if not os.path.exists("{0}/recon_segmentation".format(input_fol)):
    os.system("mkdir {0}/recon_segmentation".format(input_fol))
if os.path.exists("{0}/recon.nii".format(input_fol)):
    os.system("mv {0}/recon.nii {0}/recon_segmentation/".format(input_fol))

##Run initial alignment
os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/alignment.py -i {os.path.join(input_fol,"recon_segmentation","recon.nii")}')

##Perform initial Post NUC
os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/init_PostNUC.py --input_file {0}/recon_segmentation/recon_to31.nii --output_file {0}/recon_segmentation/recon_to31_nuc.nii".format(input_fol))

##Run initial segmentation with 4-label CP model
os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/segmentation_4.py --input {0}/recon_segmentation/recon_to31_nuc.nii --output_fol {0}/recon_segmentation".format(input_fol))

##Mask out brain using initial segmentation
os.system("mri_mask {0}/recon_segmentation/recon_to31_nuc.nii {0}/recon_segmentation/recon_to31_nuc_deep_agg.nii.gz {0}/recon_segmentation/recon_to31init_nuc_mask.nii".format(input_fol))

os.system("mv {0}/recon_segmentation/recon_to31_nuc.nii {0}/recon_segmentation/recon_to31init_nuc.nii".format(input_fol))
os.system("mv {0}/recon_segmentation/alignment_temp/recon_to31.xfm {0}/recon_segmentation/recon_to31init.xfm".format(input_fol))
    
##Perform second alignment
# Original version
#os.system("python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_codes/alignment_junshen_init_seg.py {0}/recon_segmentation".format(input_fol))

# Parallel Computing version
os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/alignment_junshen_init_seg_par.py {0}/recon_segmentation".format(input_fol))
