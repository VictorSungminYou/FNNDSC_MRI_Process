import os
import time
import argparse

def get_parent_path(dir_path):
    return os.path.abspath(os.path.join(dir_path, os.pardir))

parser = argparse.ArgumentParser('   ==========   Fetal alignment script for fetal pipeline   ==========   ')

parser.add_argument('--input_file',
                    action='store', 
                    dest='inp', 
                    type=str, 
                    required=True, 
                    help='input file name')

parser.add_argument('--output_file',
                    action='store', 
                    dest='output_file', 
                    type=str, 
                    default='recon_to31_nuc.nii', 
                    help='output file name')

# Arguments from parser place into variable args
args = parser.parse_args()

input_file = args.inp
output_file = args.output_file

print("-Performing Post NUC ...")
os.system('~/arch/Linux64/packages/ANTs/current/bin/N4BiasFieldCorrection -d 3 -o '+output_file+' -i '+input_file)
