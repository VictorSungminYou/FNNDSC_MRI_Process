import nibabel as nib
import numpy as np
import sys
import os, argparse

parser = argparse.ArgumentParser('   ==========   Cortical surface extraction   ==========   ')
parser.add_argument('--iSEGM', action ='store',dest='iSEGM',type=str, required=True, help='Path to the SP segmentation')
parser.add_argument('--oSEGM', action ='store',dest='oSEGM',type=str, required=True, help='Path to the CP-like segmentation')

args = parser.parse_args()
inVol = nib.load(args.iSEGM)
ar = np.round(inVol.get_fdata()).astype(int)

## relabel SP to WM 
ar[ar == 5] = 161
ar[ar == 4] = 160
new_img = nib.Nifti1Image(ar, inVol.affine, inVol.header)
nib.save(new_img, args.oSEGM)
os.system('nii2mnc '+args.oSEGM[:-4]+' '+args.oSEGM[:-4]+'.mnc')
