#!/usr/bin/env python
import os
import cv2
import rospy
import rosbag
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped

# Initialize the CvBridge class
bridge = CvBridge()

# Specify the ROS bag file
bag_file = '/home/ubuntu/Downloads/rgbd_dlo.bag'

# Determine the output folder name based on the bag file name (excluding the file extension)
output_folder = os.path.splitext(bag_file)[0]

# Create output directories
rgb_dir = os.path.join(output_folder, 'rgb')
depth_dir = os.path.join(output_folder, 'depth')
os.makedirs(rgb_dir, exist_ok=True)
os.makedirs(depth_dir, exist_ok=True)

# Initialize txt files
rgb_txt_path = os.path.join(output_folder, 'rgb.txt')
depth_txt_path = os.path.join(output_folder, 'depth.txt')
gt_txt_path = os.path.join(output_folder, 'groundtruth.txt')

# Open txt files to write
rgb_txt_file = open(rgb_txt_path, 'w')
depth_txt_file = open(depth_txt_path, 'w')
gt_txt_file = open(gt_txt_path, 'w')

# Specify topics
rgb_topic = '/camera/color/image_raw'
depth_topic = '/camera/aligned_depth_to_color/image_raw'
gt_topic = '/robot/dlo/odom_node/pose'

# Open the ROS bag file
bag = rosbag.Bag(bag_file, 'r')

# Process messages
for topic, msg, t in bag.read_messages(topics=[rgb_topic, depth_topic, gt_topic]):
    timestamp = t.to_sec()
    
    if topic == rgb_topic:
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV
        rgb_filename = f"{timestamp}.png"
        cv2.imwrite(os.path.join(rgb_dir, rgb_filename), cv_image_rgb)
        rgb_txt_file.write(f"{timestamp} rgb/{rgb_filename}\n")

    elif topic == depth_topic:
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        depth_filename = f"{timestamp}.png"
        cv2.imwrite(os.path.join(depth_dir, depth_filename), cv_image)  # Saving raw depth values
        depth_txt_file.write(f"{timestamp} depth/{depth_filename}\n")
    
    elif topic == gt_topic:
        # Directly access pose attributes without an additional 'pose' nesting
        pose = msg.pose
        gt_txt_file.write(f"{timestamp} {pose.position.x} {pose.position.y} {pose.position.z} "
                        f"{pose.orientation.x} {pose.orientation.y} {pose.orientation.z} {pose.orientation.w}\n")

# Close the bag file and txt files
bag.close()
rgb_txt_file.close()
depth_txt_file.close()
gt_txt_file.close()

print(f"Dataset extracted to {output_folder}")
