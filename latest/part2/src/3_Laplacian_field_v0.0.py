#!/bin/env python3
import os
import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse

def main(args):

	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/code/laplace_CSF.pl '+args.input_seg+' '+args.i_surf+' '+args.CLASP_label+' '+args.lap_volume);

if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Laplacian map ==========   ')
	parser.add_argument('-i', '--input_seg', action='store',dest='input_seg', type=str, required=True, help='CLASP segmentation [.mnc]')
	parser.add_argument('-o', '--output_laplacian',action='store', dest='lap_volume',type=str, required=True, help='Laplacian map')
	parser.add_argument('-l', '--CLASP_label',action='store', dest='CLASP_label',type=str, default = '2', help='CLASP Label for CP [default = 2]')
	parser.add_argument('-s', '--inner_surface',action='store',dest='i_surf', type=str, required=True, help='Inner surface')
	
	args = parser.parse_args()
	
	main(args)

