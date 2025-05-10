# From auto_segmentation_v2.4_high.py
# Melquisideth Lagunas Barroso

import os
import argparse

# Define a function to create a missing folder
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def get_parent_path(dir_path):
    return os.path.abspath(os.path.join(dir_path, os.pardir))

parser = argparse.ArgumentParser('   ==========   Fetal segmentation script for fetal pipeline   ==========   ')

parser.add_argument('--input',
                    action='store', 
                    dest='inp', 
                    type=str, 
                    required=True, 
                    help='input MR')

parser.add_argument('--output_fol',
                    action = 'store',
                    dest = 'output_fol',
                    type=str,
                    default='./recon_segmentation',
                    help = 'folder name for the segmentation (default=segmentation)')

# Arguments from parser place into variable args
args = parser.parse_args()

#Variables extracted from arguments
input_MR = args.inp
MRI_file = os.path.basename(input_MR)
parent_fol = get_parent_path(input_MR)
grandparent_fol = get_parent_path(parent_fol)
output_loc = os.path.abspath(args.output_fol)

print("[Info] Running CP segmentation")

print('== Starting Segmentation ==')
os.system('singularity run --no-home -B '+parent_fol+':/data --nv /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/fetal_cp_seg_0.5.sif '+MRI_file+' . 0')    
print('== Segmentation Done ==')


if output_loc:
    create_folder(os.path.join(grandparent_fol, output_loc))
    os.system('mv ' +parent_fol+'/recon_to31_nuc_deep_agg.nii.gz '+output_loc+'/')
    os.system('mv ' +parent_fol+'/recon_to31_nuc_deep_agg_verify.png '+output_loc+'/')
    os.system('cp ' +parent_fol+'/recon_to31_nuc.nii '+output_loc+'/')
