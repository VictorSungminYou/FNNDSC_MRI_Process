#!/usr/bin/env python3

##folder: /tasmiah
#v3.3 - changed volume measures lines, so it is no longer echoing fslstats

#surface extraction after segto31_final.nii created manually and recon_#/* (containing seg_to31_final.nii) copied to '+input_fol+'

import os
import sys
import math
import argparse
import nibabel as nib
import numpy as np

#volume measures		
def vol_meas(input_segmentation, recon_native_xfm):		
	# seg_final= input_fol+'/recon_segmentation/segmentation_to31_final.nii'
	seg_final= input_segmentation
	base_path = os.path.dirname(input_segmentation)

	final_nii = nib.load(seg_final)
	img_data = final_nii.get_fdata()

	vox_inRange_1 = ((img_data > 159) & (img_data < 161)).sum()
	vox_inRange_2 = ((img_data > 160) & (img_data < 162)).sum()
	vox_inRange_3 = ((img_data > 41) & (img_data < 43)).sum()
	vox_inRange_4 = ((img_data > 0) & (img_data < 2)).sum()

	print("num voxels:", vox_inRange_1, vox_inRange_2, vox_inRange_3, vox_inRange_4)

	voxel_sizes = np.abs(final_nii.header.get_zooms())
	print("vox size:", voxel_sizes)

	vol1 = vox_inRange_1 * np.prod(voxel_sizes)
	vol2 = vox_inRange_2 * np.prod(voxel_sizes)
	vol3 = vox_inRange_3 * np.prod(voxel_sizes)
	vol4 = vox_inRange_4 * np.prod(voxel_sizes)
	
	# xfm_path = input_fol+'/recon_segmentation/recon_native.xfm'
	xfm_path = recon_native_xfm
	os.system('xfm2param {} | grep scale | cut -d" " -f11 > {}/temp/temp_scale.txt;'.format(xfm_path, base_path))
	os.system('xfm2param {} | grep scale | cut -d" " -f15 >> {}/temp/temp_scale.txt;'.format(xfm_path, base_path))
	os.system('xfm2param {} | grep scale | cut -d" " -f19 >> {}/temp/temp_scale.txt;'.format(xfm_path, base_path))
	
	with open('{}/temp/temp_scale.txt'.format(base_path)) as temp:
		scale_temp = [0,0,0]
		scale_temp=temp.readlines()

	scale_av = float(scale_temp[0]) * float(scale_temp[1]) * float(scale_temp[2])
	print(scale_av)

	v1xScale = (vol1 * scale_av)
	v2xScale = (vol2 * scale_av)
	v3xScale = (vol3 * scale_av)
	v4xScale = (vol4 * scale_av)

	with open('{}/Volume_measures.txt'.format(base_path), "w") as file:
		file.write('{:.3f} {:.3f} {:.3f} {:.3f}\n'.format(v1xScale, v2xScale, v3xScale, v4xScale))

def main(args):
	input_segmentation = args.input_segmentation
	recon_native_xfm = args.recon_native_xfm
	os.makedirs('{}/temp'.format(os.path.dirname(input_segmentation)), exist_ok=True)
	vol_meas(input_segmentation, recon_native_xfm)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input_segmentation', required=True, help='path to the MRI volme data')
	parser.add_argument('--recon_native_xfm', nargs='?', required=True, help='path to the recon_native.xfm')

	args = parser.parse_args()
	main(args)
