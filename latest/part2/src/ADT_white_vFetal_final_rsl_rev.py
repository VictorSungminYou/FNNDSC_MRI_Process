#!/usr/bin/python
# Made by Hyuk Jin
# ver 1.1.1

import os
import sys
import time

if sys.argv[1]=='-help':
        print('Usage: ADT_sub_native.py <MINC file>')
        print('autocrop : covert native to isovoxel 1mm x 1mm x 1mm')
        sys.exit(0)

native_mnc = sys.argv[1]
os.system('mkdir '+native_mnc+'/ADT_rsl/')
native_l = native_mnc+'/ADT_rsl/lh.smoothwm.native.mask.mnc'
native_r = native_mnc+'/ADT_rsl/rh.smoothwm.native.mask.mnc'

native_scan_l = native_mnc+'/ADT_rsl/lh.smoothwm.native.scan.mnc'
native_scan_r = native_mnc+'/ADT_rsl/rh.smoothwm.native.scan.mnc'

depth_l = native_mnc+'/lh.smoothwm.native_81920.rsl.depth'
depth_r = native_mnc+'/rh.smoothwm.native_81920.rsl.depth'

surf_l_coord = native_mnc+'/ADT_rsl/lh.smoothwm.native.coord.rsl.obj'
surf_r_coord = native_mnc+'/ADT_rsl/rh.smoothwm.native.coord.rsl.obj'
surf_l = native_mnc+'/lh.smoothwm.native_81920.rsl.obj'
surf_r = native_mnc+'/rh.smoothwm.native_81920.rsl.obj'

os.system('surface_volume_coordinates '+surf_l+' /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/quarantines/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_l_coord)
os.system('surface_volume_coordinates '+surf_r+' /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/quarantines/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_r_coord)

os.system('scan_object_to_volume /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_l+' '+native_scan_l)
os.system('scan_object_to_volume /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_r+' '+native_scan_r)

os.system('surface_mask2 -binary_mask /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_l+' '+native_l)
os.system('surface_mask2 -binary_mask /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/Linux-x86_64/share/ICBM/icbm_nlin_template_1.00mm.mnc '+surf_r+' '+native_r)

# closing
os.system('mincmorph -clobber -close '+native_l+' '+native_l[:-4]+'.temp.mnc')
os.system('mincmorph -clobber -close '+native_r+' '+native_r[:-4]+'.temp.mnc')

os.system('mincchamfer '+native_l[:-4]+'.temp.mnc '+native_l[:-4]+'.chf.mnc')
os.system('mincchamfer '+native_r[:-4]+'.temp.mnc '+native_r[:-4]+'.chf.mnc')

os.system('mincmath -clobber -ge -const 10 '+native_l[:-4]+'.chf.mnc '+native_l[:-4]+'.chf10.mnc')
os.system('mincmath -clobber -ge -const 10 '+native_r[:-4]+'.chf.mnc '+native_r[:-4]+'.chf10.mnc')

os.system('mincchamfer '+native_l[:-4]+'.chf10.mnc '+native_l[:-4]+'.chf10chf.mnc')
os.system('mincchamfer '+native_r[:-4]+'.chf10.mnc '+native_r[:-4]+'.chf10chf.mnc')

os.system('mincmath -clobber -ge -const 10 '+native_l[:-4]+'.chf10chf.mnc '+native_l[:-4]+'.closing.mnc')
os.system('mincmath -clobber -ge -const 10 '+native_r[:-4]+'.chf10chf.mnc '+native_r[:-4]+'.closing.mnc')

os.system('mincmorph -clobber -dilation '+native_l[:-4]+'.closing.mnc '+native_l[:-4]+'.closing_dil.mnc')
os.system('mincmorph -clobber -dilation '+native_r[:-4]+'.closing.mnc '+native_r[:-4]+'.closing_dil.mnc')

os.system('mincmath -clobber -sub '+native_l[:-4]+'.closing_dil.mnc '+native_l[:-4]+'.closing.mnc '+native_l[:-4]+'.closing_LoG.mnc')
os.system('mincmath -clobber -sub '+native_r[:-4]+'.closing_dil.mnc '+native_r[:-4]+'.closing.mnc '+native_r[:-4]+'.closing_LoG.mnc')

co_l = native_l[:-4]+'.local_coord'
co_r = native_r[:-4]+'.local_coord'
Log_l = native_l[:-4]+'.closing_LoG'
Log_r = native_r[:-4]+'.closing_LoG'

# Local Coordinate
os.system('minccalc -clobber -expr "if((A[0]>0 && A[1]>0) || (A[0]+A[1])==0){out = 0;} else {out=1;}" '+native_l+' '+native_l[:-4]+'.closing.mnc '+native_l[:-4]+'.xor.mnc')
os.system('minccalc -clobber -expr "if((A[0]>0 && A[1]>0) || (A[0]+A[1])==0){out = 0;} else {out=1;}" '+native_r+' '+native_r[:-4]+'.closing.mnc '+native_r[:-4]+'.xor.mnc')

os.system('minccalc -clobber -expr "if(A[0]>0 || A[1]>0){out = 1;} else {out=0;}" '+native_l[:-4]+'.xor.mnc '+native_scan_l+' '+co_l+'.mnc')
os.system('minccalc -clobber -expr "if(A[0]>0 || A[1]>0){out = 1;} else {out=0;}" '+native_r[:-4]+'.xor.mnc '+native_scan_r+' '+co_r+'.mnc')

os.system('mincdefrag '+native_l[:-4]+'.xor.mnc '+native_l[:-4]+'.xor_defrag.mnc 1 19')
os.system('mincdefrag '+native_r[:-4]+'.xor.mnc '+native_r[:-4]+'.xor_defrag.mnc 1 19')

os.system('mnc2nii -analyze -short '+co_l+'.mnc '+co_l+'.hdr')
os.system('mnc2nii -analyze -short '+co_r+'.mnc '+co_r+'.hdr')

os.system('mnc2nii -analyze -short '+Log_l+'.mnc '+Log_l+'.hdr')
os.system('mnc2nii -analyze -short '+Log_r+'.mnc '+Log_r+'.hdr')

# ADT
os.system(' /neuro/labs/grantlab/research/HyukJin_MRI/code/ADT/ADT_subvoxel_final3 '+co_l+' '+Log_l+' '+surf_l_coord+' '+depth_l)
os.system(' /neuro/labs/grantlab/research/HyukJin_MRI/code/ADT/ADT_subvoxel_final3 '+co_r+' '+Log_r+' '+surf_r_coord+' '+depth_r)
#os.system(' ~/Codes/ADT_final_v01 '+co_l+' '+Log_l+' '+surf_r_coord+' '+depth_l)
#os.system(' ~/Codes/ADT_final_v01 '+co_r+' '+Log_r+' '+surf_l_coord+' '+depth_r)

