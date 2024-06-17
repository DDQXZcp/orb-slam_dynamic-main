"""
This script plots a single trajectory.
"""

import sys
import numpy as np
import argparse
import associate

def plot_traj(ax, stamps, traj, style, color):
    """
    Plot a trajectory using matplotlib. 
    
    Input:
    ax -- the plot
    stamps -- time stamps (1xn)
    traj -- trajectory (3xn)
    style -- line style
    color -- line color
    
    """
    stamps.sort()
    interval = np.median([s - t for s, t in zip(stamps[1:], stamps[:-1])])
    x = []
    y = []
    last = stamps[0]
    for i in range(len(stamps)):
        if stamps[i] - last < 2 * interval:
            x.append(traj[i][0])
            y.append(traj[i][1])
        elif len(x) > 0:
            ax.plot(x, y, style, color=color)
            x = []
            y = []
        last = stamps[i]
    if len(x) > 0:
        ax.plot(x, y, style, color=color)
            

if __name__ == "__main__":
    # parse command line
    parser = argparse.ArgumentParser(description='''
    This script plots a single trajectory. 
    ''')
    parser.add_argument('trajectory_file', help='trajectory file (format: timestamp tx ty tz qx qy qz qw)')
    parser.add_argument('--plot', help='plot the trajectory to an image (format: png)', required=True)
    parser.add_argument('--timestamp', help='plot trajectory up to this timestamp', type=float, default=None)
    args = parser.parse_args()

    traj_list = associate.read_file_list(args.trajectory_file)

    stamps = list(traj_list.keys())
    stamps.sort()
    
    if args.timestamp:
        stamps = [stamp for stamp in stamps if stamp <= args.timestamp]
    
    xyz = np.matrix([[float(value) for value in traj_list[b][0:3]] for b in stamps]).transpose()

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.pylab as pylab
    from matplotlib.patches import Ellipse
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot_traj(ax, stamps, xyz.transpose().A, '-', "blue")
    
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_xlim([0, 6])
    ax.set_ylim([-3, 3])
    plt.savefig(args.plot, dpi=90)