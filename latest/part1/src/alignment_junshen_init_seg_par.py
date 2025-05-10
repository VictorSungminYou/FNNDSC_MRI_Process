#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 10:30:31 2020

@author: maria.hernandez
"""

##for resolution change
## recon resolution: 0.5

import os
import sys
import math
import glob
import nibabel as nib
import numpy as np
import csv
from numpy import zeros
import concurrent.futures
import subprocess

file = sys.argv[1]  ##>> subj folder +recon folder ;; destination path ? 


alignment_temp = file+'/alignment_temp'

try:
	os.mkdir (file+'/alignment_temp')
except FileExistsError:
	print("folder already made")

os.system('cp '+file+'/recon_to31init_nuc_mask.nii '+alignment_temp+'/recon.nii')
os.system('cp '+file+'/recon_to31init_nuc.nii '+alignment_temp+'/recon_nuc.nii')

def apply_flirt_transformation(_t):
    ''' Apply the flirt command to each element in the a_temp tuple using parallel computing '''
    
    flirt_command1 = [
        'flirt', 
        '-in', f'/neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-{_t}/brain-{_t}.nii',
        '-ref', f'{alignment_temp}/recon.nii',
        '-out', f'{alignment_temp}/Temp-Recon-7dof-{_t}.nii',
        '-omat', f'{alignment_temp}/Temp-Recon-7dof-{_t}.xfm'
    ]

    flirt_command2 = [
        'flirt',
        '-in', f'/neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-{_t}/csf-{_t}.nii',
        '-ref', f'{alignment_temp}/recon.nii',
        '-out', f'{alignment_temp}/csf-aligned{_t}.nii',
        '-init', f'{alignment_temp}/Temp-Recon-7dof-{_t}.xfm',
        '-applyxfm'
    ]

    subprocess.run(flirt_command1, check=True)
    subprocess.run(flirt_command2, check=True)
    print(f"[Info] Under parallel processing: Alignment onto {_t} week template done")

a_temp=("23", "24", "25", "26", "27", "28", "29", "30", "31")

def execute_flirt_parallel():
    ''' Uses parallel computing to apply transformation to the data on multiple cpu cores'''
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(apply_flirt_transformation,a_temp)

execute_flirt_parallel()

#for t in a_temp:
#	os.system(\
#		'flirt -in /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-'+t+'/brain-'+t+'.nii -ref '+alignment_temp+'/recon.nii \
#		-out '+alignment_temp+'/Temp-Recon-7dof-'+t+'.nii -omat '+alignment_temp+'/Temp-Recon-7dof-'+t+'.xfm -dof 7 ;')
#	os.system('flirt -in /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-'+t+'/csf-'+t+'.nii -ref '+alignment_temp+'/recon.nii \
#		-out '+alignment_temp+'/csf-aligned'+t+'.nii -init '+alignment_temp+'/Temp-Recon-7dof-'+t+'.xfm -applyxfm;')

# recon = nib.load('recon_highres.nii') # Load reconstruction image 
recon = nib.load(alignment_temp+'/recon_nuc.nii')
size=recon.get_fdata().shape # Get the dimensions of the volume 

meas = [0,0,0]
beginning=[0,0,0]

for i in range (0, 3):
	beginning[i]=int(round(size[i]/10.0))
	temp=size[i]-beginning[i]
	meas[i]=temp-beginning[i]
	
	if (i==0):
		dimensions=zeros([size[1],size[2]])
		coronal= dict.fromkeys(range(0, meas[i]),dimensions)
	if (i==1):
		dimensions=zeros([size[0],size[2]])
		sagital= dict.fromkeys(range(0, meas[i]),dimensions)
	if (i==2):
		dimensions=zeros([size[0],size[1]])
		axial= dict.fromkeys(range(0, meas[i]),dimensions)

ccl= meas[0]+meas[1]+meas[2]

im = {'corrcoef':zeros([1,ccl*10]), 'greatest':zeros([1,ccl]), 'template':zeros([1,ccl])}

for i in range (0, meas[0]): #Gets the number of slides choosen
	a= beginning[0]+i #Starts in the slide selected as beginning and ends passing the one selected as end
	coronal[i]=np.uint8(np.squeeze(recon.get_fdata()[a,:,:])/4)  #Get the slide of the reconstruction image.

for i in range (0, meas[1]):	
	a= beginning[1]+i #Starts in the slide selected as beginning and ends passing the one selected as end
	sagital[i]=np.uint8(np.squeeze(recon.get_fdata()[:,a,:])/4)  #Get the slide of the reconstruction image.

for i in range (0, meas[2]):	
	a= beginning[2]+i #Starts in the slide selected as beginning and ends passing the one selected as end
	axial[i]=np.uint8(np.squeeze(recon.get_fdata()[:,:,a])/4)  #alignment_tempGet the slide of the reconstruction image.
			
number=22 #Stablishes the base to number the templates

def mean2(value):
	mean2value=np.sum(value)/np.size(value)
	return mean2value

def corr2(R, T):
	R=R-mean2(R)
	T=T-mean2(T)
	corr=((R*T).sum())/(math.sqrt((R*R).sum()*(T*T).sum()))
	return corr

for i in range (0,9): #Says that the process will repeat for the 9 templates
	number=number+1 #The first template will be 23
	volume=alignment_temp+'/csf-aligned%d.nii.gz' %number #Construct the name of the template volume that will be loaded
	volume=nib.load(volume) #Load the template volume
	meascor=(meas[0]*i)
	meassag=(meas[1]*i)+(meas[0]*9)
	measax=(meas[2]*i)+(meas[0]*9)+(meas[1]*9)
	
	for j in range (0,ccl):
		if (j<meas[0]):
			t=meascor+j #Define the position in which the results will be stored\
			a=beginning[0]+j; #Select the slide that will be taken
			slide=volume.get_fdata()[a,:,:] #Loads the slide
			
		if (j>=meas[0] and j<(meas[0]+meas[1])):
			t=meassag+j #Define the position in which the results will be stored\
			a=beginning[0]+j-meas[0]; #Select the slide that will be taken
			slide=volume.get_fdata()[:,a,:] #Loads the slide
		
		if (j>=(meas[0]+meas[1])):
			t=measax+j #Define the position in which the results will be stored\
			a=beginning[0]+j-meas[0]-meas[1]; #Select the slide that will be taken
			slide=volume.get_fdata()[:,:,a] #Loads the slide	
			
	#normalize the slide
		slide=np.uint8(256*(slide-slide.min())/(slide.max()-slide.min()))
	
		index=np.nonzero(slide) #get the positions of the non zero values 
		csfi=slide[np.nonzero(slide)] #get the values of the no zero values
	
		temp=csfi.shape #gets the number of non zero values 
		temp=temp[0]
		reconi=[]
		
		if (j<meas[0]):
			for n in range (0,temp): #get the same indexes of the recon image
				slide=coronal[j].item(index[0][n],index[1][n])
				reconi.append(slide)
						
		if (j>=meas[0] and j<(meas[0]+meas[1])):
			for n in range (0,temp): #get the same indexes of the recon image
				jj=j-meas[0]
				slide=sagital[jj].item(index[0][n],index[1][n])
				reconi.append(slide)
				
		if (j>=(meas[0]+meas[1])):
			for n in range (0,temp): #get the same indexes of the recon image
				jj=j-meas[0]-meas[1]
				slide=axial[jj].item(index[0][n],index[1][n])
				reconi.append(slide)
				
		im['corrcoef'][0,t]=corr2(reconi, csfi)
	
	a=0
		
for a in range (0,ccl):
	im['greatest'][0,a]=-5
		
	for i in range (0,9):
		if (a<meas[0]):
			j=(meas[0]*i)+a
							
		if (a>=meas[0] and a<(meas[1]+meas[0]) ):
			j=(meas[1]*i)+(meas[0]*9)+a
			
		if (a>=(meas[1]+meas[0])):	
			j=(meas[2]*i)+(meas[0]*9)+(meas[1]*9)+a			
			
		if im['corrcoef'][0,j]>im['greatest'][0,a]:
			im['greatest'][0,a]=im['corrcoef'][0,j]
			im['template'][0,a]=i+23

t=im['template']
t=t[0]
a=t.tolist()
j=im['greatest']
jj=max(j[0])-((max(j[0]))/2.5)

for i in range (0,ccl):
	if (j[0][i]>jj):
		a.append(im['template'][0,i])

n=np.histogram(t,bins=[23,24,25,26,27,28,29,30,31])
temp=np.argsort(n[0])[::-1]	
tempi=temp+23
temp=str(tempi[0])

# os.environ['temp']=str(temp)

os.system('convert_xfm -omat '+alignment_temp+'/InvAligned-'+temp+'.xfm -inverse '+alignment_temp+'/Temp-Recon-7dof-'+temp+'.xfm')
os.system('convert_xfm -omat '+alignment_temp+'/recon_nuc_temp.xfm -concat /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-'+temp+'/template-'+temp+'to31.xfm '+alignment_temp+'/InvAligned-'+temp+'.xfm')
os.system('convert_xfm -omat '+alignment_temp+'/recon_to31.xfm -concat '+alignment_temp+'/../recon_to31init.xfm '+alignment_temp+'/recon_nuc_temp.xfm')

os.system('flirt -in '+alignment_temp+'/../recon.nii -ref /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-31/template-31.nii \
			-out '+alignment_temp+'/recon_to31.nii -init '+alignment_temp+'/recon_to31.xfm -applyxfm')

os.system('gunzip '+alignment_temp+'/recon_to31.nii.gz')

os.system('cp '+file+'/alignment_temp/recon_to31.* '+file)

os.system('convert_xfm -omat '+alignment_temp+'/recon_to31_inv.xfm -inverse '+alignment_temp+'/recon_to31.xfm;')
os.system('echo `avscale '+alignment_temp+'/recon_to31_inv.xfm | grep Scales` > '+alignment_temp+'/temp.txt;')
scales=open(alignment_temp+'/temp.txt', encoding='utf-8')
scales=scales.read()
os.system('param2xfm -clobber -scales '+scales[16:-1]+' '+alignment_temp+'/recon_native.xfm;')

os.system('cp '+file+'/alignment_temp/recon_native.xfm '+file)
