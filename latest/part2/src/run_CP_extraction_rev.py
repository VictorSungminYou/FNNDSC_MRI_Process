#=============================================================
# Title: Cortical (wm and pial) extraction pipeline
# Author: Andrea Gondova 
# Contact: andrea.gondova@childrens.harvard.edu
#==========================================================

import os , argparse, glob

#path2code='/neuro/labs/grantlab/research/andrea.gondova/Scripts/CP_surface_extraction'

def main(args):
	iSEGM=args.iSEGM
	final_outdir=args.final_outdir
	taubin_itr_CP=args.taubin_itr_CP
	subsampling=args.subsampling
	CLASP_CP_label=args.CLASP_CP_label
	stretch_wgh=args.stretch_wgh
	laplacian_wgh=args.laplacian_wgh
	lz_value=args.lz_value
	n_iteration=args.n_iteration
	convert=args.convert
	clean_up=args.clean_up
	lWM=args.lWM
	rWM=args.rWM
	
	base_path = os.path.abspath(os.path.dirname(iSEGM))
	# print(base_path)
	#outdir='tmp'
	outdir=os.path.join(base_path, 'tmp')
		
	
	print('#===== WM & PIAL mesh extraction. =====#')
	print('Working on {}'.format(iSEGM))
	print('OUT:', outdir)
	os.system('mkdir -p '+outdir) # working in tmp directory, clean up in the end
	
	#==== Step 1: Inner CP extraction ====#
	if (lWM is not None) and (rWM is not None):
		print('Using previously computed CP inner surfaces.')
		os.system('cp {} {}/lh.wm_81920.obj'.format(lWM,outdir))
		os.system('cp {} {}/rh.wm_81920.obj'.format(rWM,outdir))
		
		### relabel segmentation
		# os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/relabel_segmentation.py --iSEGM {} --oSEGM {}'.format(iSEGM, 'tmp/cp_manual_seg_5.nii'))
		os.system('python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_pipeline/part2/src/relabel_segmentation.py --iSEGM {} --oSEGM {}'.format(iSEGM, os.path.join(outdir, 'cp_manual_seg_5.nii')))
		# reset path to segmentation
		iSEGM = os.path.join(base_path, 'tmp/cp_manual_seg_5.nii')
		#iSEGM='tmp/cp_manual_seg_5.nii'
		print('Using segmentation {}'.format(iSEGM))
		
	
	else:
		for hemi in ['lh', 'rh']: #, 'rh'):
			CPinner='{}/{}.wm_81920.obj'.format(outdir,hemi) # Outer surface extraction requires file to end in _81920.obj
			print(CPinner)
			#print("*"*20)
			_extract_wm_mesh(segmentation=iSEGM, output_wm=CPinner, hemi=hemi, taubin=taubin_itr_CP, subsampling=subsampling, convert=convert)
			#os.system('rm -r {}'.format(outdir)) 
			for ending in ['obj', 'asc', 'gii']:
				os.system('mkdir -p '+final_outdir)
				os.system('cp {}/{}.wm_81920.{} {}/{}.wm.{}'.format(outdir, hemi, ending, final_outdir, hemi, ending))
	#os.system('rm -r {}'.format(outdir)) 
	#==== Step 2: CSF skeletonization + relabeling manual segmentation to CLASP ====# 
	# this required both surfaces to be present in the outdir 
	_skeletonization(outdir=outdir, segmentation=iSEGM, lz_value=lz_value, n_iteration=n_iteration)

	
	for hemi in ('lh', 'rh'):
		#==== Step 3: Laplacian field ====# 
		_laplacian(outdir=outdir, hemi=hemi, CLASP_CP_label=CLASP_CP_label, convert=convert )
	
		#==== Step 4: Outer CP surface extraction ====#
		_extract_pial_mesh(outdir=outdir, hemi=hemi, stretch_wgh=stretch_wgh, laplacian_weight=laplacian_wgh, convert=convert)
	
	#==== Step 5: Clean up ====#
	for surface in ('wm', 'pial'):
		os.system('mkdir -p '+final_outdir)
		A = glob.glob('{}/*.{}*'.format(outdir, surface))
		for file_name in A:
			#new_name = file_name.split('/')[-1].replace('_81920', '')
			os.system('cp {}/*.{}* {}/'.format(outdir, surface, final_outdir)) 
			#os.system('cp tmp/{} {}/{}'.format(file_name, final_outdir, new_name)) 
		
	if clean_up == 'yes':
		print('Cleaning up the tmp file')
		os.system('mkdir -p '+final_outdir)
		# what else to keep?
		os.system('rm -rf {}'.format(outdir))
	
def _extract_wm_mesh(segmentation, output_wm, hemi, taubin, subsampling, convert='yes'):
	if hemi== 'rh':
		WM_manual_label, side =161, 'right'	
	else:
		WM_manual_label, side =160, 'left'
	
	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/sungmin.you/SM_codes/MRI_pipeline/part2/src/1_Inner_CP_surface_v0.0.py \
			--input_seg={} \
			--output_surface={} \
			--label={} \
			--side={} \
			--taubin={} \
			--subsampling={}'.format(segmentation, output_wm, WM_manual_label, side, taubin, subsampling)
		)
		
	#compute smoothness error 
	'''
	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/smtherr.py \
			--input_surface={} \
			--output_smoother={}'.format(output_wm, output_wm.replace(".obj",".smtherr.txt"))
		)
	
	
	#compute distance error: will do this automatically within pipeline but use for outher surfaces 
	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/surfdisterr.py \
			--input_surface={} \
			--input_mask={} \
			--label={} \
			--output_disterr={}'.format(output_wm, segmentation ,WM_manual_label, output_wm.replace(".obj",".disterr.txt"))
		)
	'''
	
	if os.path.isfile(output_wm):
		print('#===== {} wm extracted =====#'.format(hemi))
		if convert == 'yes':
			os.system('mris_convert {}.asc {}.gii'.format(output_wm[:-4],output_wm[:-4]))	
	else:
		print('#===== {} wm extraction FAIL =====#'.format(hemi))
		
	#os.system('rm -r tmp')

def _skeletonization(outdir, segmentation, lz_value, n_iteration):
	surface_left='{}/{}.wm_81920.obj'.format(outdir,'lh')
	surface_right='{}/{}.wm_81920.obj'.format(outdir,'rh')
	
	if not os.path.isfile(surface_left):
		print('Left surface - ending in _81920.obj - needs to be in tmp file')
	if not os.path.isfile(surface_right):
		print('Left surface - ending in _81920.obj - needs to be in tmp file')
		
	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/2_CSF_skeletonization_iteration_v0.0.py \
			--dir={} \
			--input_seg={} \
			--lz_value={} \
			--n_iteration={} \
			--surface_left={} \
			--surface_right={}'.format(outdir, segmentation, lz_value, n_iteration, surface_left, surface_right)
		)

def _laplacian(outdir, hemi, CLASP_CP_label, convert='yes' ):
	oLaplacian='{}/laplacian_{}.mnc'.format(outdir, hemi)
	oCPinner='{}/{}.wm_81920.obj'.format(outdir, hemi)
	#oCPouter='{}/{}.pial_81920.obj'.format(outdir, hemi)
	h = 'left' if hemi == 'lh' else 'right'
	iCLASP='{}/segmentation_{}_CLASP.mnc'.format(outdir, h)
	print(iCLASP)
	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/3_Laplacian_field_v0.0.py \
			--input_seg={} \
			--output_laplacian={} \
			--CLASP_label={} \
			--inner_surface={}'.format(iCLASP, oLaplacian, CLASP_CP_label, oCPinner)
		)
	if os.path.isfile(oLaplacian):
		print('Laplacian DONE')
		if convert == 'yes':
			os.system('mnc2nii {} {}/laplacian_{}.nii'.format(oLaplacian, outdir, hemi))
	else: 
		print('Laplacian FAIL')	
		

def _extract_pial_mesh(outdir, hemi, stretch_wgh, laplacian_weight, convert='yes'):
	oLaplacian='{}/laplacian_{}.mnc'.format(outdir, hemi)
	oCPinner='{}/{}.wm_81920.obj'.format(outdir, hemi)
	oCPouter='{}/{}.pial_81920.obj'.format(outdir, hemi)

	os.system('python3 /neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/CP_surface_extraction/src/4_Outer_surface_extraction_v0.0.py \
			--laplacian_map={} \
			--inner_surface={} \
			--outer_surface={} \
			--stretch_weight={} \
			--laplacian_weight={}'.format(oLaplacian, oCPinner, oCPouter, stretch_wgh, laplacian_weight)
		)

	#=== Renaming and converting the output files ===#
	# to remove _81920.obj ending
	#os.system('cp {} {}/{}.wm.obj'.format(oCPinner, outdir, hemi)) 
	#os.system('cp {}/{}.wm_81920.asc {}/{}.wm.asc'.format( outdir, hemi, outdir, hemi)) 
	#os.system('cp {} {}/{}.pial.obj'.format(oCPouter, outdir, hemi))
	if convert == 'yes':
		os.system('/neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/surface_processing/convert_obj2gii.sh {}/{}.pial_81920.obj'.format(outdir, hemi))
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser('   ==========   Cortical surface extraction   ==========   ')
	parser.add_argument('--iSEGM', action ='store',dest='iSEGM',type=str, required=True, help='Path to the CP segmentation (5 labels)')
	parser.add_argument('--outdir', action ='store',dest='final_outdir',type=str, required=True, help='Path to folder where to save outputs')
	parser.add_argument('--taubin_itr_CP', action ='store',dest='taubin_itr_CP',type=str, default=100, help='Number of iterations for taubin smoothing')
	parser.add_argument('--subsampling', action ='store',dest='subsampling',type=str, default=True, help='Whether to subsample WM or not')
	parser.add_argument('--CLASP_CP_label', action='store',dest='CLASP_CP_label', type=str, default=2,  help='CP label in CLASP scheme')
	parser.add_argument('--stretch_wgh', action='store', dest='stretch_wgh', type=str, default=1,  help='Stretch weight for pial extraction')
	parser.add_argument('--laplacian_wgh', action='store',dest='laplacian_wgh', type=str, default=1,  help='Weight of laplacian for pial extraction')
	parser.add_argument('--lz_value', action='store',dest='lz_value', type=str, default=5, help='lz value for skeletonization')
	parser.add_argument('--n_iteration', action='store',dest='n_iteration', type=str, default=10, help='number of iterations for skeletonization')
	parser.add_argument('--convert', action='store',dest='convert', type=str, default='yes', help='convert for visualisation with freeview')
	parser.add_argument('--clean_up', action='store',dest='clean_up', type=str, default='no', help='clean up the temp files')
	parser.add_argument('--lWM', action='store',dest='lWM', type=str, default=None, help='precomputed left WM mesh')
	parser.add_argument('--rWM', action='store',dest='rWM', type=str, default=None, help='precomputed right WM mesh')
	
	args = parser.parse_args()
	print(args)	
	if os.path.exists(args.final_outdir):
		print("[Info] {} is already present".format(args.final_outdir))
		print("[Info] Clearing existing files in {}".format(args.final_outdir))
		os.system("rm -rf {}".format(args.final_outdir))
	if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(args.iSEGM)), 'tmp')):
		os.system("rm -rf {}".format(os.path.join(os.path.abspath(os.path.dirname(args.iSEGM)), 'tmp')))
	main(args)





