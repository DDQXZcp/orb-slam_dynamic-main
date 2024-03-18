import numpy
import associate
import sys

offset = 0.0
scale = 1.0
max_difference = 0.02

def align(model, data):
    """Align two trajectories using the method of Horn (closed-form).
    
    Input:
    model -- first trajectory (3xn)
    data -- second trajectory (3xn)
    
    Output:
    rot -- rotation matrix (3x3)
    trans -- translation vector (3x1)
    trans_error -- translational error per point (1xn)
    
    """
    numpy.set_printoptions(precision=3, suppress=True)
    model_zerocentered = model - model.mean(1)
    data_zerocentered = data - data.mean(1)
    
    W = numpy.zeros((3, 3))
    for column in range(model.shape[1]):
        W += numpy.outer(model_zerocentered[:, column], data_zerocentered[:, column])
    U, d, Vh = numpy.linalg.svd(W.transpose())
    S = numpy.matrix(numpy.identity(3))
    if(numpy.linalg.det(U) * numpy.linalg.det(Vh) < 0):
        S[2, 2] = -1
    rot = U*S*Vh
    trans = data.mean(1) - rot * model.mean(1)
    
    model_aligned = rot * model + trans
    alignment_error = model_aligned - data
    
    trans_error = numpy.sqrt(numpy.sum(numpy.multiply(alignment_error, alignment_error), 0)).A[0]
    
    return rot, trans, trans_error

def compute_ate(groundtruth_path, trajectory1_path, trajectory2_path):

    first_list = associate.read_file_list(groundtruth_path)
    second_list = associate.read_file_list(trajectory1_path)
    third_list = associate.read_file_list(trajectory2_path)
    print(groundtruth_path, trajectory1_path, trajectory2_path)

    second_keys = sorted(second_list.keys())
    third_keys = sorted(third_list.keys())
    common_start = max(second_keys[0], third_keys[0])
    common_end = min(second_keys[-1], third_keys[-1])
    print("common_start: ",common_start, "common_end: ", common_end)
    second_list = {k: v for k, v in second_list.items() if common_start <= k <= common_end}
    third_list = {k: v for k, v in third_list.items() if common_start <= k <= common_end}

    matches_2 = associate.associate(first_list, second_list, offset, max_difference)
    if len(matches_2) < 2:
        sys.exit("Couldn't find matching timestamp pairs between ground truth and second trajectory! Did you choose the correct sequence?")
    
    first_xyz_2 = numpy.matrix([[float(value) for value in first_list[a][0:3]] for a, b in matches_2]).transpose()
    second_xyz = numpy.matrix([[float(value) * scale for value in second_list[b][0:3]] for a, b in matches_2]).transpose()
    rot_2, trans_2, trans_error_2 = align(second_xyz, first_xyz_2)
    ATE_2 = numpy.sqrt(numpy.dot(trans_error_2, trans_error_2) / len(trans_error_2))

    # Associate, align, and calculate ATE for the third trajectory
    matches_3 = associate.associate(first_list, third_list, offset, max_difference)
    if len(matches_3) < 2:
        sys.exit("Couldn't find matching timestamp pairs between ground truth and third trajectory! Did you choose the correct sequence?")
    
    first_xyz_3 = numpy.matrix([[float(value) for value in first_list[a][0:3]] for a, b in matches_3]).transpose()
    third_xyz = numpy.matrix([[float(value) * scale for value in third_list[b][0:3]] for a, b in matches_3]).transpose()
    rot_3, trans_3, trans_error_3 = align(third_xyz, first_xyz_3)
    ATE_3 = numpy.sqrt(numpy.dot(trans_error_3, trans_error_3) / len(trans_error_3))

    return ATE_2, ATE_3, len(matches_2), len(matches_3)