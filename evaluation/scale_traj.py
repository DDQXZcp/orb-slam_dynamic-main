import numpy as np
import sys
import os

def scale_trajectory(input_file, output_file, scale_factor):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse the data into a NumPy array for easy manipulation
    data = np.array([list(map(float, line.split())) for line in lines])
    
    # Apply the scaling factor to the coordinates (second, third, and fourth columns)
    data[:, 1:4] *= scale_factor
    
    # Write the scaled data to the output file
    with open(output_file, 'w') as f:
        for row in data:
            f.write(' '.join(map(str, row)) + '\n')

    print(f"Scaled data written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_file> <scale_factor>")
        sys.exit(1)

    input_file = sys.argv[1]
    scale_factor = float(sys.argv[2])
    
    # Generate the output file path
    directory, filename = os.path.split(input_file)
    output_file = os.path.join(directory, f"scaled_{filename}")
    
    scale_trajectory(input_file, output_file, scale_factor)
