import gradio as gr
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

# Gradio 3.48
# Python 3

offset = 0.0
scale = 1.0
max_difference = 0.02

def read_file_list(filename):
    with open(filename) as file:
        data = file.read()
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    list = [[v.strip() for v in line.split(" ") if v.strip() != ""] for line in lines if len(line) > 0 and line[0] != "#"]
    list = [(float(l[0]), l[1:]) for l in list if len(l) > 1]
    return dict(list)

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

    print("first_list: ", len(first_list))
    print("second_list: ", len(second_list))
    print("matches: ", len(matches))

    return matches

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

    first_list = read_file_list(groundtruth_path)
    second_list = read_file_list(trajectory1_path)
    third_list = read_file_list(trajectory2_path)
    print(groundtruth_path, trajectory1_path, trajectory2_path)

    second_keys = sorted(second_list.keys())
    third_keys = sorted(third_list.keys())
    common_start = max(second_keys[0], third_keys[0])
    common_end = min(second_keys[-1], third_keys[-1])
    print("common_start: ",common_start, "common_end: ", common_end)
    second_list = {k: v for k, v in second_list.items() if common_start <= k <= common_end}
    third_list = {k: v for k, v in third_list.items() if common_start <= k <= common_end}

    matches_2 = associate(first_list, second_list, offset, max_difference)
    if len(matches_2) < 2:
        sys.exit("Couldn't find matching timestamp pairs between ground truth and second trajectory! Did you choose the correct sequence?")
    
    first_xyz_2 = numpy.matrix([[float(value) for value in first_list[a][0:3]] for a, b in matches_2]).transpose()
    second_xyz = numpy.matrix([[float(value) * scale for value in second_list[b][0:3]] for a, b in matches_2]).transpose()
    rot_2, trans_2, trans_error_2 = align(second_xyz, first_xyz_2)
    ATE_2 = numpy.sqrt(numpy.dot(trans_error_2, trans_error_2) / len(trans_error_2))

    # Associate, align, and calculate ATE for the third trajectory
    matches_3 = associate(first_list, third_list, offset, max_difference)
    if len(matches_3) < 2:
        sys.exit("Couldn't find matching timestamp pairs between ground truth and third trajectory! Did you choose the correct sequence?")
    
    first_xyz_3 = numpy.matrix([[float(value) for value in first_list[a][0:3]] for a, b in matches_3]).transpose()
    third_xyz = numpy.matrix([[float(value) * scale for value in third_list[b][0:3]] for a, b in matches_3]).transpose()
    rot_3, trans_3, trans_error_3 = align(third_xyz, first_xyz_3)
    ATE_3 = numpy.sqrt(numpy.dot(trans_error_3, trans_error_3) / len(trans_error_3))

    print("ATE for the second trajectory: {:.3f} m".format(ATE_2))
    print("ATE for the third trajectory: {:.3f} m".format(ATE_3))

    return ATE_2, ATE_3

def visualize_trajectory_plotly(path, name):
    data_dict = read_file_list(path)
    positions = [(float(data[0]), float(data[1]), float(data[2])) for _, data in data_dict.items()]
    x, y, z = zip(*positions)
    
    fig = go.Figure()

    # Main trajectory line with markers
    fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines+markers',
                               name=name, marker=dict(size=2), line=dict(width=1)))

    # Start point marker
    fig.add_trace(go.Scatter3d(x=[x[0]], y=[y[0]], z=[z[0]],
                               mode='markers', name='Start',
                               marker=dict(size=6, color='green')))
    
    # End point marker
    fig.add_trace(go.Scatter3d(x=[x[-1]], y=[y[-1]], z=[z[-1]],
                               mode='markers', name='End',
                               marker=dict(size=6, color='red')))

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                      scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    return fig

with gr.Blocks() as app:
    gr.Markdown("# Trajectory Analysis")
    with gr.Row():
        groundtruth_path = gr.Textbox(label="Groundtruth Trajectory Path", value = "/home/ubuntu/Downloads/rgbd_dataset_freiburg3_sitting_static/groundtruth.txt")
        trajectory1_path = gr.Textbox(label="Trajectory 1 Path", value = "/home/ubuntu/orb-slam_dynamic-main/FullFrameTrajectoryTUM_sit_masked.txt")
        trajectory2_path = gr.Textbox(label="Trajectory 2 Path", value = "/home/ubuntu/orb-slam_dynamic-main/FullFrameTrajectoryTUM_sit_unmasked.txt")
    with gr.Row():
        compute_ate_btn = gr.Button("Compute ATE")
        visualize_btn = gr.Button("Visualize Trajectories")
    with gr.Row():
        plot_output_gt = gr.Plot(label="Groundtruth Trajectory Visualization")
        plot_output_t1 = gr.Plot(label="Trajectory 1 Visualization")
        plot_output_t2 = gr.Plot(label="Trajectory 2 Visualization")
    with gr.Row():
        ate_output1 = gr.Text(label="ATE for Trajectory 1")
        ate_output2 = gr.Text(label="ATE for Trajectory 2")

    def visualize_all(groundtruth_path, trajectory1_path, trajectory2_path):
        fig_gt = visualize_trajectory_plotly(groundtruth_path, "Groundtruth")
        fig_t1 = visualize_trajectory_plotly(trajectory1_path, "Trajectory 1")
        fig_t2 = visualize_trajectory_plotly(trajectory2_path, "Trajectory 2")
        return fig_gt, fig_t1, fig_t2

    visualize_btn.click(
        fn=visualize_all,
        inputs=[groundtruth_path, trajectory1_path, trajectory2_path],
        outputs=[plot_output_gt, plot_output_t1, plot_output_t2]
    )
    
    compute_ate_btn.click(
        fn=compute_ate,
        inputs=[groundtruth_path, trajectory1_path, trajectory2_path],
        outputs=[ate_output1, ate_output2]
    )

if __name__ == "__main__":
    app.launch()
