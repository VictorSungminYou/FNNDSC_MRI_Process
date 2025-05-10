#!/bin/env python3
import os
import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse

def main(args):

	dest_fol = args.data_dir
	input_seg = args.input_seg
	s_left = args.sl
	s_right = args.sr
	lz = args.lz
	
	os.system('mkdir -p '+dest_fol)
	
	if not os.path.exists(input_seg):
		print('Input segmentation is not exist')
		exit()
	    
	if not os.path.exists(dest_fol):
		print('Output folder is created')
		exit()

	if not (os.path.exists(s_left) and os.path.exists(s_right)):
		print('Input surface is not exist')
		exit()
	
	print('\n\n')
	print('\t\t Initial segmentation input: \t\t\t\t'+input_seg)
	print('\t\t Output folder: \t\t\t\t'+dest_fol)
	print('\t\t Skeletonization parameter (LZ): \t\t\t'+lz)
	print('\t\t Number of iteration: \t\t\t'+str(args.iteration))
	
	for n_iter in range(0,args.iteration + 1):
		print('Iteration : '+str(n_iter))
		CSF_skel(input_seg, dest_fol, lz, n_iter)
		input_seg=dest_fol+'/temp_seg_'+str(n_iter)+'.nii'
	print('Done')
	print('Creating CLASP segmentation files')
	CLASP_seg(input_seg, dest_fol, s_left, s_right)
	print('Done')
	
def CSF_skel(input_seg, dest_fol, lz, n_iter):
	
	
	
	###############################
	# Labels:
	# 1: Right-Cerebral-Exterior
	# 42: Left-Cerebral-Exterior
	# 160: Left-Cerebral-WM
	# 161: Right-Cerebral-WM
	###############################
	
	# Segment and Join Cerebral Exterior Labels 1 & 42.
	seg = nib.load(input_seg)
	seg_data = seg.get_fdata()
	
	hdr = seg.header
	hdr.set_data_dtype(np.int16)
	
	cerebral_ext_left = np.zeros(np.shape(seg_data))
	cerebral_ext_right = np.zeros(np.shape(seg_data))
	
	cerebral_ext_left[np.where(np.round(seg_data)==42)]=1
	cerebral_ext_right[np.where(np.round(seg_data)==1)]=1
	
	# Dilation Cerebral Exterior
	cerebral_ext_d_left=ndimage.binary_dilation(cerebral_ext_left)
	cerebral_ext_d_right=ndimage.binary_dilation(cerebral_ext_right)
	
	# Segment and Join Cerebral Interior Labels 160 & 161.
	cerebral_int_left = np.zeros(np.shape(seg_data))
	cerebral_int_right = np.zeros(np.shape(seg_data))
	
	cerebral_int_left[np.where(np.round(seg_data)==160)]=1
	cerebral_int_right[np.where(np.round(seg_data)==161)]=1
	
	# Binarize all segmentations 
	initial_segmentations_left = np.zeros(np.shape(seg_data))
	initial_segmentations_right = np.zeros(np.shape(seg_data))
	
	initial_segmentations_left[np.where((np.round(cerebral_int_left)==1) | (np.round(cerebral_ext_left)==1))]=1
	initial_segmentations_right[np.where((np.round(cerebral_int_right)==1) | (np.round(cerebral_ext_right)==1))]=1
	
	# Dilation Initial Segmentations
	initial_segmentations_d_left=ndimage.binary_dilation(initial_segmentations_left)
	initial_segmentations_d_right=ndimage.binary_dilation(initial_segmentations_right)
	
	#############################################################
	###################### START SKELETON #######################
	#############################################################

	# GM External Boundary - 1th voxel apart.
	gm_ext_left = np.zeros(np.shape(seg_data))
	gm_ext_right = np.zeros(np.shape(seg_data))
	
	gm_ext_left[np.where((np.round(initial_segmentations_d_left)==1) & (np.round(initial_segmentations_left)==0))]=1
	gm_ext_right[np.where((np.round(initial_segmentations_d_right)==1) & (np.round(initial_segmentations_right)==0))]=1
	
	#############################################################
	# Join GM and WM
	wm_and_gm_left = np.zeros(np.shape(seg_data),dtype=np.int16)
	wm_and_gm_right = np.zeros(np.shape(seg_data),dtype=np.int16)
	
	wm_and_gm_left[np.where(np.round(cerebral_ext_left)>0)]=2
	wm_and_gm_left[np.where(np.round(cerebral_int_left)>0)]=3
	
	wm_and_gm_right[np.where(np.round(cerebral_ext_right)>0)]=2
	wm_and_gm_right[np.where(np.round(cerebral_int_right)>0)]=3
	
	new_img = nib.Nifti1Image(wm_and_gm_left, seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_left.nii')
	new_img = nib.Nifti1Image(wm_and_gm_right, seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_right.nii')
	
	#####################(GM -> Skeleton)########################################
	#### GM in Gray Scale. Prepare file.
	gm_grayscale_left = 11*np.ones(np.shape(seg_data),dtype=np.int16)
	gm_grayscale_right = 11*np.ones(np.shape(seg_data),dtype=np.int16)
	
	gm_grayscale_left[np.where(np.round(gm_ext_left)>0)]=255
	gm_grayscale_left[np.where(np.round(cerebral_ext_left)>0)]=255
	gm_grayscale_left[np.where(np.round(cerebral_int_left)>0)]=0
	
	gm_grayscale_right[np.where(np.round(gm_ext_right)>0)]=255
	gm_grayscale_right[np.where(np.round(cerebral_ext_right)>0)]=255
	gm_grayscale_right[np.where(np.round(cerebral_int_right)>0)]=0
	
	new_img = nib.Nifti1Image(gm_grayscale_left, seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_left.nii')
	new_img = nib.Nifti1Image(gm_grayscale_right, seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_right.nii')
	
	#### Skeleton
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_left.nii \
	    -so '+dest_fol+'/skeleton_1_left.nii \
	    -vo '+dest_fol+'/roots_1_left.nii \
	    -g '+dest_fol+'/wm_and_gm_left.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_right.nii \
	    -so '+dest_fol+'/skeleton_1_right.nii \
	    -vo '+dest_fol+'/roots_1_right.nii \
	    -g '+dest_fol+'/wm_and_gm_right.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	
	##################### Flip left-right ########################################
	new_img = nib.Nifti1Image(wm_and_gm_left[::-1,:,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_LR_left.nii')
	new_img = nib.Nifti1Image(wm_and_gm_right[::-1,:,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_LR_right.nii')
	
	new_img = nib.Nifti1Image(gm_grayscale_left[::-1,:,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_LR_left.nii')
	new_img = nib.Nifti1Image(gm_grayscale_right[::-1,:,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_LR_right.nii')
	
	#### Skeleton flip
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_LR_left.nii \
	    -so '+dest_fol+'/skeleton_2_left.nii \
	    -vo '+dest_fol+'/roots_2_left.nii \
	    -g '+dest_fol+'/wm_and_gm_LR_left.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_LR_right.nii \
	    -so '+dest_fol+'/skeleton_2_right.nii \
	    -vo '+dest_fol+'/roots_2_right.nii \
	    -g '+dest_fol+'/wm_and_gm_LR_right.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')

	##################### Flip A-P ########################################
	new_img = nib.Nifti1Image(wm_and_gm_left[:,::-1,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_AP_left.nii')
	new_img = nib.Nifti1Image(wm_and_gm_right[:,::-1,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_AP_right.nii')
	
	new_img = nib.Nifti1Image(gm_grayscale_left[:,::-1,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_AP_left.nii')
	new_img = nib.Nifti1Image(gm_grayscale_right[:,::-1,:], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_AP_right.nii')
	
	#### Skeleton flip
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_AP_left.nii \
	    -so '+dest_fol+'/skeleton_3_left.nii \
	    -vo '+dest_fol+'/roots_3_left.nii \
	    -g '+dest_fol+'/wm_and_gm_AP_left.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_AP_right.nii \
	    -so '+dest_fol+'/skeleton_3_right.nii \
	    -vo '+dest_fol+'/roots_3_right.nii \
	    -g '+dest_fol+'/wm_and_gm_AP_right.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	    
	##################### Flip S-I ########################################
	new_img = nib.Nifti1Image(wm_and_gm_left[:,:,::-1], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_SI_left.nii')
	new_img = nib.Nifti1Image(wm_and_gm_right[:,:,::-1], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/wm_and_gm_SI_right.nii')
	
	new_img = nib.Nifti1Image(gm_grayscale_left[:,:,::-1], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_SI_left.nii')
	new_img = nib.Nifti1Image(gm_grayscale_right[:,:,::-1], seg.affine, hdr)
	nib.save(new_img, dest_fol+'/gm_grayscale_SI_right.nii')
	
	#### Skeleton flip
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_SI_left.nii \
	    -so '+dest_fol+'/skeleton_4_left.nii \
	    -vo '+dest_fol+'/roots_4_left.nii \
	    -g '+dest_fol+'/wm_and_gm_SI_left.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/brainvisa/bin/VipSkeleton \
	    -i '+dest_fol+'/gm_grayscale_SI_right.nii \
	    -so '+dest_fol+'/skeleton_4_right.nii \
	    -vo '+dest_fol+'/roots_4_right.nii \
	    -g '+dest_fol+'/wm_and_gm_SI_right.nii \
	    -p c -wp 0 -lz '+lz+' -lu 10 -e 0.5 -mct 0 -gct -10')

	# Binarize Skeleton
	skeleton_1_left = nib.load(dest_fol+'/skeleton_1_left.nii')
	skeleton_1_left_data = skeleton_1_left.get_fdata()
	skeleton_1_right = nib.load(dest_fol+'/skeleton_1_right.nii')
	skeleton_1_right_data = skeleton_1_right.get_fdata()
	
	skeleton_1_left_data[np.where(np.round(skeleton_1_left_data)<=11.5)]=0
	skeleton_1_right_data[np.where(np.round(skeleton_1_right_data)<=11.5)]=0
	
	skeleton_2_left = nib.load(dest_fol+'/skeleton_2_left.nii')
	skeleton_2_left_data = skeleton_2_left.get_fdata()
	skeleton_2_right = nib.load(dest_fol+'/skeleton_2_right.nii')
	skeleton_2_right_data = skeleton_2_right.get_fdata()
	
	skeleton_2_left_data[np.where(np.round(skeleton_2_left_data)<=11.5)]=0
	skeleton_2_right_data[np.where(np.round(skeleton_2_right_data)<=11.5)]=0
	
	skeleton_3_left = nib.load(dest_fol+'/skeleton_3_left.nii')
	skeleton_3_left_data = skeleton_3_left.get_fdata()
	skeleton_3_right = nib.load(dest_fol+'/skeleton_3_right.nii')
	skeleton_3_right_data = skeleton_3_right.get_fdata()
	
	skeleton_3_left_data[np.where(np.round(skeleton_3_left_data)<=11.5)]=0
	skeleton_3_right_data[np.where(np.round(skeleton_3_right_data)<=11.5)]=0
	
	skeleton_4_left = nib.load(dest_fol+'/skeleton_4_left.nii')
	skeleton_4_left_data = skeleton_4_left.get_fdata()
	skeleton_4_right = nib.load(dest_fol+'/skeleton_4_right.nii')
	skeleton_4_right_data = skeleton_4_right.get_fdata()
	
	skeleton_4_left_data[np.where(np.round(skeleton_4_left_data)<=11.5)]=0
	skeleton_4_right_data[np.where(np.round(skeleton_4_right_data)<=11.5)]=0
	
	skeleton_left_data = np.zeros(np.shape(seg_data))
	skeleton_right_data = np.zeros(np.shape(seg_data))
	
	x, y, z = nib.aff2axcodes(skeleton_1_left.affine)

	if x == 'R':
		skeleton_left_data = skeleton_1_left_data[::-1,:,:] + skeleton_2_left_data + skeleton_3_left_data[::-1,::-1,:] + skeleton_4_left_data[::-1,:,::-1]
		skeleton_right_data = skeleton_1_right_data[::-1,:,:] + skeleton_2_right_data + skeleton_3_right_data[::-1,::-1,:]  + skeleton_4_right_data[::-1,:,::-1]
	else:
		skeleton_left_data = skeleton_1_left_data + skeleton_2_left_data[::-1,:,:] + skeleton_3_left_data[:,::-1,:] + skeleton_4_left_data[:,:,::-1]
		skeleton_right_data = skeleton_1_right_data + skeleton_2_right_data[::-1,:,:] + skeleton_3_right_data[:,::-1,:]  + skeleton_4_right_data[:,:,::-1]
	
	
	
	# Join Skeleton with GM external boundary.
	skeleton_output_left = np.zeros(np.shape(seg_data))
	skeleton_output_right = np.zeros(np.shape(seg_data))
	skeleton_output = np.zeros(np.shape(seg_data))
	
	skeleton_output_left[np.where(skeleton_left_data > 0)]=1
	skeleton_output_left[np.where(gm_ext_left > 0)]=1
	
	skeleton_output_right[np.where(skeleton_right_data > 0)]=1
	skeleton_output_right[np.where(gm_ext_right > 0)]=1
	
	skeleton_output[np.where(skeleton_output_left > 0)]=1
	skeleton_output[np.where(skeleton_output_right > 0)]=1
		
	new_img = nib.Nifti1Image(skeleton_output_left, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/skeleton_output_left.nii')
	new_img = nib.Nifti1Image(skeleton_output_right, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/skeleton_output_right.nii')
	new_img = nib.Nifti1Image(skeleton_output, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/skeleton_output_iter_'+str(n_iter)+'.nii')
	
	
	temp_seg = seg_data
	temp_seg[np.where((skeleton_output>0) & (seg_data<100))]=0
	
	new_img = nib.Nifti1Image(temp_seg, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/temp_seg_'+str(n_iter)+'.nii')
	
	acc_skel = np.zeros(np.shape(seg_data))
	for a in range(0,n_iter+1):
		temp_skel = nib.load(dest_fol+'/skeleton_output_iter_'+str(a)+'.nii')
		temp_skel_data = temp_skel.get_fdata()
		acc_skel = acc_skel + temp_skel_data
	
	new_img = nib.Nifti1Image(acc_skel, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/accumulated_skeleton.nii')

def CLASP_seg(input_seg, dest_fol, s_left, s_right):
	
	if os.path.exists(dest_fol+'/seg_temp.mnc'):
		print('file already exists - removing files')
		os.system('rm '+dest_fol+'/seg_temp.mnc')
		os.system('rm '+dest_fol+'/surf_mask_left.*')
		os.system('rm '+dest_fol+'/surf_mask_right.*')
		os.system('rm '+dest_fol+'/segmentation_left_CLASP.*')
		os.system('rm '+dest_fol+'/segmentation_right_CLASP.*')
	
	os.system('nii2mnc '+input_seg+' '+dest_fol+'/seg_temp.mnc')
	
	os.system('surface_mask '+dest_fol+'/seg_temp.mnc '+s_left+' '+dest_fol+'/surf_mask_left.mnc')
	os.system('surface_mask '+dest_fol+'/seg_temp.mnc '+s_right+' '+dest_fol+'/surf_mask_right.mnc')
	
	os.system('mnc2nii -float '+dest_fol+'/surf_mask_left.mnc '+dest_fol+'/surf_mask_left.nii')
	os.system('mnc2nii -float '+dest_fol+'/surf_mask_right.mnc '+dest_fol+'/surf_mask_right.nii')
	
	mask_left = nib.load(dest_fol+'/surf_mask_left.nii')
	mask_left_data = mask_left.get_fdata()
	
	mask_right = nib.load(dest_fol+'/surf_mask_right.nii')
	mask_right_data = mask_right.get_fdata()
	
	seg = nib.load(input_seg)
	seg_data = seg.get_fdata()
	
	new_seg = seg_data
	
	new_seg[np.where(np.round(mask_left_data[::-1,:,:])>0)]=160
	new_seg[np.where((np.round(mask_left_data[::-1,:,:])==0) & (np.round(seg_data)==160))]=42
	
	new_seg[np.where(np.round(mask_right_data[::-1,:,:])>0)]=161
	new_seg[np.where((np.round(mask_right_data[::-1,:,:])==0) & (np.round(seg_data)==161))]=1
	
	
	skeleton_output_left = nib.load(dest_fol+'/skeleton_output_left.nii')
	skeleton_output_left_data = skeleton_output_left.get_fdata()
	skeleton_output_right = nib.load(dest_fol+'/skeleton_output_right.nii')
	skeleton_output_right_data = skeleton_output_right.get_fdata()
	
	CLASP_left = np.zeros(np.shape(seg.get_fdata()))
	CLASP_right = np.zeros(np.shape(seg.get_fdata()))
	
	CLASP_left[np.where(np.round(new_seg) == 42)]=2
	CLASP_left[np.where(np.round(skeleton_output_left_data) == 1)]=1
	CLASP_left[np.where(np.round(new_seg) == 160)]=3
	
	CLASP_right[np.where(np.round(new_seg) == 1)]=2
	CLASP_right[np.where(np.round(skeleton_output_right_data) == 1)]=1
	CLASP_right[np.where(np.round(new_seg) == 161)]=3

	new_img = nib.Nifti1Image(CLASP_left, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/segmentation_left_CLASP.nii')
	new_img = nib.Nifti1Image(CLASP_right, seg.affine, seg.header)
	nib.save(new_img, dest_fol+'/segmentation_right_CLASP.nii')
	
	os.system('nii2mnc '+dest_fol+'/segmentation_left_CLASP.nii '+dest_fol+'/segmentation_left_CLASP.mnc')
	os.system('nii2mnc '+dest_fol+'/segmentation_right_CLASP.nii '+dest_fol+'/segmentation_right_CLASP.mnc')

if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Iterative skeletonization of CP   ==========   ')
	parser.add_argument('-dir', '--dir',action='store',dest='data_dir',type=str, required=True, help='Path for skeleton output')
	parser.add_argument('-i', '--input_seg', action='store',dest='input_seg', type=str, required=True, help='Initial segmnetation')
	parser.add_argument('-lz', '--lz_value',action='store', dest='lz',type=str, default = '5', help='LZ value for skeletonization [default = 5]')
	parser.add_argument('-n', '--n_iteration',action='store', dest='iteration',type=int, default = 10, help='Number of iteration [default = 10]')
	parser.add_argument('-sl', '--surface_left',action='store',dest='sl', type=str, required=True, help='Left inner surface')
	parser.add_argument('-sr', '--surface_right',action='store',dest='sr', type=str, required=True, help='Right inner surface') 
	args = parser.parse_args()
	
	main(args)

