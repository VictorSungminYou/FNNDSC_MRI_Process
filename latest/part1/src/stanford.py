from PIL import Image
import numpy as np
from helper_functions import timeit_decorator
import os

from masking import singularity



image = Image.open('2.jpg')

gray_image_array = np.array(image.convert('L'))



VERB_TEXT = '>/dev/null 2>&1'

os.system(f'singularity run --no-home -B {gray_image_array} :/data /neuro/labs/grantlab/research/MRI_processing/sungmin.you/MRI_SIF/brain_mask.sif /data; {VERB_TEXT}')
