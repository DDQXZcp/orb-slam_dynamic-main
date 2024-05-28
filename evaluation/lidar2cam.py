import numpy as np
from scipy.spatial.transform import Rotation as R
import os
import sys

# Define the transformation matrix from MID360 to d435i
T_mid_to_d435i = np.array([[1, 0, 0, 0.06733],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

def pose_to_matrix(x, y, z, qx, qy, qz, qw):
    t = np.array([x, y, z])
    r = R.from_quat([qx, qy, qz, qw]).as_matrix()
    T = np.eye(4)
    T[:3, :3] = r
    T[:3, 3] = t
    return T

def transform_pose(mid_pose, T_mid_to_d435i):
    T_mid = pose_to_matrix(*mid_pose)
    T_d435i = np.dot(T_mid, T_mid_to_d435i)
    return T_d435i

def matrix_to_pose(T):
    t = T[:3, 3]
    r = R.from_matrix(T[:3, :3])
    q = r.as_quat()
    return t.tolist() + q.tolist()

def process_poses(poses, T_mid_to_d435i):
    transformed_poses = []
    for pose in poses:
        mid_pose = [pose[1], pose[2], pose[3], pose[4], pose[5], pose[6], pose[7]]
        T_d435i = transform_pose(mid_pose, T_mid_to_d435i)
        d435i_pose = matrix_to_pose(T_d435i)
        transformed_poses.append([pose[0]] + d435i_pose)
    return transformed_poses

def read_groundtruth(file_path):
    poses = []
    with open(file_path, 'r') as f:
        for line in f:
            poses.append([float(x) for x in line.strip().split()])
    return poses

def write_groundtruth(file_path, poses):
    with open(file_path, 'w') as f:
        for pose in poses:
            f.write(" ".join(map(str, pose)) + "\n")

def main(input_file_path):
    # Read poses from the input groundtruth file
    poses = read_groundtruth(input_file_path)

    # Apply transformation to all poses
    transformed_poses = process_poses(poses, T_mid_to_d435i)

    # Create the output file path in the same directory
    output_file_path = os.path.join(os.path.dirname(input_file_path), 'groundtruth_cam.txt')

    # Write transformed poses to the output file
    write_groundtruth(output_file_path, transformed_poses)

    print(f"Transformation complete. The transformed poses have been saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_groundtruth.txt>")
    else:
        input_file_path = sys.argv[1]
        main(input_file_path)
