#!/bin/env python3
import os
import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse

def main(args):

	os.system('/neuro/labs/grantlab/research/HyukJin_MRI/CIVET/quarantines/Linux-x86_64/bin/expand_from_white_fetal_MNI.pl '+args.i_surf+' '+args.o_surf+' '+args.lap_volume+' '+args.sw+' '+args.lw);

if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Outer Surface Extraction  ==========   ')

	parser.add_argument('-lm', '--laplacian_map',action='store', dest='lap_volume',type=str, required=True, help='Laplacian map')
	parser.add_argument('-i', '--inner_surface',action='store',dest='i_surf', type=str, required=True, help='Inner surface [should contain suffix _81920.obj]')
	parser.add_argument('-o', '--outer_surface',action='store', dest='o_surf',type=str, required=True, help='Outer surface')
	parser.add_argument('-sw', '--stretch_weight',action='store', dest='sw',type=str, default = '1.0', help='Stretch weight for outer surface deformation')
	parser.add_argument('-lw', '--laplacian_weight',action='store', dest='lw',type=str, default = '1.0', help='Laplacian weight for outer surface deformation')
	args = parser.parse_args()
	
	main(args)

