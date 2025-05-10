#!/bin/env python3
import os
import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse
import tempfile

def main(args):
	input_surf = args.input_surf
	target_surf = args.target_surf
	output_sm = args.output_sm
	output_surf = args.output_surf
	options = args.options
	
	folder_path_surf = output_surf.replace(output_surf.split('/')[-1],"")
	folder_path_sm = output_sm.replace(output_sm.split('/')[-1],"")
	
	os.system('mkdir -p '+folder_path_surf)
	os.system('mkdir -p '+folder_path_sm)
		
	#surface registration	
	os.system('bestsurfreg.pl '+options+' '+target_surf+' '+input_surf+' '+output_sm)
	#surface resample
	os.system('sphere_resample_obj -clobber '+input_surf+' '+output_sm+' '+output_surf)
	
if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Outer Surface Extraction [+ Laplacian map] ==========   ')

	parser.add_argument('-i', '--input_surf',action='store', dest='input_surf',type=str, required=True, help='Input surface')
	parser.add_argument('-t', '--target_surf',action='store', dest='target_surf',type=str, required=True, help='Target surface')
	parser.add_argument('-o', '--output_surf',action='store',dest='output_surf', type=str, required=True, help='Resampled surface')
	parser.add_argument('-sm', '--output_sm',action='store',dest='output_sm', type=str, required=True, help='Resampling file')
	parser.add_argument('-b', '--options',action='store',dest='options', type=str, default = '-clobber -min_control_mesh 80 -max_control_mesh 81920 -blur_coef 1.25 -neighbourhood_radius 2.8 -maximum_blur 1.9', help='Option for bestsurfreg.pl')
	
	args = parser.parse_args()
	
	main(args)

