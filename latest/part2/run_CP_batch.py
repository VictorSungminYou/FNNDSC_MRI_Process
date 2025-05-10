#!. /neuro/users/mri.team/packages/env_MRI_team

#=============================================================
# Title: Cortical Surface extraction over a batch of subjects
# Author: Andrea Gondova 
# Contact: andrea.gondova@childrens.harvard.edu
# Comment: For now runs for subjects that have manual CP segmentation, in theory should run also for CP extraction from SP-based model,
# but this would require some relabelling
# Comment - expects subjects.csv that contains columns subject_id, session_id, and GA
#=============================================================

import pandas as pd
import os, argparse, glob

## PARAMETERS:
#convert='yes'
#clean_up='no'
#=== parameters ===#
#inner CP
#taubin_itr_CP=100
#outer CP
#CLASP_CP_label=2
#stretch_wgh=1
#laplacian_wgh=1
# skeletonization
#lz_value=5
#n_iteration=10

## optimizing parameters?
taubin=[0,50,100,150,200]

if __name__ == '__main__':
	parser = argparse.ArgumentParser('   ==========   Cortical surface extraction   ==========   ')
	parser.add_argument('--subjects', action ='store',dest='subjects',type=str, required=True, help='Path to .csv file with subjects')
	parser.add_argument('--taubin_itr_CP', action ='store',dest='taubin_itr_CP',type=str, default=100, help='Number of iterations for taubin smoothing')
	parser.add_argument('--CLASP_CP_label', action='store',dest='CLASP_CP_label', type=str, default=2,  help='CP label in CLASP scheme')
	parser.add_argument('--stretch_wgh', action='store', dest='stretch_wgh', type=str, default=1,  help='Stretch weight for pial extraction')
	parser.add_argument('--laplacian_wgh', action='store',dest='laplacian_wgh', type=str, default=1,  help='Weight of laplacian for pial extraction')
	parser.add_argument('--lz_value', action='store',dest='lz_value', type=str, default=5, help='lz value for skeletonization')
	parser.add_argument('--n_iteration', action='store',dest='n_iteration', type=str, default=10, help='number of iterations for skeletonization')
	parser.add_argument('--convert', action='store',dest='convert', type=str, default='yes', help='convert for visualisation with freeview')
	parser.add_argument('--clean_up', action='store',dest='clean_up', type=str, default='no', help='clean up the temp files')
	parser.add_argument('--log', action='store',dest='log', type=str, default='yes', help='Keep track of subjects that were finished')
	parser.add_argument('--previous_CP', action='store',dest='previous_CP', type=str, default='no', help='Turn yes if want to use previously computed CP')
	
	args = parser.parse_args()
	
	print('HERE: ',os.getcwd())	
	
	subjects=pd.read_csv(args.subjects)
	for i, row in subjects.iterrows():	
		print(row.subject_id, row.session_id)
		
		iSEGM='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/segmentations/{}_{}_cp_manual_seg_5_ag.nii'.format(
			row.subject_id, row.session_id,
			row.subject_id, row.session_id
		)
		#oDIR='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/surfaces_auto'.format(
		#		row.subject_id, row.session_id,
		#)
		oDIR='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/default_surfaces'.format(
			row.subject_id, row.session_id,
		)
		
		print('Pipeline will save new surfaces to {}'.format(oDIR))
		if row.GA < 28.5:
			subsampling=False
		else:
			subsampling=True
		
		if args.previous_CP == 'yes':
			iSEGM=iSEGM='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/segmentations/{}_{}_nuc_deep_subplate_dilate.nii'.format(
			row.subject_id, row.session_id,
			row.subject_id, row.session_id
		)

			lWM = os.path.join(oDIR, 'lh.wm.obj' )
			rWM = os.path.join(oDIR, 'rh.wm.obj')
			os.system('python3 src/run_CP_extraction.py \
				--iSEGM {} \
				--outdir {} \
				--taubin_itr_CP {} \
				--subsampling {} \
				--CLASP_CP_label {} \
				--stretch_wgh {} \
				--laplacian_wgh {} \
				--lz_value {} \
				--n_iteration {} \
				--convert {} \
				--clean_up {} \
				--lWM {} \
				--rWM {} \
				'.format(iSEGM, oDIR, 
					args.taubin_itr_CP, subsampling, args.CLASP_CP_label, 
					args.stretch_wgh, args.laplacian_wgh, 
					args.lz_value, args.n_iteration, 
					args.convert, args.clean_up,
					lWM, rWM))	
			
		
		else:
			os.system('python3 src/run_CP_extraction.py \
				--iSEGM {} \
				--outdir {} \
				--taubin_itr_CP {} \
				--subsampling {} \
				--CLASP_CP_label {} \
				--stretch_wgh {} \
				--laplacian_wgh {} \
				--lz_value {} \
				--n_iteration {} \
				--convert {} \
				--clean_up {} \
				'.format(iSEGM, oDIR, 
					args.taubin_itr_CP, subsampling,
					args.CLASP_CP_label, 
					args.stretch_wgh, args.laplacian_wgh, 
					args.lz_value, args.n_iteration, 
					args.convert, args.clean_up ))	
								
		if args.log == 'yes':
			A = glob.glob('{}/*.obj'.format(oDIR))
			B = ['{}/lh.pial_81920.obj'.format(oDIR), '{}/lh.wm_81920.obj'.format(oDIR), '{}/rh.pial_81920.obj'.format(oDIR), '{}/rh.wm_81920.obj'.format(oDIR)]
			with open('log.txt', 'a') as the_file:
				if set(B).issubset(set(A)):
					the_file.write('{},{},finished\n'.format(row.subject_id, row.session_id))
				else:
					the_file.write('{},{},failed\n'.format(row.subject_id, row.session_id))
			
			
# python run_CP_batch.py --subjects manualCP_batch.csv
# python run_CP_batch.py --subjects --previous yes manualSP_noCP_batch.csv
#python run_CP_batch.py --subjects test.csv --previous_CP yes


