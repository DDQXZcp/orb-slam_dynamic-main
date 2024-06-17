import os
import associate

def associate_and_write(parent_folder, output_file="associate.txt"):
    # File paths
    rgb_file = os.path.join(parent_folder, "rgb.txt")
    depth_file = os.path.join(parent_folder, "depth.txt")
    
    # Read RGB and Depth data
    rgb_info = associate.read_file_list(rgb_file)
    depth_info = associate.read_file_list(depth_file)
    
    # Associate RGB and Depth data
    matches = associate.associate(rgb_info, depth_info, 0, float('inf'))

    # Prepare mask filenames mapping based on RGB order
    mask_filenames = {timestamp: f"{idx:05}.png" for idx, timestamp in enumerate(sorted(rgb_info.keys()))}
    
    # Write associations to output_file
    output_path = os.path.join(parent_folder, output_file)
    with open(output_path, 'w') as f:
        for rgb_time, depth_time in matches:
            if rgb_time in mask_filenames:
                mask_filename = mask_filenames[rgb_time]
                f.write(f"{rgb_time} {rgb_info[rgb_time][0]} {depth_time} {depth_info[depth_time][0]} {rgb_time} mask/{mask_filename}\n")

    print(f"Associations written to {output_path}.")

associate_and_write('/home/ubuntu/Downloads/rgbd_dlo_60')