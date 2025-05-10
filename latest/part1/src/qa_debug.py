''' Quality assessment '''
import os
import argparse
from helper_functions import create_folder,get_parent_path, verify
import csv
import shutil
import nibabel as nib
import glob
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(' === Fetal QA script for fetal pipeline === ')

parser.add_argument('-i','--input','--input_folder',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input folder name')

parser.add_argument('-output_file', '--output_file',
                    action='store',
                    dest='out_file',
                    default='quality_assessment.csv',
                    type=str,
                    help='Output filename')

parser.add_argument('-output_loc', '--output_path',
                    action='store',
                    dest='out_loc',
                    default=False,
                    type=str,
                    help='Output file location')

args = parser.parse_args()

input_fol = args.inp
out_loc = args.out_loc
out_file = args.out_file
parent_fol = get_parent_path(input_fol)

create_folder(out_loc)

COW_TEXT = "[Info] Starting Quality Assessment ..."

# Updated QA model
os.system('singularity run --no-home -B ./'+input_fol+':/'+input_fol
          +' --nv /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/fetal_brain_QA.sif /'
          +input_fol+' /'+input_fol+' '+out_file+' -1')

# Old QA model
# os.system('singularity exec --no-home docker://fnndsc/pl-fetal-brain-assessment:1.3.0 fetal_brain_assessment ./'+input_fol+'/nuc/ ./'+input_fol+'/;')

qa_dir = os.path.join(input_fol, out_file) #Path for Quality Assessment file
threshold = 0.4
Best_list = []

with open(qa_dir, 'r',encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        score = float(row["quality"]) #Reading QC score and cast it to float
        if score >= threshold:
            Best_list.append(row)

Best_list_sorted = sorted(Best_list, key=lambda row: row['quality'], reverse=True)
Best_image_filename = [row['filename'][1:] for row in Best_list_sorted]

dest_dir = '{}/Best_Images_crop'.format(input_fol)
os.makedirs(dest_dir, exist_ok=True)

print(Best_image_filename)

for src in Best_image_filename:
    if os.path.exists(src):
        src_basename = os.path.basename(src)
        dest_path = os.path.join(dest_dir, src_basename)
        
        if os.path.isdir(src):
            # Copy directory recursively
            shutil.copytree(src, dest_path, dirs_exist_ok=True)
        else:
            # Copy file
            shutil.copy2(src, dest_path)

verify(dest_dir)

if out_loc:
    os.system('mv ' +input_fol+'/'+out_file+' '+ out_loc+'/')
else:
    os.system('mv ' +input_fol+'/'+out_file+' '+ parent_fol+'/')


print(' === QA FINISHED === ')
