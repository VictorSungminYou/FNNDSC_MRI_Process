''' Segmentation '''
# From auto_segmentation_v2.4_high.py
# Melquisideth Lagunas Barroso

import os
import argparse
import numpy
import nibabel as nib

def create_folder(folder):
    ''' Define a function to create a missing folder '''
    if not os.path.exists(folder):
        os.mkdir(folder)

def get_parent_path(dir_path):
    ''' Get the parent directory path '''
    return os.path.abspath(os.path.join(dir_path, os.pardir))

def superimpose_segmentations(target_filename, source_filename, output_filename, source_label=18):
    # Load NIfTI files
    target_img = nib.load(target_filename)
    source_img = nib.load(source_filename)

    # Get data from NIfTI files
    A = target_img.get_fdata()
    B = source_img.get_fdata()

    # Make sure A and B have the same shape
    if A.shape != B.shape:
        raise ValueError("Arrays A and B must have the same shape")

    # Create a mask where B's elements have a value of 18
    mask = (B == source_label)

    # Superimpose B over A where B has a value of 18
    A[mask] = B[mask]

    # Create a new NIfTI image from the modified data
    result_img = nib.Nifti1Image(A, target_img.affine, target_img.header)

    # Save the result as a new NIfTI file
    nib.save(result_img, output_filename)


parser = argparse.ArgumentParser('=== Fetal segmentation script ===')

parser.add_argument('-i','--input','--input_MR',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input MR')

parser.add_argument('--output_folder',
                    action = 'store',
                    dest = 'output_fol',
                    type=str,
                    default='recon_segmentation',
                    help = 'folder name for the segmentation (default=recon_segmentation)')

# Arguments from parser place into variable args
args = parser.parse_args()

#Variables extracted from arguments
input_MR = args.inp
MRI_file = os.path.basename(input_MR)
parent_fol = get_parent_path(input_MR)
grandparent_fol = get_parent_path(parent_fol)
# output_loc = os.path.abspath(args.output_fol)

print("[Info] Running CP segmentation")

print('== Starting Segmentation ==')
os.system('singularity run --no-home -B ' + parent_fol
          + ':/data --nv /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/fetal_cp_seg_0.5.sif '
          + MRI_file + ' . 0')
os.system("mv {0}/recon_to31_nuc_deep_agg.nii.gz {0}/{1}".format(parent_fol, "segmentation_to31_label4.nii.gz"))

os.system('singularity run --no-home -B ' + parent_fol
          + ':/data --nv /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/fetal_CP_CSF5.sif '
          + MRI_file + ' . 0')
os.system("mv {0}/recon_to31_nuc_deep_agg.nii.gz {0}/{1}".format(parent_fol, "segmentation_to31_label5.nii.gz"))

target_filename = "{}/segmentation_to31_label4.nii.gz".format(parent_fol)
source_filename = "{}/segmentation_to31_label5.nii.gz".format(parent_fol)
output_filename = "{}/segmentation_to31_5over4.nii.gz".format(parent_fol)
print('== Segmentation Done ==')

print('== Merging CSF from 5 label model over 4 label model output ==')
superimpose_segmentations(target_filename, source_filename, output_filename)
print('== Superimposing Done ==')

# if output_loc:
#     create_folder(os.path.join(grandparent_fol, output_loc))
#     os.system('mv ' +parent_fol+'/recon_to31_nuc_deep_agg.nii.gz '+output_loc+'/')
#     os.system('mv ' +parent_fol+'/recon_to31_nuc_deep_agg_verify.png '+output_loc+'/')
#     os.system('cp ' +parent_fol+'/recon_to31_nuc.nii '+output_loc+'/')
