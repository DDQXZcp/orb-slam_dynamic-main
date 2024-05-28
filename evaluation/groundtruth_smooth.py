import numpy as np
from scipy.stats import zscore
import os
import sys

def moving_average(data, window_size):
    """Smooth data using a simple moving average filter."""
    cumsum_vec = np.cumsum(np.insert(data, 0, 0)) 
    ma_vec = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return ma_vec

def remove_outliers(data, threshold=3.0):
    """Remove outliers from data using Z-score."""
    z_scores = zscore(data, axis=0)
    filtered_entries = (np.abs(z_scores) < threshold).all(axis=1)
    return data[filtered_entries]

def smooth_ground_truth(input_file, window_size=10, outlier_threshold=3.0):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse the data into a NumPy array for easy manipulation
    data = np.array([list(map(float, line.split())) for line in lines])
    
    # Remove outliers
    data_no_outliers = remove_outliers(data[:, 1:], outlier_threshold)  # Exclude timestamp for outlier detection
    data_no_outliers = np.hstack((data[:len(data_no_outliers), :1], data_no_outliers))  # Reattach the timestamp
    
    # Apply moving average filter to each column except the first one (timestamp)
    smoothed_data = np.copy(data_no_outliers)
    for i in range(1, data_no_outliers.shape[1]):
        smoothed_data[:, i] = np.concatenate([
            data_no_outliers[:window_size-1, i],  # Keep the first few values as is
            moving_average(data_no_outliers[:, i], window_size)
        ])
    
    # Generate the output file path
    directory, filename = os.path.split(input_file)
    output_file = os.path.join(directory, f"smoothed_{filename}")
    
    # Write the smoothed data to the output file
    with open(output_file, 'w') as f:
        for row in smoothed_data:
            f.write(' '.join(map(str, row)) + '\n')

    print(f"Smoothed data written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    smooth_ground_truth(input_file)