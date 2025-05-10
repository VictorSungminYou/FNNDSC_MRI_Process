''' Non uniform correction 

input: brain folder

output: nuc folder


'''
import os
import glob
import argparse
import numpy as np
from tqdm import tqdm
from helper_functions import create_folder

parser = argparse.ArgumentParser(' === Fetal nuc script for fetal pipeline ===')

parser.add_argument('-i','--input', '--input_folder',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input folder name')

parser.add_argument('-brainF', '--brain_folder',
                    action='store',
                    dest='brain',
                    type=str,
                    default='brain',
                    help='Folder where .brain files are located')

parser.add_argument('-nucF', '--nuc_folder',
                    action='store',
                    dest='nuc',
                    type=str,
                    default='nuc',
                    help='Folder where nuc files will be stored (default=nuc)')


args = parser.parse_args()

input_fol = args.inp
brain_fol = args.brain
nuc_fol = args.nuc

#Checking for NUC folder (create if doesn't exist)
nuc_folder = os.path.join(input_fol, nuc_fol)
create_folder(nuc_folder)


#img_list = np.asarray(sorted(glob.glob(os.path.join(os.getcwd(), input_fol, '*.nii'))))
img_list = np.asarray(sorted(glob.glob(os.path.join(input_fol, brain_fol, '*.nii'))))

COW_TEXT = "fet_nuc_new.py \n -Starting Non-Uniformity Correction ..."
os.system(f'cowsay -c tux -t "{COW_TEXT}"')

# Loop over images with a progress bar
for img_path in tqdm(img_list, desc='Correcting Bias Fields'):

    os.system('~/arch/Linux64/packages/ANTs/current/bin/N4BiasFieldCorrection -d 3 -o '
              + img_path.replace('/' + brain_fol + '/','/' + nuc_fol + '/') + ' -i ' + img_path)


print(' === NUC FINISHED === ')
