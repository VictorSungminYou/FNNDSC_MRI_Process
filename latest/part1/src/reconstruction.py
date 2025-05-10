''' Reconstruction , input folder MUST have quality_assessment.csv and nuc folder'''
import os
import argparse
import csv
from helper_functions import get_parent_path

def create_folder(folder):
    '''Define a function to create a missing folder'''

    if not os.path.exists(folder):
        os.mkdir(folder)


parser = argparse.ArgumentParser('=== Fetal recon script for fetal pipeline ===')

parser.add_argument('-i','--input', '--input_folder',
                    action='store',
                    dest='inp',
                    type=str,
                    required=True,
                    help='input folder name')

parser.add_argument('--output_file',
                    action='store',
                    dest='recon_name',
                    default='recon.nii',
                    type=str,
                    help = 'Name for the reconstruction file (default=recon.nii)')

parser.add_argument('--output_folder',
                    action='store',
                    dest='recon_fol',
                    default='recon_segmentation',
                    type=str,
                    help = 'Name for the reconstruction folder')

parser.add_argument('--threshold',
                    action='store',
                    dest='thresh',
                    default=0.4,
                    type=float,
                    help='Treshold for files from QA (default=0.4)')

parser.add_argument('--qa_file',
                    action='store',
                    default='quality_assessment.csv',
                    dest='qa_file',
                    type=str,
                    help='Name for the file where quality assesment is stored (default=quality_assesment.csv)')

parser.add_argument('--res',
                    action='store',
                    dest='res',
                    default='0.5',
                    type=str,
                    help='Output resolution of reconstuction (default=0.5)')

parser.add_argument('--thickness',
                    action='store',
                    dest='thickness',
                    default=0,
                    type=float,
                    help='Slice thickness of each input stack. If not provided, use the slice gap of the input stack. If only a single number is provided, Assume all input stacks have the same thickness.')

parser.add_argument('--GPU',
                    action='store',
                    dest='GPU',
                    default='0',
                    type=str,
                    help='GPU number to run NESVOR (default=0)')


args = parser.parse_args()

input_fol = args.inp
recon_fol = args.recon_fol
output_file = args.recon_name
thresh = args.thresh
qa_file = args.qa_file
resolution = args.res
thickness = args.thickness
parent_fol = get_parent_path(input_fol)
GPU= args.GPU

threshold = thresh #Treshold for files used for reconstruction
Best_list = []

qa_dir = os.path.join(input_fol,qa_file) #Path for Quality Assessment file

with open(qa_dir, 'r',encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        score = float(row["quality"]) #Reading QC score and cast it to float
        if score >= threshold:
            Best_list.append(row)


Best_list_sorted = sorted(Best_list, key=lambda row: row['quality'], reverse=True)
# print("Best_list_sorted",Best_list_sorted)

print("[Info] -Starting Fetal Reconstruction with Nesvor ...")

nesvor_com = '--nv "/neuro/labs/grantlab/research/Apptainer/nesvor:v0.6.0rc2.sif" nesvor reconstruct'
out_vol = os.path.join(input_fol, output_file)

print("[Info] List of found MRI stack from QA file")
#!!!
print(str(['./' + row['filename'] for row in Best_list_sorted]).replace("[","").replace("]","")
      .replace("'","").replace(",",""))

if thickness == 0:   # Thickness is not provided
    os.system('CUDA_VISIBLE_DEVICES=' + GPU + ' apptainer exec ' + nesvor_com + ' --input-stacks '
            + str(['./'+row['filename'] for row in Best_list_sorted]).replace("[", "")
            .replace("]", "").replace("'", "").replace(",", "") + \
            ' --output-volume '  + out_vol + ' --output-resolution ' + resolution + ' --svort-version v2')
else:
    os.system('CUDA_VISIBLE_DEVICES=' + GPU + ' apptainer exec ' + nesvor_com + ' --input-stacks '
            + str(['./'+row['filename'] for row in Best_list_sorted]).replace("[", "")
            .replace("]", "").replace("'", "").replace(",", "") + \
            ' --thickness {}'.format(thickness) + ' --output-volume '  + out_vol + ' --output-resolution ' + resolution + ' --svort-version v2')

# if recon_fol:
#     #Checking for recon folder (create if doesn't exist)
#     create_folder(os.path.join(input_fol, recon_fol))
#     os.system('mv ' + out_vol + ' ' + recon_fol + '/')
