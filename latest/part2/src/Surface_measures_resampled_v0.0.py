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

#surface registration 	
def surf_reg():		
	for i in templ_num:
		os.system('bestsurfreg.pl -clobber -min_control_mesh 80 -max_control_mesh 81920 -blur_coef 1.25 -neighbourhood_radius 2.8 -maximum_blur 1.9 /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.mni.obj ./'+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj  ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.toT'+i+'.sm;')
		os.system('bestsurfreg.pl -clobber -min_control_mesh 80 -max_control_mesh 81920 -blur_coef 1.25 -neighbourhood_radius 2.8 -maximum_blur 1.9 /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.mni.obj ./'+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj  ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.toT'+i+'.sm;')

#surface resample
def resampling():
	for i in templ_num:
		os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/lh.smoothwm.mni_81920.obj ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.toT'+i+'.sm ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl'+i+'.obj;')
		os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/rh.smoothwm.mni_81920.obj ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.toT'+i+'.sm ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl'+i+'.obj;')
		
		os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/lh.pial.mni_81920.obj ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.toT'+i+'.sm ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.mni_81920.rsl'+i+'.obj;')
		os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/rh.pial.mni_81920.obj ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.toT'+i+'.sm ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.mni_81920.rsl'+i+'.obj;')
		
		if i == "29":
			os.system('cp ./'+input_fol+'/surfaces/template-29/lh.smoothwm.mni_81920.rsl29.obj ./'+input_fol+'/surfaces/template-29/lh.smoothwm.mni_81920.rsl.obj;')
			os.system('cp ./'+input_fol+'/surfaces/template-29/rh.smoothwm.mni_81920.rsl29.obj ./'+input_fol+'/surfaces/template-29/rh.smoothwm.mni_81920.rsl.obj;')
			
			os.system('cp ./'+input_fol+'/surfaces/template-29/lh.pial.mni_81920.rsl29.obj ./'+input_fol+'/surfaces/template-29/lh.pial.mni_81920.rsl.obj;')
			os.system('cp ./'+input_fol+'/surfaces/template-29/rh.pial.mni_81920.rsl29.obj ./'+input_fol+'/surfaces/template-29/rh.pial.mni_81920.rsl.obj;')
		else:
			os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl'+i+'.obj /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.T29.sm ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj;')
			os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl'+i+'.obj /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.T29.sm ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj;')
			os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.mni_81920.rsl'+i+'.obj /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.T29.sm ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.mni_81920.rsl.obj;')
			os.system('sphere_resample_obj -clobber ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.mni_81920.rsl'+i+'.obj /neuro/users/mri.team/fetal_mri/Surface_template/template-'+i+'/bh.smoothwm.T29.sm ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.mni_81920.rsl.obj;')

		os.system('transform_objects ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj /neuro/users/mri.team/fetal_mri/Surface_template/xfm/template-31toMNI_inv.xfm  ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.to31_81920.rsl.obj;')
		os.system('transform_objects ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj /neuro/users/mri.team/fetal_mri/Surface_template/xfm/template-31toMNI_inv.xfm  ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.to31_81920.rsl.obj;')
		os.system('transform_objects '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.to31_81920.rsl.obj ./'+input_fol+'/recon_segmentation/recon_native.xfm ./'+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.obj;')
		os.system('transform_objects '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.to31_81920.rsl.obj ./'+input_fol+'/recon_segmentation/recon_native.xfm ./'+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.obj;')
		
		os.system('transform_objects ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.mni_81920.rsl.obj /neuro/users/mri.team/fetal_mri/Surface_template/xfm/template-31toMNI_inv.xfm  ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.to31_81920.rsl.obj;')
		os.system('transform_objects ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.mni_81920.rsl.obj /neuro/users/mri.team/fetal_mri/Surface_template/xfm/template-31toMNI_inv.xfm  ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.to31_81920.rsl.obj;')
		os.system('transform_objects '+input_fol+'/surfaces/template-'+i+'/lh.pial.to31_81920.rsl.obj ./'+input_fol+'/recon_segmentation/recon_native.xfm ./'+input_fol+'/surfaces/template-'+i+'/lh.pial.native_81920.rsl.obj;')
		os.system('transform_objects '+input_fol+'/surfaces/template-'+i+'/rh.pial.to31_81920.rsl.obj ./'+input_fol+'/recon_segmentation/recon_native.xfm ./'+input_fol+'/surfaces/template-'+i+'/rh.pial.native_81920.rsl.obj;')

#surface measures
def surf_meas():
	for i in templ_num:
#sulcal depth 			
		# os.system('python3 /neuro/labs/grantlab/research/HyukJin_MRI/code/ADT/ADT_white_vFetal_final_rsl.py '+input_fol+'/surfaces/template-'+i+'/;')
		os.system('python3 /neuro/users/mri.team/Codes/pipeline_2024/part2/src/ADT_white_vFetal_final_rsl_rev.py '+input_fol+'/surfaces/template-'+i+'/;') # Revised for current file namings with suffix '_81920'
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.depth '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.depth.s10;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.depth '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.depth.s10;')	
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.depth '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.depth.s20;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.depth '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.depth.s20;')	

# surface area
		os.system('depth_potential -area_voronoi '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.area;')
		os.system('depth_potential -area_voronoi '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.area;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.area '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.area.s10;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.area '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.area.s10;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.area '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.area.s20;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.area '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.area.s20;')

# mean curvature
		os.system('depth_potential -mean_curvature '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.mc;')
		os.system('depth_potential -mean_curvature '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj  '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.mc;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.mc '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.mc.s10;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.mc '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.mc.s10;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.mc '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.mc.s20;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.mc '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.mc.s20;')

# thickness

		os.system('cortical_thickness -tlink '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.pial.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk ')
		os.system('cortical_thickness -tlink '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.pial.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk ')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk.s10;')
		os.system('depth_potential -smooth 10 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.thk.s10;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/lh.smoothwm.native_81920.rsl.thk.s20;')
		os.system('depth_potential -smooth 20 '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.thk '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.mni_81920.rsl.obj '+input_fol+'/surfaces/template-'+i+'/rh.smoothwm.native_81920.rsl.thk.s20;')

def main():
	args = parser.parse_args()
	print(args)

	global input_fol
	input_fol = args.input_fol		## input_fol should be: ./$file

	global templ_num
	global i 
	templ_num=("29","31","adult")		##default to template 29
	for i in templ_num:
		os.makedirs(input_fol+'/surfaces/template-'+i+'/', exist_ok=True)
	
	surf_reg()
	resampling()
	surf_meas()

if __name__ == '__main__':
    main()
