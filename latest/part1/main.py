import os
import argparse
from src.helper_functions import timeit_decorator, verify
import sys
import logging
import time
import nibabel as nib
import glob
import numpy as np
import matplotlib.pyplot as plt

@timeit_decorator
def mask_func():
    ''' -Masking 
    Input: Directory with the raw files (main directory)
    Output: 3 sub-directories in input dir, raw,masks,brain 
    '''
    logging.info(" @@@ Running masking @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/masking.py -i {input_fol}')
    os.makedirs('{0}/verify'.format(input_fol), exist_ok=True)
    os.system('cp {0}/brain/* {0}/verify/'.format(input_fol))
    verify('{}/verify'.format(input_fol))

@timeit_decorator
def remask_func():
    ''' -Re_Masking 
    Input: Directory with the raw files (main directory)
    Output: 3 sub-directories in input dir, raw,masks,brain 
    '''
    logging.info(" @@@ Running masking @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/masking.py -i {input_fol} --remask')
    os.makedirs('{0}/verify'.format(input_fol), exist_ok=True)
    os.system('cp {0}/brain/* {0}/verify/'.format(input_fol))
    verify('{}/verify'.format(input_fol))


@timeit_decorator
def nuc_func():
    ''' -NUC 
    Input: main Directory 
    Output: nuc directory in the main dir 
    notes: from the input it will find the brain folder, the material for nuc
    '''
    logging.info(" @@@ Running NUC @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/nuc.py -i {input_fol}')

@timeit_decorator
def qa_func():
    ''' -QA
    Input: nuc folder directory
    Output: quality assessment csv  in main dir
    '''
    input_qa = input_fol + '/nuc'

    logging.info(" @@@ Running QA @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/qa.py -i {input_qa}')

@timeit_decorator
def reconstruction_func():
    '''Recon, input directory path must have csv and nuc folder.
    Input: main dir, where the qa file is located
    Output: recon folder in main dir with recon.nii file
    Notes: the quality csv file must have the correct paths to the nuc files
    '''
    logging.info(" @@@ Running Reconstruction @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/reconstruction.py -i {input_fol}')

@timeit_decorator
def alignment_func():
    '''Alignment 
    Input: recon.nii file 
    Output: recon_alignment.nii in the recon folder
    '''

    logging.info(" @@@ Running Alignment @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/alignment.py -i {os.path.join(input_fol,"recon_segmentation","recon.nii")}')

@timeit_decorator
def two_step_alignment_func():
    '''Two step Alignment 
    Input: recon.nii file 
    Output: recon_alignment.nii in the recon folder
    '''

    logging.info(" @@@ Running Two step Alignment @@@ ")

    ##Moving recon.nii to recon_segmentation folder
    if not os.path.exists("{0}/recon_segmentation".format(input_fol)):
        os.system("mkdir {0}/recon_segmentation".format(input_fol))
    if os.path.exists("{0}/recon.nii".format(input_fol)):
        os.system("mv {0}/recon.nii {0}/recon_segmentation/".format(input_fol))

    ##Run initial alignment
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/alignment.py -i {os.path.join(input_fol,"recon_segmentation","recon.nii")}')

    ##Perform initial Post NUC
    os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/init_PostNUC.py --input_file {0}/recon_segmentation/recon_to31.nii --output_file {0}/recon_segmentation/recon_to31_nuc.nii".format(input_fol))

    ##Run initial segmentation with 4-label CP model
    os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/segmentation_4.py --input {0}/recon_segmentation/recon_to31_nuc.nii --output_fol {0}/recon_segmentation".format(input_fol))

    ##Mask out brain using initial segmentation
    os.system("mri_mask {0}/recon_segmentation/recon_to31_nuc.nii {0}/recon_segmentation/recon_to31_nuc_deep_agg.nii.gz {0}/recon_segmentation/recon_to31init_nuc_mask.nii".format(input_fol))

    os.system("mv {0}/recon_segmentation/recon_to31_nuc.nii {0}/recon_segmentation/recon_to31init_nuc.nii".format(input_fol))
    os.system("mv {0}/recon_segmentation/alignment_temp/recon_to31.xfm {0}/recon_segmentation/recon_to31init.xfm".format(input_fol))
       
    ##Perform second alignment
    # Original version
    #os.system("python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_codes/alignment_junshen_init_seg.py {0}/recon_segmentation".format(input_fol))

    # Parallel Computing version
    os.system("python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/alignment_junshen_init_seg_par.py {0}/recon_segmentation".format(input_fol))


@timeit_decorator
def post_nuc_func():
    '''Post NUC
    Input: recon_alignment file from the last step
    Output: recon_to31_nuc.nii in main folder
    '''
    logging.info(" @@@ Running Post NUC @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/post_nuc.py -i {os.path.join(input_fol,"recon_segmentation","recon_to31.nii")}')

@timeit_decorator
def segmentation_func():
    '''Segmentation
    input: recon_to31_nuc.nii file
    output: segmentation folder in main directory
    '''
    logging.info(" @@@ Running Segmentation @@@ ")
    os.system(f'python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/segmentation.py -i {os.path.join(input_fol,"recon_segmentation","recon_to31_nuc.nii")}')

@timeit_decorator
def volume_measure_func():
    '''Volume measurement
    input: recon_to31_nuc_deep_agg.nii.gz file; recon_native.xfm file
    output: Volume measurement at "/recon_segmentation/Volume_measures.txt"
    '''
    logging.info(" @@@ Running Volume measurement @@@ ")
    os.system('python3 /neuro/users/mri.team/Codes/pipeline_2024/part1/src/Volume_measures_v0.0.py --input_segmentation {0}/recon_segmentation/recon_to31_nuc_deep_agg.nii.gz --recon_native_xfm {0}/recon_segmentation/recon_native.xfm'.format(input_fol))

@timeit_decorator
def main(args):

    masking = args.masks
    remasking = args.remask
    NUC = args.NUC
    QA = args.QA
    reconstruction = args.recon
    alignment = args.align
    post_nuc = args.post_nuc
    seg = args.auto_seg
    vol_measure = args.vol_measure

    from_remask = args.remask__
    fromNUC = args.nuc__
    fromQA = args.qa__
    from_recon = args.recon__
    from_align = args.align__
    allSteps = args.all

    if masking == True:
        try:
            mask_func()
        except Exception as e :
            print(f"masking error,{e}")
            sys.exit()
    if remasking == True: 
        try:
            remask_func()
        except Exception as e :
            print(f"Remasking error,{e}")
            sys.exit()
    if NUC == True:
        try:
            nuc_func()
        except Exception as e:
            print(f"nuc error,{e}")
            sys.exit()
    if QA == True:
        try:
            qa_func()
        except Exception as e:
            print(f"qa error,{e}")
            sys.exit()
    if reconstruction == True:
        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()
    if alignment == True:
        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()
    if post_nuc == True:
        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()
    if seg == True:
        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()
    if vol_measure == True:
        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()

    if from_remask == True:
        print(" *** Starting from Remasking *** ")
        time.sleep(1)

        try:
            remask_func()
        except Exception as e :
            print(f"Remasking error,{e}")
            sys.exit()

        try:
            nuc_func()
        except Exception as e:
            print(f"nuc error,{e}")
            sys.exit()

        try:
            qa_func()
        except Exception as e:
            print(f"qa error,{e}")
            sys.exit()

        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()

    if fromNUC == True:
        print(" *** Starting from Non uniform correction *** ")
        time.sleep(1)

        try:
            nuc_func()
        except Exception as e:
            print(f"nuc error,{e}")
            sys.exit()

        try:
            qa_func()
        except Exception as e:
            print(f"qa error,{e}")
            sys.exit()

        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()

    if fromQA == True:
        print(" *** Starting from Quality Assessment *** ")
        time.sleep(1)

        try:
            qa_func()
        except Exception as e:
            print(f"qa error,{e}")
            sys.exit()

        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()
        
    if from_recon == True:
        print(" *** Starting from Reconstruction *** ")
        time.sleep(1)

        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()

    if from_align == True:
        print(" *** Starting from Alignment *** ")
        time.sleep(1)

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()

    if allSteps == True:
        print(" *** Starting from Masking *** ")

        try:
            mask_func()
        except Exception as e :
            print(f"masking error,{e}")
            sys.exit()

        time.sleep(1)
        print(" *** Starting Non uniform correction *** ")
        time.sleep(1)

        try:
            nuc_func()
        except Exception as e:
            print(f"nuc error,{e}")
            sys.exit()

        time.sleep(3)
        print(" *** Starting QA assessment *** ")
        time.sleep(1)

        try:
            qa_func()
        except Exception as e:
            print(f"qa error,{e}")
            sys.exit()

        time.sleep(1)
        print(" *** Starting Reconstruction *** ")
        time.sleep(1)

        try:
            reconstruction_func()
        except Exception as e:
            print(f"recon error,{e}")
            sys.exit()

        time.sleep(1)
        print(" *** Starting Alignment *** ")
        time.sleep(1)

        try:
            two_step_alignment_func()
        except Exception as e:
            print(f"alignment error,{e}")
            sys.exit()

        time.sleep(1)
        print(" *** Starting Post NUC *** ")
        time.sleep(1)

        try:
            post_nuc_func()
        except Exception as e:
            print(f"post_nuc error,{e}")
            sys.exit()

        time.sleep(1)
        print(" *** Starting Segmentation *** ")
        time.sleep(1)

        try:
            segmentation_func()
        except Exception as e:
            print(f"segmentation error,{e}")
            sys.exit()
        print(" ***** Segmentaion finished *****")

        time.sleep(1)
        print(" *** Starting Volume measurement *** ")
        time.sleep(1)

        try:
            volume_measure_func()
        except Exception as e:
            print(f"volume measurement error,{e}")
            sys.exit()
        print(" ***** Volume measurement finished *****")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(' === Main script to run all steps === ')

    parser.add_argument('-i', '--input', '--input_folder', '--input_fol',
                        action='store',
                        dest='inp',
                        type=str,
                        required=False,
                        help='Input folder name')

    parser.add_argument('-pwd',
                        action='store_true',
                        dest='pwd',
                        help='Use the present working directory as the input path')

    parser.add_argument('--from_remask', 
        dest='remask__',
        action='store_true',
        help='extracts corrected brain region and does following steps')

    parser.add_argument('--from_NUC', 
        dest='nuc__',
        action='store_true',
        help='NUC to auto segmentation')

    parser.add_argument('--from_QA', 
        dest='qa__',
        action='store_true',
        help='QA to segmentation')

    parser.add_argument('--from_recon', 
        dest='recon__',
        action='store_true',
        help='recon to segmentation')

    parser.add_argument('--from_alignment', 
        dest='align__',
        action='store_true',
        help='alignment to segmentation')

    parser.add_argument('--all', 
        dest='all',
        action='store_true',
        help='does all steps from masking')

    parser.add_argument('--masking', '--mask',
        dest='masks', 
        action='store_true',
        help='creates masks of the raw scans and moves the mask files into a folder')

    parser.add_argument('--remask', 
        dest='remask', 
        action='store_true',
        help='creates brain folder and extracts brain region using manually corrected masks')

    parser.add_argument('--NUC', '--nuc', 
        dest='NUC', 
        action='store_true',
        help='performs non uniformity corrrection')

    parser.add_argument('--QA', '--qa',
        dest='QA',
        action='store_true',
        help='creates quality assessment .csv')

    parser.add_argument('--recon', '--reconstruction',
        dest='recon',
        action='store_true',
        help='performs reconstructions using NESVOR')

    parser.add_argument('--alignment', '--align',
        dest='align',
        action='store_true',
        help='aligns the reconstructed images')

    parser.add_argument('--post_nuc',
        dest='post_nuc',
        action='store_true',
        help='Perform second NUC')

    parser.add_argument('--segment', '--segmentation',
        dest='auto_seg',
        action='store_true',
        help='automatically segments the reconstructed images')

    parser.add_argument('--vol_measure',
        dest='vol_measure',
        action='store_true',
        help='Compute volume measurements')
    
    args = parser.parse_args()

    if args.pwd:
        print("Using present working directory")
        input_fol=os.getcwd().replace('/net/rc-fs-nfs.tch.harvard.edu/FNNDSC-e2', '/')

    elif args.inp:
        print("Using input directory")
        input_fol=args.inp
    else:
        raise ValueError("You must specify either -pwd or -i/--input to provide an input path.")

    main(args)
