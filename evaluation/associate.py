import numpy as np
from scipy.spatial.transform import Rotation as R

def read_file_list(filename):
    with open(filename) as file:
        data = file.read()
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip() != ""] for line in lines if len(line) > 0 and line[0] != "#"]
    list = [(float(l[0]), l[1:]) for l in list if len(l) > 1]
    return dict(list)

def read_file_list_rotate(filename, x=0, y=0, z=0):
    # Convert rotation angles from degrees to radians
    rotation_radians = np.radians([x, y, z])
    rotation = R.from_euler('xyz', rotation_radians)
    
    with open(filename) as file:
        data = file.read()
        
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    data_list = [[v.strip() for v in line.split(" ") if v.strip() != ""] for line in lines if len(line) > 0 and line[0] != "#"]
    rotated_data = {}

    for line in data_list:
        if len(line) >= 8:  # Ensure it's a full data line with timestamp and position/orientation data
            stamp = float(line[0])
            position = np.array(line[1:4], dtype=np.float64)
            quaternion = line[4:8]  # Not modifying orientation in this example
            
            # Apply rotation to position
            rotated_position = rotation.apply(position)
            
            # Update data dictionary with rotated position
            rotated_data[stamp] = list(rotated_position) + quaternion

    return rotated_data

def associate(first_list, second_list, offset, max_difference):
    first_keys = list(first_list.keys())
    second_keys = list(second_list.keys())
    potential_matches = [(abs(a - (b + offset)), a, b)
                         for a in first_keys
                         for b in second_keys
                         if abs(a - (b + offset)) < max_difference]
    potential_matches.sort()
    matches = []
    for diff, a, b in potential_matches:
        if a in first_keys and b in second_keys:
            first_keys.remove(a)
            second_keys.remove(b)
            matches.append((a, b))

    matches.sort()

    return matches