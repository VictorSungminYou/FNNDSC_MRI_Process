####!/usr/bin/python
import nibabel as nib
import numpy as np
import sys
import os
from scipy.ndimage import binary_erosion

LH = sys.argv[1]
RH = sys.argv[2]
out_LH = sys.argv[3]
out_RH = sys.argv[4]

for f in [out_LH, out_RH]:
	if os.path.isfile(f):
		os.system('rm '+f)

vol_LH = nib.load(LH)
vol_LH_ar = np.round(vol_LH.get_fdata()).astype(int)
vol_RH = nib.load(RH)
vol_RH_ar = np.round(nib.load(RH).get_fdata()).astype(int)

## LH 
lh = vol_RH_ar.copy()
lh[vol_RH_ar == 1] = 0
lh[vol_LH_ar != 0] = vol_LH_ar[vol_LH_ar != 0]

new_img = nib.Nifti1Image(lh, vol_LH.affine, vol_LH.header)
nib.save(new_img, out_LH)
os.system('nii2mnc '+out_LH[:-4]+' '+out_LH[:-4]+'.mnc')

## RH 
rh = vol_LH_ar.copy()
rh[vol_LH_ar == 1] = 0
rh[vol_RH_ar != 0] = vol_RH_ar[vol_RH_ar != 0]

new_img = nib.Nifti1Image(vol_RH_ar, vol_RH.affine, vol_RH.header)
nib.save(new_img, out_RH)
os.system('nii2mnc '+out_RH[:-4]+' '+out_RH[:-4]+'.mnc')


'''
## for left side
vol_LH = nib.load(LH)
vol_LH_ar = vol_LH.get_fdata()
vol_RH = nib.load(RH)
vol_RH_ar = nib.load(RH).get_fdata()


out_lh_ar = vol_RH_ar.copy()
out_lh_ar[out_lh_ar < 1.5] = 0.
#out_lh_ar[vol_RH_ar > 1] = vol_RH_ar[vol_RH_ar > 1]
out_lh_ar[vol_LH_ar > 0.5] = vol_LH_ar[vol_LH_ar > 0.5]

# try to erode the WM
#errosion_mask = np.zeros_like(vol_LH_ar)
#errosion_mask[out_lh_ar == 3] = 1
#errosion_mask_new=binary_erosion(errosion_mask)
#final_mask = (errosion_mask.astype(int) - errosion_mask_new.astype(int)).astype(int)
#out_lh_ar[final_mask == 1] = 2

new_img = nib.Nifti1Image(out_lh_ar.astype(np.float32), vol_LH.affine, vol_LH.header)
new_img.set_data_dtype(np.float32)
nib.save(new_img, out_LH)
## convert to .mnc
os.system('nii2mnc '+out_LH[:-4]+' '+out_LH[:-4]+'.mnc')

#out_rh_ar = np.zeros_like(vol_RH_ar)
out_rh_ar = vol_LH_ar.copy()
out_rh_ar[out_rh_ar < 1.5] = 0.
out_rh_ar[vol_RH_ar > 0.5] = vol_RH_ar[vol_RH_ar > 0.5]

# try to erode the WM
#errosion_mask = np.zeros_like(vol_RH_ar)
#errosion_mask[out_rh_ar == 2] = 1
#errosion_mask_new=binary_erosion(errosion_mask)
#final_mask = (errosion_mask.astype(int) - errosion_mask_new.astype(int)).astype(int)
#out_rh_ar[final_mask == 1] = 2


new_img = nib.Nifti1Image(out_rh_ar.astype(np.float32), vol_RH.affine, vol_RH.header)
new_img.set_data_dtype(np.float32)
nib.save(new_img, out_RH)
## convert to .mnc
os.system('nii2mnc '+out_RH[:-4]+' '+out_RH[:-4]+'.mnc')
'''




