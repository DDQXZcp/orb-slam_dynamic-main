import gradio as gr
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import associate
import evaluate_ate
import evaluate_rpe
import mask_combine
import mask_associate

# Gradio 3.48
# Python 3

path_text = """
## Ground Truth Trajectory Paths

- Path 1: `/home/ubuntu/Downloads/rgbd_dataset_freiburg3_sitting_static/groundtruth.txt`
- Path 2: `/home/ubuntu/Downloads/rgbd_dataset_freiburg3_walking_xyz/groundtruth.txt`
- Path 3: `/home/ubuntu/Downloads/rgbd_dataset_freiburg3_long_office_household/groundtruth.txt`

**Note:** These paths are for display purposes only and cannot be edited.
"""

def visualize_trajectory_plotly(data_dict, name):
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
    path_display = gr.Markdown(path_text)
    with gr.Row():
        groundtruth_path = gr.Textbox(label="Groundtruth Trajectory Path", value = "/home/ubuntu/Downloads/rgbd_dlo/groundtruth.txt")
        trajectory1_path = gr.Textbox(label="Trajectory 1 Path", value = "/home/ubuntu/ORB_SLAM3/dlo_1.txt")
        trajectory2_path = gr.Textbox(label="Trajectory 2 Path", value = "/home/ubuntu/orb-slam_dynamic-main/dlo_1.txt")
    with gr.Row():
        compute_btn = gr.Button("Compute ATE & RPE")
        visualize_btn = gr.Button("Visualize Trajectories")
    # with gr.Row():
    #     plot_output_gt = gr.Plot(label="Groundtruth Trajectory Visualization")
    #     plot_output_t1 = gr.Plot(label="Trajectory (with mask) Visualization")
    #     plot_output_t2 = gr.Plot(label="Trajectory (without mask) Visualization")
    plot_output_gt = gr.Plot(label="Groundtruth Trajectory Visualization")
    plot_output_t1 = gr.Plot(label="Trajectory (with mask) Visualization")
    plot_output_t2 = gr.Plot(label="Trajectory (without mask) Visualization")
    with gr.Row():
        ate_output1 = gr.Text(label="ATE for Trajectory 1")
        ate_output2 = gr.Text(label="ATE for Trajectory 2")
        ate_pair1 = gr.Text(label="Match Pairs for Trajectory 1")
        ate_pair2 = gr.Text(label="Match Pairs for Trajectory 2")
    with gr.Row():
        rpe_output1 = gr.Text(label="RPE for Trajectory 1")
        rpe_output2 = gr.Text(label="RPE for Trajectory 2")
        rpe_pair1 = gr.Text(label="Match Pairs for Trajectory 1")
        rpe_pair2 = gr.Text(label="Match Pairs for Trajectory 2")

    with gr.Row():
        mask_folder_path = gr.Textbox(label="Path to folders containing masks", value = "/home/ubuntu/Downloads/rgbd_dataset_freiburg3_walking_xyz")
        combine_masks_btn = gr.Button("Combine Masks")
        mask_combine_output = gr.Text(label="Mask Combination Result")
    with gr.Row():
        associate_folder_path = gr.Textbox(label="Path to folders containing txt", value = "/home/ubuntu/Downloads/rgbd_dataset_freiburg3_walking_xyz")
        associate_txt_btn = gr.Button("associate")

    def visualize_all(groundtruth_path, trajectory1_path, trajectory2_path):
        # Load and parse the trajectory data
        gt_data = associate.read_file_list_rotate(groundtruth_path, x=90)
        t1_data = associate.read_file_list(trajectory1_path)
        t2_data = associate.read_file_list(trajectory2_path)
        
        gt_timestamps = sorted(map(float, gt_data.keys()))
        t1_timestamps = sorted(map(float, t1_data.keys()))
        t2_timestamps = sorted(map(float, t2_data.keys()))
        
        # Find the maximum of the minimum timestamps and the minimum of the maximum timestamps
        common_start = max(gt_timestamps[0], t1_timestamps[0], t2_timestamps[0])
        common_end = min(gt_timestamps[-1], t1_timestamps[-1], t2_timestamps[-1])
        
        # Ensure there is overlap
        if common_start >= common_end:
            raise ValueError("No overlapping timestamps found among the trajectories.")
        
        # Filter data for common timeframe
        gt_data_common = {k: v for k, v in gt_data.items() if common_start <= k <= common_end}
        t1_data_common = {k: v for k, v in t1_data.items() if common_start <= k <= common_end}
        t2_data_common = {k: v for k, v in t2_data.items() if common_start <= k <= common_end}
        
        # Visualize trimmed trajectories
        fig_gt = visualize_trajectory_plotly(gt_data_common, "Groundtruth")
        fig_t1 = visualize_trajectory_plotly(t1_data_common, "Trajectory 1")
        fig_t2 = visualize_trajectory_plotly(t2_data_common, "Trajectory 2")
        return fig_gt, fig_t1, fig_t2


    visualize_btn.click(
        fn=visualize_all,
        inputs=[groundtruth_path, trajectory1_path, trajectory2_path],
        outputs=[plot_output_gt, plot_output_t1, plot_output_t2]
    )

    def compute_ate_and_rpe(groundtruth_path, trajectory1_path, trajectory2_path):
    # Assuming evaluate_ate.compute_ate returns two ATE results and two sets of pairs
        ate_result1, ate_result2, ate_pairs_result1, ate_pairs_result2 = evaluate_ate.compute_ate(
        groundtruth_path, trajectory1_path, trajectory2_path)
    
    # Assuming evaluate_rpe.compute_rpe returns two RPE results and two sets of pairs
        rpe_result1, rpe_result2, rpe_pairs_result1, rpe_pairs_result2 = evaluate_rpe.compute_rpe(
        groundtruth_path, trajectory1_path, trajectory2_path)
    
    # Return all results in the order expected by the Gradio interface
        return ate_result1, ate_result2, ate_pairs_result1, ate_pairs_result2, \
           rpe_result1, rpe_result2, rpe_pairs_result1, rpe_pairs_result2
    
    compute_btn.click(
        fn=compute_ate_and_rpe,
        inputs=[groundtruth_path, trajectory1_path, trajectory2_path],
        outputs=[ate_output1, ate_output2, ate_pair1, ate_pair2, rpe_output1, rpe_output2, rpe_pair1, rpe_pair2]
    ) 

    def combine_masks(mask_folder_path):
        mask_combine.combine_masks(mask_folder_path)

    combine_masks_btn.click(
        fn=combine_masks,
        inputs=mask_folder_path,
        outputs=mask_combine_output
    )

    def wrap_associate_and_write(folder_path):
        # Wrapper function to match Gradio expectations
        mask_associate.associate_and_write(folder_path)
        return f"Associations written to {folder_path}/associate.txt."
    
    associate_txt_btn.click(
        fn=wrap_associate_and_write,
        inputs=associate_folder_path
    )

if __name__ == "__main__":
    app.launch()
