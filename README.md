Fetal MRI processing pipeline API document(2024)

Environment setup (stable)
source /latest/init_stable_env.sh
Use the above command until libraries are stabilized.


All-in-one Scripts
Part1 (brain masking to segmentation)
python3 /latest/part1/main.py --input ${file} --all
Input arguments:
--input: Path for data to be processed 

Part2 (Surface extraction)
python3 /latest/part2/main.py --iSEGM ${file}/recon_segmentation/segmentation_to31_final.nii --outdir ${file}/surfaces
Input arguments:
--iSEGM: Path to the CP segmentation (5 labels)
--outdir: Path to folder where to save outputs
--inner_only: flag to perform inner CP surface extraction only
[Optional] Part2 (with Parallel computing): wrapper to run multiple cases in parallel
Usage: python3 /latest/part2/main_parallel.py path1 path2 …
It will run Part2 script for each path in parallel considering CPU capacity and sequentially.


Module API description
[input]: command arguments directly related to inputs of functions
[output]: command arguments related to outputs from functions
[option]: others (parameters, flags, etc)

Brain Masking
Command: 
python3 /latest/part1/src/masking.py
Input arguments:
--input_folder: 		[input] Input folder name (a.k.a ${file})
--masks_folder: 	[output] Folder to store the masks created (default=masks)
--brains_folder: 	[output] Folder to store extracted brains (default=brain)
--remask: 	[option] Flag for remasking. If given, skip brain masking and apply masking with existing masks at masks_folder

Non-Uniformity Correction(NUC)
Command: 
python3 /latest/part1/src/nuc.py
Input arguments:
--input_folder: 	[input] Input folder name (a.k.a ${file}) 
--brains_folder: 	[option] Folder name for where extracted brains are (default=brain)
--nuc_folder: 	[output] Folder to store NUC applied brains (default=nuc)

Quality Assessment
Command: 
python3 /latest/part1/src/qa.py
Input arguments:
--input_folder: 	[input] Input folder name (It should include the exact full path including the subfolder, such as ${file}/nuc)
--output_file:	[output] Output filename (default='quality_assessment.csv')

Reconstruction (NesVor)
Command: 
python3 /latest/part1/src/reconstruction.py
Input arguments:
--input_folder:	[input] Input folder name (a.k.a ${file}) 
--output_file:  	[output] Name for the reconstruction file (default=recon.nii)
--threshold: 	[option] Threshold for files from QA (default=0.4)
--qa_file: 	[input] Name for the file where quality assessment is stored (default=quality_assesment.csv)
--res: 		[option] Output resolution of reconstruction (default=0.5)
--thickness: 	[option] (Nesvor parameter) Slice thickness of each input stack. If not provided, use the slice gap of the input stack (default). If only a single number is provided, assume all input stacks have the same thickness.
--gpu: 		[option] GPU ID number to run (default=”0”)

Alignment
Command: 
python3 /latest/part1/src/alignment.py
Input arguments:
--input_file: 	[input] Input volume filename 
--output_file: 	[output] Output volume filename (default=recon_to31.nii)
--FLIRT_options: 	[option] Option for FLIRT function (default= “-dof 7”)

Two-step Alignment (script)
Command: 
python3 /latest/part1/src/alignment_TwoStep.py
Input arguments:
--input_fol: 	[input] Input folder name (a.k.a ${file})



Post(alignment) NUC
Command: 
python3 /latest/part1/src/post_nuc.py
Input arguments:
--input_file: 	[input] Input volume filename 
--output_file: 	[output] Output volume filename (default=recon_to31_nuc.nii)


(CP) Segmentation
Command: 
python3 /latest/part1/src/segmentation.py
Input arguments:
--input_MR: 	[input] Input file name 


Volume measurement
Command: python3 /latest/part1/src/Volume_measures_v0.0.py
Input arguments:
--input_segmentation: 	[input] Input segmentation file name
--recon_native_xfm:		[input] Corresponding recon_native_xfm file
Note:
It will measure tissue volumes and save them in Volume_measures.txt, found in recon_segmentation/. Contains left/right CP volumes, left/right inner volumes of CP. The order of the output text file: left inner volume, right inner volume, left CP volume, and right CP volume.


Inner CP extraction
Command: python3 /latest/part2/src/1_Inner_CP_surface_v0.0.py
Input arguments:
--input_seg: 	[input] Segmentation volume
--output_surface:	[output] Inner surface output filename
--label: 	[option] Segmentation label for surface extraction
--side: 		[option] Hemisphere side
--taubin: 	[option] Global iteration of taubin smoothing (default = 100)
--subsampling:[option] Whether to subsample WM or not (default = True)

CSF skeletonization
Command: python3 /latest/part2/src/2_CSF_skeletonization_iteration_v0.0.py
Input arguments:
--input_seg: 	[input] Initial segmentation file
--surface_left: 	[input] Left inner surface filename
--surface_right:	[input] Right inner surface filename
--dir: 		[output] Path for skeleton output
--lz_value: 	[option] LZ value for skeletonization (default = 5)
--n_iteration: 	[option] Number of iteration (default = 10)


Laplacian map
Command: python3 /latest/part2/src/3_Laplacian_field_v0.0.py
Input arguments:
--input_seg: 	[input] CLASP segmentation file (*.mnc)
--inner_surface: 	[input] Inner surface
--output_laplacian: 	[output] Laplacian map output file
--CLASP_label:	[option] CLASP Label for CP (default = 2)
--inner_surface: 	[input] Inner surface


Outer surface extraction
Command: python3 /latest/part2/src/4_Outer_surface_extraction_v0.0.py
Input arguments:
--laplacian_map: 	[input] Laplacian map
--inner_surface: 	[input] Inner surface (should contain suffix _81920.obj)
--outer_surface: 	[output] Outer surface
--stretch_weight:	[option] Stretch weight for outer surface deformation (default = 1)
--laplacian_weight: 	[option] Laplacian weight for outer surface deformation
Note
If the outer surface output and inner surface output look the same, it means failure during the outer surface extraction. Check the self-intersection log and revise the segmentation map.

Surface registration
Command: python3 /latest/part2/src/5_Surface_registration_v0.0.py
Input arguments:
--input_surf: 	[input] Input surface
--target_surf: 	[input] Target surface
--output_surf: 	[output] Resampled surface
--output_sm:	[option] Resampling file
--options: 	[option] Option for bestsurfreg.pl (default = -clobber -min_control_mesh 80 -max_control_mesh 81920 -blur_coef 1.25 -neighbourhood_radius 2.8 -maximum_blur 1.9)

Surface measurement (original)
Command: python3 /latest/part2/src/Surface_measures_original_v0.0.py
Input arguments:
--input_fol: 	[input] Input folder name (a.k.a ${file})


Surface measurement (resampled on templates)
Command: python3 /latest/part2/src/Surface_measures_resampled_v0.0.py
Input arguments:
--input_fol: 	[input] Input folder name (a.k.a ${file})
Note:
It calculates surface area, sulcal depth, and mean curvature. Whole brain measures (left/right area, left/right depth, left/right absolute mean curvature) will be saved as Area_Depth_aMC.rsl.s5.txt, inside surfaces/.  
The order of the output text file: left surface area, right surface area, left sulcal depth, right sulcal depth, left absolute mean curvature, and right absolute mean curvature.

Automatic Surface Parcellation (using spherical Unet): stable over 27 GW
Command: python3 /latest/part2/src/automatic_parcellation.py --input_path $file/surfaces/
Input arguments:
--input_path: 	[input] Path for the directory where MNI surfaces are (*h.smoothwm.mni.obj)
Outputs:	*h.parcel.dset (Parcellation label maps)



Update note
Jan 8, 2025	
Revised Surface_measures_original_v0.1.py	Revised spacing issues in “Volume_measures.txt” and “GI_info_final.txt”

Jan 10, 2025
Added Volume_measures_v0.0.py	Volume measurements are moved to part1
Revised part1/main.py		Flag options are added. 
After brain masking, “verify” folder is created under ${file}, which contains images of raw brains.
Revised part1/src/qa.py 		
After QA, “Best_Image_crop” folder is created under ${file}, which contains images of volumes over the threshold(0.4).

Jan 13, 2025
Added automatic_parcellation.py	Perform automatic parcellation using Spherical U-net. https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2024.1410936/full 

Jan 31, 2025
Revised part2/main.py		Added “--inner_only” flag option
