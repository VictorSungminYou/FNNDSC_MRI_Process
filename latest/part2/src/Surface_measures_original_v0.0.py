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

parser = argparse.ArgumentParser()

parser.add_argument('--input_fol',
    nargs='?',			
    required=True,
    help='path to the data directory')
parser.add_argument('-thk', '--thickness',action='store_true', help='only thickness')

#surface extraction
def transformation():		
	os.system('transform_objects '+input_fol+'/surfaces/lh.smoothwm.to31_81920.obj '+input_fol+'/recon_segmentation//recon_native.xfm '+input_fol+'/surfaces/lh.smoothwm.native_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/rh.smoothwm.to31_81920.obj '+input_fol+'/recon_segmentation//recon_native.xfm '+input_fol+'/surfaces/rh.smoothwm.native_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/lh.smoothwm.to31_81920.obj /neuro/labs/grantlab/research/HyukJin_MRI/Fetal_template/xfm/template-31toMNI.xfm '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/rh.smoothwm.to31_81920.obj /neuro/labs/grantlab/research/HyukJin_MRI/Fetal_template/xfm/template-31toMNI.xfm '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj;')
	
	os.system('transform_objects '+input_fol+'/surfaces/lh.pial.to31_81920.obj '+input_fol+'/recon_segmentation//recon_native.xfm '+input_fol+'/surfaces/lh.pial.native_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/rh.pial.to31_81920.obj '+input_fol+'/recon_segmentation//recon_native.xfm '+input_fol+'/surfaces/rh.pial.native_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/lh.pial.to31_81920.obj /neuro/labs/grantlab/research/HyukJin_MRI/Fetal_template/xfm/template-31toMNI.xfm '+input_fol+'/surfaces/lh.pial.mni_81920.obj;')
	os.system('transform_objects '+input_fol+'/surfaces/rh.pial.to31_81920.obj /neuro/labs/grantlab/research/HyukJin_MRI/Fetal_template/xfm/template-31toMNI.xfm '+input_fol+'/surfaces/rh.pial.mni_81920.obj;')

#surface measures
def thickness():
	os.system('cortical_thickness -tlink '+input_fol+'/surfaces/lh.smoothwm.native_81920.obj  '+input_fol+'/surfaces/lh.pial.native_81920.obj '+input_fol+'/surfaces/lh.smoothwm.native_81920.thk;')
	os.system('cortical_thickness -tlink '+input_fol+'/surfaces/rh.smoothwm.native_81920.obj  '+input_fol+'/surfaces/rh.pial.native_81920.obj '+input_fol+'/surfaces/rh.smoothwm.native_81920.thk;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/lh.smoothwm.native_81920.thk '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj '+input_fol+'/surfaces/lh.smoothwm.native_81920.thk.s5;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/rh.smoothwm.native_81920.thk '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj '+input_fol+'/surfaces/rh.smoothwm.native_81920.thk.s5;')

def surf_meas():
	#s5 calculations inside /surfaces folder
	# os.system('python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/ADT/ADT_white_vFetal_final.py '+input_fol+'/surfaces/;')
	os.system('python3 /neuro/users/mri.team/Codes/pipeline_2024/part2/src/ADT_white_vFetal_final_rev.py '+input_fol+'/surfaces/;')	# Revised for current file namings with suffix '_81920'
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/lh.smoothwm.native_81920.depth '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/lh.smoothwm.native_81920.depth.s5;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/rh.smoothwm.native_81920.depth '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/rh.smoothwm.native_81920.depth.s5;')
 
	os.system('depth_potential -area_voronoi '+input_fol+'/surfaces/lh.smoothwm.native_81920.obj '+input_fol+'/surfaces/lh.smoothwm.native_81920.area;')
	os.system('depth_potential -area_voronoi '+input_fol+'/surfaces/rh.smoothwm.native_81920.obj '+input_fol+'/surfaces/rh.smoothwm.native_81920.area;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/lh.smoothwm.native_81920.area '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/lh.smoothwm.native_81920.area.s5;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/rh.smoothwm.native_81920.area '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/rh.smoothwm.native_81920.area.s5;')

	os.system('depth_potential -mean_curvature '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/lh.smoothwm.mni_81920.mc;')
	os.system('depth_potential -mean_curvature '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj  '+input_fol+'/surfaces/rh.smoothwm.mni_81920.mc;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/lh.smoothwm.mni_81920.mc '+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj '+input_fol+'/surfaces/lh.smoothwm.mni_81920.mc.s5;')
	os.system('depth_potential -smooth 5 '+input_fol+'/surfaces/rh.smoothwm.mni_81920.mc '+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj '+input_fol+'/surfaces/rh.smoothwm.mni_81920.mc.s5;')
	
	# whole brain depth, area, and curvature -> txt 
	os.system('echo `python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -sum '+input_fol+'/surfaces/lh.smoothwm.native_81920.area.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -sum '+input_fol+'/surfaces/rh.smoothwm.native_81920.area.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -mean '+input_fol+'/surfaces/lh.smoothwm.native_81920.depth.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -mean '+input_fol+'/surfaces/rh.smoothwm.native_81920.depth.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -ab_mean '+input_fol+'/surfaces/lh.smoothwm.mni_81920.mc.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -ab_mean '+input_fol+'/surfaces/rh.smoothwm.mni_81920.mc.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -mean '+input_fol+'/surfaces/lh.smoothwm.native_81920.thk.s5` '
		'`python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/vertex_mean_sum.py -mean '+input_fol+'/surfaces/rh.smoothwm.native_81920.thk.s5` >  '+input_fol+'/surfaces/Area_Depth_aMC_Thk.txt;')

#volume measures		
def vol_meas():		
	seg_final= input_fol+'/recon_segmentation/segmentation_to31_final.nii'
	final_nii= nib.load(seg_final)
	img_data= final_nii.get_fdata()

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
	

	
	xfm_path = input_fol+'/recon_segmentation/recon_native.xfm'
			
	os.system('xfm2param '+input_fol+'/recon_segmentation/recon_native.xfm | grep scale | cut -d" " -f11 > '+input_fol+'/temp/temp2.txt;')
	os.system('xfm2param '+input_fol+'/recon_segmentation/recon_native.xfm | grep scale | cut -d" " -f15 >> '+input_fol+'/temp/temp2.txt;')
	os.system('xfm2param '+input_fol+'/recon_segmentation/recon_native.xfm | grep scale | cut -d" " -f19 >> '+input_fol+'/temp/temp2.txt;')
	
	with open(input_fol+'/temp/temp2.txt') as temp2:
		scale_temp = [0,0,0]
		scale_temp=temp2.readlines()

	scale_av = float(scale_temp[0]) * float(scale_temp[1]) * float(scale_temp[2])
	print(scale_av)

	v1xScale = (vol1 * scale_av)
	v2xScale = (vol2 * scale_av)
	v3xScale = (vol3 * scale_av)
	v4xScale = (vol4 * scale_av)

	with open(input_fol+'/recon_segmentation/Volume_measures.txt', "w") as file:
		file.write('{} {} {} {}\n'.format(str(v1xScale), str(v2xScale), str(v3xScale), str(v4xScale)))

#gyrification index
def GI():
	os.system('mkdir ./'+input_fol+'/temp/hull/;')
	os.system('mri_distance_transform ./'+input_fol+'/recon_segmentation/segmentation_to31_final.nii 160 10 1 ./'+input_fol+'/temp/lh.dist10.nii;'
			'mri_threshold ./'+input_fol+'/temp/lh.dist10.nii 10 ./'+input_fol+'/temp/lh.dist10.mask.nii;'
			'mri_distance_transform ./'+input_fol+'/temp/lh.dist10.mask.nii 0 10 2 ./'+input_fol+'/temp/lh.dist10.mask.dist10.nii;'
			'fslmaths ./'+input_fol+'/temp/lh.dist10.mask.dist10.nii -mul -1 ./'+input_fol+'/temp/lh.dist10.mask.dist10.inv.nii;'
			'gunzip ./'+input_fol+'/temp/lh.dist10.mask.dist10.inv.nii.gz;'
			'mri_threshold ./'+input_fol+'/temp/lh.dist10.mask.dist10.inv.nii 10 ./'+input_fol+'/temp/lh.closing.nii;')
			
	os.system('mri_distance_transform ./'+input_fol+'/recon_segmentation/segmentation_to31_final.nii 161 10 1 ./'+input_fol+'/temp/rh.dist10.nii;'
			'mri_threshold ./'+input_fol+'/temp/rh.dist10.nii 10 ./'+input_fol+'/temp/rh.dist10.mask.nii;'
			'mri_distance_transform ./'+input_fol+'/temp/rh.dist10.mask.nii 0 10 2 ./'+input_fol+'/temp/rh.dist10.mask.dist10.nii;'
			'fslmaths ./'+input_fol+'/temp/rh.dist10.mask.dist10.nii -mul -1 ./'+input_fol+'/temp/rh.dist10.mask.dist10.inv.nii;'
			'gunzip ./'+input_fol+'/temp/rh.dist10.mask.dist10.inv.nii.gz;'
			'mri_threshold ./'+input_fol+'/temp/rh.dist10.mask.dist10.inv.nii 10 ./'+input_fol+'/temp/rh.closing.nii;')

	os.system('nii2mnc ./'+input_fol+'/temp/lh.closing.nii ./'+input_fol+'/temp/lh.closing.mnc;'
				'nii2mnc ./'+input_fol+'/temp/rh.closing.nii ./'+input_fol+'/temp/rh.closing.mnc;')
				
	os.system('mincmath -clobber -gt -const 0 ./'+input_fol+'/temp/lh.closing.mnc ./'+input_fol+'/temp/hull/closing_bin_left.mnc;'
				'mincmath -clobber -gt -const 0 ./'+input_fol+'/temp/rh.closing.mnc ./'+input_fol+'/temp/hull/closing_bin_right.mnc;')

				
	os.system('singularity exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp --adapt_object_mesh 0,100,0,0 '+input_fol+'/temp/hull/ '+input_fol+'/temp/hull/;')
	
	os.system('cp '+input_fol+'/temp/hull/closing_bin_left._81920.obj '+input_fol+'/temp/lh.hull.to31_81920.obj;'
				'cp '+input_fol+'/temp/hull/closing_bin_right._81920.obj '+input_fol+'/temp/rh.hull.to31_81920.obj;')

	os.system('measure_surface_area ./'+input_fol+'/surfaces/lh.smoothwm.to31_81920.obj > ./'+input_fol+'/temp/GI_inf2.txt;'
			'measure_surface_area ./'+input_fol+'/temp/lh.hull.to31_81920.obj >> ./'+input_fol+'/temp/GI_inf2.txt;'
			'measure_surface_area ./'+input_fol+'/surfaces/rh.smoothwm.to31_81920.obj >> ./'+input_fol+'/temp/GI_inf2.txt;'
			'measure_surface_area ./'+input_fol+'/temp/rh.hull.to31_81920.obj >> ./'+input_fol+'/temp/GI_inf2.txt;')
			
	with open(input_fol+'/temp/GI_inf2.txt') as GI_temp:
		temp=GI_temp.read()
		temp=temp.split('Area: '); 
		
		bh_surf= float(temp[1])+float(temp[3])
		bh_hull= float(temp[2])+float(temp[4])
		lh_GI=float(temp[1])/float(temp[2])
		rh_GI=float(temp[3])/float(temp[4])
		
		GI_temp.close

		bh_GI=str(bh_surf/bh_hull)
		lh_GI=str(lh_GI)
		rh_GI=str(rh_GI)
			
	with open(input_fol+'/surfaces/GI_info_final.txt', "w") as GI_final:
		GI_final.write('{} {} {}\n'.format(lh_GI, rh_GI, bh_GI))

	# os.system('echo '+lh_GI+' '+rh_GI+' '+bh_GI+' > ./'+input_fol+'/surfaces/GI_info_final.txt;')
	

def main():
	args = parser.parse_args()
	print(args)

	global input_fol
	input_fol = args.input_fol		## input_fol should be: ./$file

	if not os.path.exists(input_fol+'/temp/'):
		os.system('mkdir '+input_fol+'/temp/')
	
	if args.thickness:
		transformation()
		thickness()
	else:
		transformation()
		thickness()
		surf_meas()
		vol_meas()
		GI() 


if __name__ == '__main__':
    main()
