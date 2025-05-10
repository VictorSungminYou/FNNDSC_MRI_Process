''' Alignment '''
import os
import argparse
import math
import concurrent.futures
import subprocess
import nibabel as nib
import numpy as np
from numpy import zeros

from helper_functions import timeit_decorator,get_parent_path, create_folder

parser = argparse.ArgumentParser('=== Fetal alignment script for fetal pipeline ===')

parser.add_argument('-i','--input','--input_file',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input file name')

parser.add_argument('--output_file',
                    action='store',
                    dest='output_file',
                    type=str,
                    required=False,
                    default="recon_to31.nii",
                    help='output file name')

parser.add_argument('--output_folder',
                    action='store',
                    dest='output_folder',
                    type=str,
                    required=False,
                    help='output location')

parser.add_argument('--temp_folder',
                    action='store',
                    dest='temp',
                    type=str,
                    default='alignment_temp',
                    help='Temporaly folder name')

parser.add_argument('--FLIRT_options',
                    action='store',
                    dest='FLIRT_opts',
                    type=str,
                    default='-dof 7',
                    help='Option for FLIRT function')

# Arguments from parser place into variable args
args = parser.parse_args()

input_file = args.inp
output_file = args.output_file
temp_fol = args.temp
opts = args.FLIRT_opts
output_folder = args.output_folder

parent_path = get_parent_path(input_file)

print("[Info] Performing Alignment ...")
print(" --- Input file: " + input_file)

alignment_temp = parent_path + '/alignment_temp'
create_folder(alignment_temp)

if output_folder:
    create_folder(parent_path + '/' + output_folder)

os.system('cp ' + input_file + ' ' + alignment_temp + '/recon.nii')

print('')

#sys.exit()

def apply_flirt_transformation(_t):
    ''' Apply the flirt command to each element in the a_temp tuple using parallel computing '''
    
    flirt_command1 = [
        'flirt', 
        '-in', f'/neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-{_t}/template-{_t}.nii',
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

a_temp = ("23", "24", "25", "26", "27", "28", "29", "30", "31", "32")

@timeit_decorator
def execute_flirt_parallel():
    ''' Uses parallel computing to apply transformation to the data on multiple cpu cores'''
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(apply_flirt_transformation,a_temp)
execute_flirt_parallel()

# recon = nib.load('recon_highres.nii') # Load reconstruction image
recon = nib.load(alignment_temp + '/recon.nii')
size = recon.get_fdata().shape # Get the dimensions of the volume

meas = [0,0,0]
beginning = [0,0,0]

for i in range (0, 3):
    beginning[i] = int(round(size[i] / 10.0))
    temp = size[i] - beginning[i]
    meas[i] = temp - beginning[i]

    if i == 0:
        dimensions = zeros([size[1],size[2]])
        coronal = dict.fromkeys(range(0, meas[i]),dimensions)
    if i == 1:
        dimensions = zeros([size[0],size[2]])
        sagital = dict.fromkeys(range(0, meas[i]),dimensions)
    if i == 2:
        dimensions=zeros([size[0],size[1]])
        axial= dict.fromkeys(range(0, meas[i]),dimensions)

CCL = meas[0] + meas[1] + meas[2]

im = {'corrcoef':zeros([1,CCL * 10]), 'greatest':zeros([1,CCL]), 'template':zeros([1,CCL])}

for i in range (0, meas[0]): #Gets the number of slides choosen
	#Starts in the slide selected as beginning and ends passing the one selected as end
    a = beginning[0] + i
	#Get the slide of the reconstruction image.
    coronal[i] = np.uint8(np.squeeze(recon.get_fdata()[a,:,:]) / 4)

for i in range (0, meas[1]):
	#Starts in the slide selected as beginning and ends passing the one selected as end
    a = beginning[1] + i
	#Get the slide of the reconstruction image.
    sagital[i] = np.uint8(np.squeeze(recon.get_fdata()[:,a,:]) / 4)

for i in range (0, meas[2]):
	#Starts in the slide selected as beginning and ends passing the one selected as end
    a = beginning[2] + i 
	#alignment_tempGet the slide of the reconstruction image.
    axial[i] = np.uint8(np.squeeze(recon.get_fdata()[:,:,a]) / 4)

number = 22 #Stablishes the base to number the templates

def mean2(value):
    ''' MEAN2VALUE '''
    return np.sum(value)/np.size(value)


def corr2(_r, _t):
    ''' Compute the Pearson correlation coefficient between two 1D arrays. '''
    _r=_r-mean2(_r)
    _t=_t-mean2(_t)
    corr=((_r*_t).sum())/(math.sqrt((_r*_r).sum()*(_t*_t).sum()))
    return corr

for i in range (0,10): #Says that the process will repeat for the 10 templates
    number=number + 1 #The first template will be 23
    volume=alignment_temp+'/csf-aligned%d.nii.gz' %number #Construct the name of the template volume that will be loaded
    volume=nib.load(volume) #Load the template volume
    meascor=(meas[0]*i)
    meassag=(meas[1]*i)+(meas[0]*9)
    measax=(meas[2]*i)+(meas[0]*9)+(meas[1]*9)

    for j in range (0,CCL):
        if (j<meas[0]):
            t=meascor+j #Define the position in which the results will be stored\
            a=beginning[0]+j #Select the slide that will be taken
            slide=volume.get_fdata()[a,:,:] #Loads the slide
			
        if (j>=meas[0] and j<(meas[0]+meas[1])):
            t=meassag+j #Define the position in which the results will be stored\
            a=beginning[0]+j-meas[0] #Select the slide that will be taken
            slide=volume.get_fdata()[:,a,:] #Loads the slide
		
        if (j>=(meas[0]+meas[1])):
            t=measax+j #Define the position in which the results will be stored\
            a=beginning[0]+j-meas[0]-meas[1] #Select the slide that will be taken
            slide=volume.get_fdata()[:,:,a] #Loads the slide	
			
	#normalize the slide
        slide = np.uint8(256 * (slide - slide.min()) / (slide.max() - slide.min()))

        non_zero_indexes = np.nonzero(slide) #get the positions of the non zero values 

        try:
            csfi = slide[non_zero_indexes] #get the values of the non zero values
        except TypeError:
            print(" Error: slide is not subscriptable. ")

        temp = csfi.shape #gets the number of non zero values 
        temp = temp[0]
        reconi = []

        if j < meas[0]:
            for n in range (0,temp): #get the same indexes of the recon image
                slide=coronal[j].item(non_zero_indexes[0][n],non_zero_indexes[1][n])
                reconi.append(slide)

        if (j>=meas[0] and j<(meas[0]+meas[1])):
            for n in range (0,temp): #get the same indexes of the recon image
                jj=j-meas[0]
                slide=sagital[jj].item(non_zero_indexes[0][n],non_zero_indexes[1][n])
                reconi.append(slide)

        if j >= (meas[0]+meas[1]):
            for n in range (0,temp): #get the same indexes of the recon image
                jj=j-meas[0]-meas[1]
                slide=axial[jj].item(non_zero_indexes[0][n],non_zero_indexes[1][n])
                reconi.append(slide)
        im['corrcoef'][0,t]=corr2(reconi, csfi)

a = 0

for a in range (0,CCL):
    im['greatest'][0,a]=-5

    for i in range (0,10):
        if a < meas[0]:
            j = (meas[0] * i) + a

        if (a >= meas[0] and a < (meas[1] + meas[0]) ):
            j = (meas[1] * i) + (meas[0] * 9) + a

        if a>=(meas[1] + meas[0]):
            j=(meas[2] * i)+(meas[0] * 9)+(meas[1]*9) + a

        if im['corrcoef'][0,j] > im['greatest'][0,a]:
            im['greatest'][0,a]=im['corrcoef'][0,j]
            im['template'][0,a]=i + 23

t = im['template']
t = t[0]
a = t.tolist()
j = im['greatest']
jj = max(j[0])-((max(j[0])) / 2.5)

for i in range (0,CCL):
    if j[0][i] > jj:
        a.append(im['template'][0,i])

n = np.histogram(t,bins=[23,24,25,26,27,28,29,30,31,32,33])
temp = np.argsort(n[0])[::-1]
tempi = temp + 23
temp = str(tempi[0])
os.system('convert_xfm -omat '+ alignment_temp + '/InvAligned-' + temp
          + '.xfm -inverse ' + alignment_temp + '/Temp-Recon-7dof-' + temp + '.xfm')

os.system('convert_xfm -omat '+ alignment_temp
          + '/recon_to31.xfm -concat /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-'
          + temp + '/template-' + temp + 'to31.xfm ' + alignment_temp + '/InvAligned-' + temp + '.xfm')

os.system('flirt -in ' + alignment_temp
          + '/recon.nii -ref /neuro/users/mri.team/fetal_mri/templates_for_alginment/0.5mm/template-31/template-31.nii \
			-out ' + alignment_temp + '/recon_to31.nii.gz -init ' + alignment_temp + '/recon_to31.xfm -applyxfm')

os.system('gunzip ' + alignment_temp + '/recon_to31.nii.gz')

print(' === ALIGNMENT FINISHED WITH PARALLEL COMPUTING === ')

os.system('convert_xfm -omat ' + alignment_temp + '/recon_to31_inv.xfm -inverse ' 
          + alignment_temp + '/recon_to31.xfm;')
os.system('echo `avscale ' + alignment_temp + '/recon_to31_inv.xfm | grep Scales` > ' 
          + alignment_temp + '/temp.txt;')

scales = open(alignment_temp + '/temp.txt' , encoding='utf-8')
scales = scales.read()

os.system('param2xfm -clobber -scales ' + scales[16:-1] 
          + ' ' + alignment_temp + '/recon_native.xfm;')

#mv .../alignment_temp/recon_to31.nii  args.outputfol/args.outputFile
if output_folder:
    os.system('mv ' + alignment_temp + '/recon_to31.nii ' + output_folder + '/' + output_file)
    os.system('cp ' + alignment_temp + '/recon_native.xfm ' + output_folder + '/')
else:
    os.system('mv ' + alignment_temp + '/recon_to31.nii ' + parent_path + '/' + output_file)
    os.system('cp ' + alignment_temp + '/recon_native.xfm ' + parent_path + '/')
