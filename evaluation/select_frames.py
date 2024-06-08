import os
import argparse

def select_frames(folder_path, frame_number):
    # Define input and output file paths
    rgb_input_path = os.path.join(folder_path, 'rgb.txt')
    mask_input_path = os.path.join(folder_path, 'mask.txt')
    rgb_output_path = os.path.join(folder_path, f'rgb_{frame_number}.txt')
    mask_output_path = os.path.join(folder_path, f'mask_{frame_number}.txt')

    # Read and select frames from rgb.txt
    with open(rgb_input_path, 'r') as rgb_file:
        rgb_lines = rgb_file.readlines()
    
    selected_rgb_lines = [line for i, line in enumerate(rgb_lines) if i % frame_number == 0]

    # Write selected frames to rgb_n.txt
    with open(rgb_output_path, 'w') as rgb_output_file:
        rgb_output_file.writelines(selected_rgb_lines)

    # Read and select frames from mask.txt
    with open(mask_input_path, 'r') as mask_file:
        mask_lines = mask_file.readlines()

    selected_mask_lines = [line for i, line in enumerate(mask_lines) if i % frame_number == 0]

    # Write selected frames to mask_n.txt
    with open(mask_output_path, 'w') as mask_output_file:
        mask_output_file.writelines(selected_mask_lines)

    print(f"Selected frames written to {rgb_output_path} and {mask_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select every n-th frame from rgb.txt and mask.txt")
    parser.add_argument('folder_path', type=str, help='Path to the folder containing rgb.txt and mask.txt')
    parser.add_argument('frame_number', type=int, help='Frame number interval for selecting frames')
    
    args = parser.parse_args()
    select_frames(args.folder_path, args.frame_number)
