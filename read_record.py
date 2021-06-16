import sys
sys.path.insert(1, 'pyKinectAzure/')

import numpy as np
from pyKinectAzure import pyKinectAzure, _k4a
import record
import cv2



# Path to the module
# TODO: Modify with the path containing the k4a.dll from the Azure Kinect SDK
modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
bodyTrackingModulePath = 'C:\\Program Files\\Azure Kinect Body Tracking SDK\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll'
# under x86_64 linux please use r'/usr/lib/x86_64-linux-gnu/libk4a.so'
# In Jetson please use r'/usr/lib/aarch64-linux-gnu/libk4a.so'


if __name__ == "__main__":

	pyK4A = pyKinectAzure.pyKinectAzure(modulePath)	# 必須載入k4a.dll才不會出錯
	recorder = record.load_record(modulePath)
	
	# Open record
	recorder.playback_open('./record/test.mkv')
	recorder.get_capture()
	pyK4A.device_open()
	pyK4A.capture_handle = recorder.capture_handle
	

	# Modify camera configuration
	device_config = pyK4A.config
	device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = _k4a.K4A_DEPTH_MODE_NFOV_UNBINNED
	print(device_config)


	# Initialize the body tracker
	pyK4A.bodyTracker_start(bodyTrackingModulePath)

	
	# Get the depth image from the capture
	depth_image_handle = pyK4A.capture_get_depth_image()
	if depth_image_handle:
		# Read and convert the image data to numpy array:
		depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
		depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results  
		depth_color_image = cv2.applyColorMap(depth_color_image, cv2.COLORMAP_JET)
		cv2.namedWindow('Colorized Depth Image',cv2.WINDOW_NORMAL)
		cv2.imshow('Colorized Depth Image',depth_color_image)
		k = cv2.waitKey(1)

		# Get body segmentation image
		# body_image_color = pyK4A.bodyTracker_get_body_segmentation()