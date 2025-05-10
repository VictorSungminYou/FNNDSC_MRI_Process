import pandas as pd
import os, argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser('   ==========   Cortical surface extraction   ==========   ')
	parser.add_argument('--subjects', action ='store',dest='subjects',type=str, required=True, help='Path to .csv file with subjects')
	#parser.add_argument('--taubin_itr_CP', action ='store',dest='taubin_itr_CP',type=str, default=100, help='Number of iterations for taubin smoothing')
	#parser.add_argument('--CLASP_CP_label', action='store',dest='CLASP_CP_label', type=str, default=2,  help='CP label in CLASP scheme')
	#parser.add_argument('--stretch_wgh', action='store', dest='stretch_wgh', type=str, default=1,  help='Stretch weight for pial extraction')
	#parser.add_argument('--laplacian_wgh', action='store',dest='laplacian_wgh', type=str, default=1,  help='Weight of laplacian for pial extraction')
	#parser.add_argument('--lz_value', action='store',dest='lz_value', type=str, default=5, help='lz value for skeletonization')
	#parser.add_argument('--n_iteration', action='store',dest='n_iteration', type=str, default=10, help='number of iterations for skeletonization')
	#parser.add_argument('--convert', action='store',dest='convert', type=str, default='yes', help='convert for visualisation with freeview')
	#parser.add_argument('--clean_up', action='store',dest='clean_up', type=str, default='no', help='clean up the temp files')
	
	args = parser.parse_args()
	
	print('HERE: ',os.getcwd())	
	
	subjects=pd.read_csv(args.subjects)
	for i, row in subjects.iterrows():	
		print(row.subject_id, row.session_id)
		
		iSEGM='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/segmentations/{}_{}_cp_manual_seg_5.nii'.format(
			row.subject_id, row.session_id,
			row.subject_id, row.session_id
		)
		oDIR='/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/optimisation'.format(
			row.subject_id, row.session_id,
		)
		
		#print(iSEGM)
		#print(oDIR)
		#====== OPTIMIZING TAUBIN ======#
		taubin = [0,50,100,150,200]
		for taubin_value in taubin:	
			print('Taubin value: ', taubin_value)
		#	os.system('mkdir -p '+ oDIR)
			for hemi in ['lh', 'rh']:
				iWM = '/neuro/labs/grantlab/users/andrea.gondova/Projects/DerivedData/subjects/{}/{}/optimisation/{}.wm_81920.obj'.format(
			row.subject_id, row.session_id, hemi)
				
				os.system('adapt_object_mesh {} {}/{}.wm_81920_adapted.obj 0 {} 0 0;'.format(iWM, oDIR, hemi, taubin_value))
				#print('{}/taubin_{}_{}.wm_81920.obj'.format(oDIR, taubin_value, hemi))
				os.system('mv {}/{}.wm_81920_adapted.obj {}/taubin_{}_{}.wm_81920.obj'.format(oDIR, hemi,oDIR, taubin_value, hemi))		
				os.system('/neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/processing/convert_obj2gii.sh {}/taubin_{}_{}.wm_81920.obj'.format(oDIR, taubin_value, hemi))
				
				# compute smoothness error
				os.system('python src/smtherr.py -s {} -o {}/taubin_{}_{}.wm_81920.smtherr.txt'.format(iWM, oDIR, taubin_value, hemi))
				if hemi == 'lh':
					label=160
				else:
					label=161
				os.system('python src/surfdisterr.py -s {} -m {} -l {} -o {}/taubin_{}_{}.wm_81920.disterr.txt'.format(iWM, iSEGM, label, oDIR, taubin_value, hemi))	
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
