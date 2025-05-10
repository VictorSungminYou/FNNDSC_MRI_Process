''' Post nuc , input is the post alignment file.'''
import os
import argparse

def get_parent_path(dir_path):
    ''' Get the parent directory path '''
    return os.path.abspath(os.path.join(dir_path, os.pardir))

parser = argparse.ArgumentParser('=== Fetal alignment script for fetal pipeline ===')

parser.add_argument('-i','--input','--input_file',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input file name')

parser.add_argument('-o','--output_file',
                    action='store',
                    dest='output_file',
                    type=str,
                    default='recon_to31_nuc.nii',
                    help='output file name')

# Arguments from parser place into variable args
args = parser.parse_args()

input_file = args.inp
parent_fol = get_parent_path(input_file)

output_file = os.path.join(parent_fol, args.output_file)

print("-Performing Post NUC ...")
os.system('~/arch/Linux64/packages/ANTs/current/bin/N4BiasFieldCorrection -d 3 -o '
          + output_file + ' -i ' + input_file)
