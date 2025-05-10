#!/bin/env python3
import os
import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse
import tempfile

def main(args):
	
	input_seg = args.input_seg
	side = args.side
	label = args.label
	surf = args.surf
	taubin = args.taubin
	subsampling = args.subsampling
	
	print(side)
	print(label)
	
	temp_dir = tempfile.TemporaryDirectory()
	temp_dir2 = tempfile.TemporaryDirectory()
	#os.system('rm '+temp_dir2.name+'/*')
	
	temp_seg = temp_dir2.name+'/temp_seg.mnc'
	os.system('nii2mnc '+input_seg+' '+temp_seg)
	
	os.system('mincmath -clobber -eq -const '+label+' '+temp_seg+' '+temp_dir.name+'/surf_inner_'+side+'.mnc')
	# os.system('cp '+temp_dir2.name+'/temp_seg.mnc temp_seg_'+side+'.mnc')
	
	
	### Surface extraction
	if args.subsampling == True:
		os.system('singularity exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp --side '+side+ ' --adapt_object_mesh 0,100,0,0 --mincmorph-iterations 1 --subsample '+temp_dir.name+' '+temp_dir2.name)
	else:
		os.system('singularity exec docker://fnndsc/pl-fetal-cp-surface-extract extract_cp --side '+side+ ' --adapt_object_mesh 0,100,0,0 --mincmorph-iterations 1 '+temp_dir.name+' '+temp_dir2.name)
		
	### to sanity check
	#os.system('cp '+temp_dir.name+'/* .')
	#os.system('cp '+temp_dir2.name+'/* .')

	#os.system('adapt_object_mesh '+folder_path+'/surf_inner_'+side+'._81920.obj '+surf+' 0 '+taubin+' 0 0;')
	### Checking self-intersection	
	print('check_self_intersect '+temp_dir2.name+'/surf_inner_'+side+'._81920.obj '+temp_dir2.name+'/self_intersection.txt')
	os.system('check_self_intersect '+temp_dir2.name+'/surf_inner_'+side+'._81920.obj '+temp_dir2.name+'/self_intersection.txt')

	self_intersection_vertex(temp_dir2.name+'/self_intersection.txt', surf.replace(".obj",".self_intersection.txt"))
	
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/obj2asc '+temp_dir2.name+'/surf_inner_'+side+'._81920.obj '+temp_dir2.name+'/surf_inner_'+side+'._81920.asc')
	os.system('obj2asc '+temp_dir2.name+'/surf_inner_'+side+'._81920.obj '+temp_dir2.name+'/surf_inner_'+side+'._81920.asc')
	os.system('mris_remove_intersection '+temp_dir2.name+'/surf_inner_'+side+'._81920.asc '+temp_dir2.name+'/surf_inner_'+side+'._corrected_81920.asc')
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/asc2obj '+temp_dir2.name+'/surf_inner_'+side+'._corrected_81920.asc '+temp_dir2.name+'/surf_inner_'+side+'._corrected_81920.obj')
	
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/mesh_to_std_format.pl '+temp_dir2.name+'/surf_inner_'+side+'._corrected_81920.obj -'+side+' '+temp_dir2.name+'/surf_inner_'+side+'._corrected_resampled_81920.obj')
	
	if taubin != 0:
		os.system('adapt_object_mesh '+temp_dir2.name+'/surf_inner_'+side+'._corrected_resampled_81920.obj '+surf+' 0 '+taubin+' 0 0;')
	else:
		os.system('mv '+temp_dir2.name+'/surf_inner_'+side+'._corrected_resampled_81920.obj '+surf)
	### Distance error between volume and surface
	os.system('mri_binarize --i '+input_seg+' --match '+label+' --o '+temp_dir2.name+'/temp_seg.nii')
	os.system('mri_distance_transform '+temp_dir2.name+'/temp_seg.nii 1 20 3 '+temp_dir2.name+'/temp_seg_dist.nii')
	os.system('nii2mnc '+temp_dir2.name+'/temp_seg_dist.nii '+temp_dir2.name+'/temp_seg_dist.mnc')
	
	os.system('volume_object_evaluate '+temp_dir2.name+'/temp_seg_dist.mnc ' +surf+' '+surf.replace(".obj",".disterr.txt"))
	
	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/obj2asc '+surf+' '+surf.replace(".obj",".asc"))

	
		
def self_intersection_vertex(file_name, output):

	val_list = open(file_name, 'r')
	temp_list =[]

	lines=val_list.readlines()
	for line in lines:
		temp_list.append(float(line))
		
	dist_val = np.array(temp_list)
	if len(np.where(dist_val<0.00000001))>0:
		print("\n\nSelf-intersection of the surface was found - see "+str(output))
		np.savetxt(output,np.transpose(np.where(dist_val<0.00001)),fmt="%d")

if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Outer Surface Extraction  ==========   ')

	parser.add_argument('-i', '--input_seg',action='store', dest='input_seg',type=str, required=True, help='Segmentation')
	parser.add_argument('-o', '--output_surface',action='store',dest='surf', type=str, required=True, help='Inner surface')
	parser.add_argument('-l', '--label',action='store',dest='label', type=str, required=True, help='Segmentation label for surface extraction')
	parser.add_argument('-sd {left or right}', '--side',choices=['left', 'right'],action='store',dest='side', type=str, required=True, help='Hemisphere [important for vertex index]')
	parser.add_argument('-t', '--taubin',action='store',dest='taubin', type=str, default = '100', help='Global iteration of taubin smoothing')
	parser.add_argument('-sub', '--subsampling', action ='store',dest='subsampling',type=str, default=True, help='Whether to subsample WM or not')
	args = parser.parse_args()
	
	main(args)

