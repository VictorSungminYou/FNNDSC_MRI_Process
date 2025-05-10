''' Functions that support the main modules '''

import time
import os
import nibabel as nib
import glob
import numpy as np
import matplotlib.pyplot as plt

def timeit_decorator(func):
    ''' Prints the function execution time '''
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"Function {func.__name__} took {execution_time:.4f} seconds")
        return result
    return wrapper

def get_parent_path(dir_path):
    return os.path.abspath(os.path.join(dir_path, os.pardir))



def create_folder(folder):
    '''Define a function to create a missing folder'''
    if not os.path.exists(folder):
        os.mkdir(folder)

def verify(img_path):
    img_list = np.asarray(sorted(glob.glob('{}/*_brain.nii*'.format(img_path))))
    def auto_crop_image(input_name, output_name, reserve):
        nim = nib.load(input_name)
        image = nim.get_data()
        if np.mean(image) == 0:
            print(input_name,'\t Passed')
            return 0
        # else:
        #     print(input_name, '\t Worked')
        image = np.pad(image, [(50,50),(50,50),(16,16)], 'constant')
        X, Y, Z = image.shape[:3]

        # Detect the bounding box of the foreground
        idx = np.nonzero(image > 0)
        x1, x2 = idx[0].min() - reserve[0,0], idx[0].max() + reserve[0,1] + 1
        y1, y2 = idx[1].min() - reserve[1,0], idx[1].max() + reserve[1,1] + 1
        z1, z2 = idx[2].min() - reserve[2,0], idx[2].max() + reserve[2,1] + 1
        # print('Bounding box')
        # print(input_name+'\t'+str([x2-x1, y2-y1, z2-z1]))
        # return [x2-x1, y2-y1, z2-z1]
        # print('  bottom-left corner = ({},{},{})'.format(x1, y1, z1))
        # print('  top-right corner = ({},{},{})'.format(x2, y2, z2))

        # Crop the image
        image = image[x1:x2, y1:y2, z1:z2]

        # Update the affine matrix
        affine = nim.affine
        affine[:3, 3] = np.dot(affine, np.array([x1, y1, z1, 1]))[:3]
        nim2 = nib.Nifti1Image(image, affine)
        nib.save(nim2, output_name)
        return image

    for i in range(len(img_list)):
        f,axarr = plt.subplots(1,6)#,figsize=(len(in_img_list),9))
        f.patch.set_facecolor('k')
        #imsize = np.zeros([len(in_img_list),3])
        img = auto_crop_image(img_list[i], img_list[i].replace('.nii.gz','').replace('.nii','')+'_crop.nii.gz', np.array([[0,0],[0,0],[0,0]]))
        if isinstance(img,(list, tuple, np.ndarray)) == False:
            continue
        
        img = nib.load(img_list[i].replace('.nii.gz','').replace('.nii','')+'_crop.nii.gz').get_data()
        hdr = nib.load(img_list[i].replace('.nii.gz','').replace('.nii','')+'_crop.nii.gz').header
        axarr[0].imshow(np.rot90(img[:,:,np.int_(img.shape[-1]*0.3)]),cmap='gray')
        axarr[0].axis('off')
        axarr[0].set_title(str(img_list[i]),size=5,color='white')

        axarr[1].imshow(np.rot90(img[:,:,np.int_(img.shape[-1]*0.4)]),cmap='gray')
        axarr[1].axis('off')

        axarr[2].imshow(np.rot90(img[:,:,np.int_(img.shape[-1]*0.5)]),cmap='gray')
        axarr[2].axis('off')

        axarr[3].imshow(np.rot90(img[:,:,np.int_(img.shape[-1]*0.6)]),cmap='gray')
        axarr[3].axis('off')

        axarr[4].imshow(np.rot90(img[:,np.int_(img.shape[-2]*0.5),:]),cmap='gray',aspect=str(hdr['pixdim'][3]/hdr['pixdim'][2]))
        axarr[4].axis('off')

        axarr[5].imshow(np.rot90(img[np.int_(img.shape[0]*0.5),:,:]),cmap='gray',aspect=str(hdr['pixdim'][3]/hdr['pixdim'][1]))
        axarr[5].axis('off')

        f.subplots_adjust(wspace=0, hspace=0)
        plt.savefig(img_list[i].replace('.nii.gz','').replace('.nii','')+'_crop_verify.png', facecolor=f.get_facecolor(), pad_inches=0, dpi=300)
        plt.close()
    return 0

