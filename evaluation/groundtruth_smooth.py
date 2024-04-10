import numpy as np

def moving_average(data, window_size):
    """Smooth data using a simple moving average filter."""
    cumsum_vec = np.cumsum(np.insert(data, 0, 0)) 
    ma_vec = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return ma_vec

def smooth_ground_truth(input_file, output_file, window_size=10):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse the data into a NumPy array for easy manipulation
    data = np.array([list(map(float, line.split())) for line in lines])
    
    # Apply moving average filter to each column except the first one (timestamp)
    smoothed_data = np.copy(data)
    for i in range(1, data.shape[1]):
        smoothed_data[:, i] = np.concatenate([
            data[:window_size-1, i],  # Keep the first few values as is
            moving_average(data[:, i], window_size)
        ])
    
    # Write the smoothed data to the output file
    with open(output_file, 'w') as f:
        for row in smoothed_data:
            f.write(' '.join(map(str, row)) + '\n')

# Example usage
input_file = '/home/ubuntu/Downloads/rgbd_dlo_2/groundtruth.txt'  # Your input file name
output_file = '/home/ubuntu/Downloads/rgbd_dlo_2/smoothed_groundtruth.txt'  # Output file name
smooth_ground_truth(input_file, output_file)
