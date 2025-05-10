import os
import argparse
from helper_functions import timeit_decorator
import sys
import logging
import time

parser = argparse.ArgumentParser(' === Main script to run all steps === ')

parser.add_argument('-i', '--input', '--input_folder',
                    action='store',
                    dest='inp',
                    type=str,
                    required=False,
                    help='Input folder name')


parser.add_argument('-pwd',
                    action='store_true',
                    dest='pwd',
                    help='Use the present working directory as the input path')


args = parser.parse_args()


if args.pwd:
    print("Using present working directory")

    #TODO this but cleaner and universal
    input_fol=os.getcwd().replace('/net/rc-fs-nfs.tch.harvard.edu/FNNDSC-e2', '/')

    print("input fol var",input_fol)

elif args.inp:
    print("Using input directory")
    input_fol=args.inp
else:
    raise ValueError("You must specify either -pwd or -i/--input to provide an input path.")


@timeit_decorator
def masking():
    ''' -Masking 
    Input: Directory with the raw files (main directory)
    Output: 3 sub-directories in input dir, raw,masks,brain 
    '''
    logging.info(" @@@ Running masking @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/masking.py -i {input_fol}')

@timeit_decorator
def nuc():
    ''' -NUC 
    Input: main Directory 
    Output: nuc directory in the main dir 
    notes: from the input it will find the brain folder, the material for nuc
    '''
    logging.info(" @@@ Running NUC @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/nuc.py -i {input_fol}')

@timeit_decorator
def qa():
    ''' -QA
    Input: nuc folder directory
    Output: quality assessment csv  in main dir
    '''
    input_qa = input_fol + '/nuc'

    logging.info(" @@@ Running QA @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/qa.py -i {input_qa}')

@timeit_decorator
def reconstruction():
    '''Recon, input directory path must have csv and nuc folder.
    Input: main dir, where the qa file is located
    Output: recon folder in main dir with recon.nii file
    Notes: the quality csv file must have the correct paths to the nuc files
    '''
    logging.info(" @@@ Running Reconstruction @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/reconstruction.py -i {input_fol}')

@timeit_decorator
def alignment():
    '''Alignment 
    Input: recon.nii file 
    Output: recon_alignment.nii in the recon folder
    '''

    logging.info(" @@@ Running Alignment @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/alignment.py -i {os.path.join(input_fol,"recon","recon.nii")}')

@timeit_decorator
def post_nuc():
    '''Post NUC
    Input: recon_alignment file from the last step
    Output: recon_to31_nuc.nii in main folder
    '''
    logging.info(" @@@ Running Post NUC @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/post_nuc.py -i {os.path.join(input_fol,"recon","recon_alignment.nii")}')

@timeit_decorator
def segmentation():
    '''Segmentation
    input: recon_to31_nuc.nii file
    output: segmentation folder in main directory
    '''
    logging.info(" @@@ Running Segmentation @@@ ")
    os.system(f'python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/pipeline_gilberto/segmentation.py -i {os.path.join(input_fol,"recon_to31_nuc.nii")}')



@timeit_decorator
def main():
    
    try:
        masking()
    except Exception as e :
        print(f"masking error,{e}")
        sys.exit()

    time.sleep(1)
    print(" *** Starting Non uniform correction *** ")
    time.sleep(1)

    try:
        nuc()
    except Exception as e:
        print(f"nuc error,{e}")
        sys.exit()

    time.sleep(3)
    print(" *** Starting QA assessment *** ")
    time.sleep(1)

    try:
        qa()
    except Exception as e:
        print(f"qa error,{e}")
        sys.exit()

    time.sleep(1)
    print(" *** Starting Reconstruction *** ")
    time.sleep(1)

    try:
        reconstruction()
    except Exception as e:
        print(f"recon error,{e}")
        sys.exit()

    time.sleep(1)
    print(" *** Starting Alignment *** ")
    time.sleep(1)

    try:
        alignment()
    except Exception as e:
        print(f"alignment error,{e}")
        sys.exit()

    time.sleep(1)
    print(" *** Starting Post NUC *** ")
    time.sleep(1)

    try:
        post_nuc()
    except Exception as e:
        print(f"post_nuc error,{e}")
        sys.exit()

    time.sleep(1)
    print(" *** Starting Segmentation *** ")
    time.sleep(1)

    try:
        segmentation()
    except Exception as e:
        print(f"segmentation error,{e}")
        sys.exit()

    print(" ***** Script finished *****")

main()
