import cv2
import numpy as np
import os
import re  # Import the regular expression module

def combine_masks(folder_path):
    # Use a regular expression to match subfolders starting with 'mask_' followed by a number
    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir() and re.match(r'mask_\d+', f.name)]
    
    if not subfolders:
        return "No valid mask folders found in the given directory."
    
    # Ensure the mask directory exists
    mask_dir = os.path.join(folder_path, 'mask')
    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)
    
    # Get the list of mask files in the first subfolder to define the loop
    mask_files = [f for f in os.listdir(subfolders[0]) if f.endswith('.png')]
    
    for mask_file in mask_files:
        combined_mask = None
        for subfolder in subfolders:
            mask_path = os.path.join(subfolder, mask_file)
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                print(f"Warning: Could not read mask {mask_path}")
                continue  # Skip this mask if it couldn't be read
            if combined_mask is None:
                combined_mask = mask
            else:
                # Combine by taking max value pixel-wise (255 is mask, 0 is background)
                combined_mask = np.maximum(combined_mask, mask)
                
        combined_mask_path = os.path.join(mask_dir, mask_file)
        cv2.imwrite(combined_mask_path, combined_mask)
    
    return f"Combined masks saved in {mask_dir}."
