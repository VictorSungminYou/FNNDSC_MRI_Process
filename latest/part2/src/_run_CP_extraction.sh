#!/bin/bash
which python
# requires mri_team environment and fetachallenge conda (for python)
# . /neuro/users/mri.team/packages/env_MRI_team;
# add subject_id and session_id to name

convert_for_visualisation=yes
clean_up=no

#=== parameters ===#
#inner CP
taubin_itr_CP=100
#outer CP
CLASP_CP_label=2
stretch_wgh=1
laplacian_wgh=1
# skeletonization
lz_value=5
n_iteration=10
#=======#

#outdir='tmp'
#iSEGM=test_5labels_FCB145.nii

echo 'CP inner/outer extraction...'
echo 'Working on: ' ${iSEGM}
mkdir -p ${outdir}


#for hemi in lh rh; 
#do

#	if [[ "$hemi" == "rh" ]]; then
#		WM_manual_label=161
#		side=right
#	else
#		WM_manual_label=160
#		side=left
#	fi
	
#	echo Working on $hemi...
	
	#==== Step 1: Inner CP extraction ====#
#	oCPinner=${outdir}/$hemi.wm_81920.obj # Outer surface extraction requires file to end in _81920.obj
	
#	echo ${oCPinner}
#	echo ${WM_manual_label}
	
#	python 1_Inner_CP_surface_v0.0.py --input_seg=${iSEGM} --output_surface=${oCPinner} --label=${WM_manual_label} --side=${side} --taubin=${taubin_itr_CP}
	
#	if [[ "$convert_for_visualisation" == 'yes' ]]; then
#		mris_convert ${outdir}/${hemi}.wm_81920.asc ${outdir}/${hemi}.wm.gii	
#	fi
#done 

#==== Step 2: CSF skeletonization + relabeling manual segmentation to CLASP ====# 
# this requires both surfaces
#surface_left=${outdir}/lh.wm_81920.obj
#surface_right=${outdir}/rh.wm_81920.obj

#python 2_CSF_skeletonization_iteration_v0.0.py --dir=${outdir} --input_seg=${iSEGM} --lz_value=${lz_value} --n_iteration=${n_iteration} --surface_left=${surface_left} --surface_right=${surface_right}

for hemi in lh rh; 
do
	if [[ "$hemi" == "rh" ]]; then
		iCLASP=${outdir}/segmentation_right_CLASP.mnc
	else
		iCLASP=${outdir}/segmentation_left_CLASP.mnc
	fi

	#==== Step 3: Laplacian field ====# 
	oLaplacian=${outdir}/laplacian_${hemi}.mnc
	oCPinner=${outdir}/$hemi.wm_81920.obj
	oCPouter=${outdir}/$hemi.pial_81920.obj
	
	#python 3_Laplacian_field_v0.0.py --input_seg=${iCLASP} --output_laplacian=${oLaplacian} --CLASP_label=${CLASP_CP_label} --inner_surface=${oCPinner}
	
	#if [[ "$convert_for_visualisation" == 'yes' ]]; then
#		mnc2nii ${oLaplacian} ${outdir}/laplacian_${hemi}.nii	
#	fi
	
	#==== Step 4: Outer CP surface extraction ====# 
	echo ${stretch_wgh}
	echo ${laplacian_wgh}
	which python 
	
	python 4_Outer_surface_extraction_v0.0.py --laplacian_map=${oLaplacian} --inner_surface=${oCPinner} --outer_surface=${oCPouter} --stretch_weight=${stretch_wgh} --laplacian_weight=${laplacian_wgh}
	
	#=== Renaming and converting the output files ===#
	# to remove _81920.obj ending
	
	mv ${oCPinner} ${outdir}/${hemi}.wm.obj
	mv ${outdir}/${hemi}.wm_81920.asc ${outdir}/${hemi}.wm.asc
	mv ${oCPouter} ${outdir}/${hemi}.pial.obj
	
	# convert pial.obj to .asc and .gii
	/neuro/labs/grantlab/research/MRI_processing/andrea.gondova/Scripts/CP_SP_coevolution/processing/convert_obj2gii.sh ${outdir}/${hemi}.pial.obj
		  
done
#if [[ "$clean_up" == 'yes' ]]; then
#	rm tmp_extraction* 	
#fi

