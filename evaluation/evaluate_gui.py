import gradio as gr
import numpy
import associate  # Ensure this module is properly defined or imported in your environment.

def align(model,data):
    """Align two trajectories using the method of Horn (closed-form).
    
    Input:
    model -- first trajectory (3xn)
    data -- second trajectory (3xn)
    
    Output:
    rot -- rotation matrix (3x3)
    trans -- translation vector (3x1)
    trans_error -- translational error per point (1xn)
    
    """
    numpy.set_printoptions(precision=3,suppress=True)
    model_zerocentered = model - model.mean(1)
    data_zerocentered = data - data.mean(1)
    
    W = numpy.zeros( (3,3) )
    for column in range(model.shape[1]):
        W += numpy.outer(model_zerocentered[:,column],data_zerocentered[:,column])
    U,d,Vh = numpy.linalg.linalg.svd(W.transpose())
    S = numpy.matrix(numpy.identity( 3 ))
    if(numpy.linalg.det(U) * numpy.linalg.det(Vh)<0):
        S[2,2] = -1
    rot = U*S*Vh
    trans = data.mean(1) - rot * model.mean(1)
    
    model_aligned = rot * model + trans
    alignment_error = model_aligned - data
    
    trans_error = numpy.sqrt(numpy.sum(numpy.multiply(alignment_error,alignment_error),0)).A[0]
        
    return rot,trans,trans_error

def compute_ate(groundtruth_file, trajectory1_file, trajectory2_file):
    groundtruth_list = associate.read_file_list(groundtruth_file.name)
    trajectory1_list = associate.read_file_list(trajectory1_file.name)
    trajectory2_list = associate.read_file_list(trajectory2_file.name)

    # Process files and compute ATE for each trajectory against the groundtruth
    # This is a placeholder for demonstration. Implement actual computation using your align function.
    ATE_1 = "Computed ATE for Trajectory 1: Placeholder"
    ATE_2 = "Computed ATE for Trajectory 2: Placeholder"

    return ATE_1, ATE_2

# Define your Gradio interface here
iface = gr.Interface(
    fn=compute_ate,
    inputs=[gr.inputs.File(label="Groundtruth Trajectory"), 
            gr.inputs.File(label="Trajectory 1"), 
            gr.inputs.File(label="Trajectory 2")],
    outputs=["text", "text"],
    title="ATE Computation",
    description="Upload the groundtruth and two trajectory files to compute the Absolute Trajectory Errors."
)

if __name__ == "__main__":
    iface.launch()
