from pathlib import Path
import subprocess as sp
from tempfile import NamedTemporaryFile
import argparse, os
import numpy as np

############# TBCOMPLETED, for now included in CP extraction



def surfdisterr(surface: Path, mask: Path, output: Path, label: np.int16):
    """
    Compute the distance from each vertex of the surface to the mask boundary,
    and write the output to a text file.
    """
    with NamedTemporaryFile(suffix='.nii') as temp1:
        mask_tmp = temp1.name
        distance_tmp = 'distance.nii'
        distance_mnc = 'distance.mnc'
        
        create_mask(mask, mask_tmp, label)
        create_distance(mask_tmp, distance_tmp)
        convert_distance(distance_tmp, distance_mnc)
        disterr(distance_mnc, surface, output)
        
        os.system('rm ' + distance_tmp)
        os.system('rm ' + distance_mnc)

def create_mask(mask, mask_tmp, label):
    cmd = ['mri_binarize', '--i', mask, '--match', label, '--o', mask_tmp]
    sp.run(cmd, check=True)


def create_distance(mask_tmp, distance_tmp):
    cmd = ['mri_distance_transform', mask_tmp, '1', '20', '3', distance_tmp]
    sp.run(cmd, check=True)


def convert_distance(distance_tmp, distance_mnc):
    #os.system('nii2mnc '+distance_tmp+' '+ distance_mnc)
    print(distance_tmp, distance_mnc)
    
    #cmd = ['nii2mnc', distance_tmp, distance_mnc]
    #cmd = 'nii2mnc {} {}'.format(distance_tmp, distance_mnc)
    os.system('nii2mnc ' + distance_tmp + ' ' + distance_mnc)
    #sp.run(cmd, check=True)


def disterr(distance_mnc, surface, output):
    cmd = ['volume_object_evaluate', distance_mnc, surface, output]
    sp.run(cmd, check=True)
    

    
def main(args):
    input_surface=args.input_surface
    input_mask=args.input_mask
    label=args.label
    output_disterr=args.output_disterr

    surfdisterr(input_surface, input_mask, output_disterr, label)

		
if __name__== '__main__':
	
    parser = argparse.ArgumentParser('   ==========   Calculating distance error  ==========   ')
    parser.add_argument('-s', '--input_surface',action='store', dest='input_surface',type=str, required=True, help='Input surface')
    parser.add_argument('-m', '--input_mask',action='store', dest='input_mask',type=str, required=True, help='Input mask for the boundary')
    parser.add_argument('-l', '--label',action='store', dest='label',type=str, required=True, help='Region label (e.g. 160 for lh CP)')
    parser.add_argument('-o', '--output_disterr',action='store',dest='output_disterr', type=str, required=True, help='Ouput file with distance error')
    args = parser.parse_args()
    main(args)
		
		
		   
  
