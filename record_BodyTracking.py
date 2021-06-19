import sys
sys.path.insert(1, 'pyKinectAzure/')

import numpy as np
from pyKinectAzure import pyKinectAzure, _k4a
import record_tool
import cv2



# Path to the module
# TODO: Modify with the path containing the k4a.dll from the Azure Kinect SDK
modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
bodyTrackingModulePath = 'C:\\Program Files\\Azure Kinect Body Tracking SDK\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll'
# under x86_64 linux please use r'/usr/lib/x86_64-linux-gnu/libk4a.so'
# In Jetson please use r'/usr/lib/aarch64-linux-gnu/libk4a.so'


if __name__ == "__main__":

	pyK4A = pyKinectAzure.pyKinectAzure(modulePath)	# 必須載入k4a.dll才不會出錯
	recorder = record_tool.load_record(modulePath)
	
	# Open record
	recorder.playback_open('./record/test01.mkv')
	

	# Modify camera configuration
	device_config = pyK4A.config
	device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = _k4a.K4A_DEPTH_MODE_NFOV_UNBINNED
	print(device_config)

	# Initialize the body tracker
	pyK4A.record_bodyTracker_start(bodyTrackingModulePath, recorder.playback_get_calibration())

	while True:
		# 確認是否還有下一幀
		try:
			pyK4A.capture_handle = recorder.get_capture()
			next_frame = True
		except:
			next_frame = False
			break

		if next_frame:
			# Get the depth image from the capture
			depth_image_handle = recorder.capture_get_depth_image()

			if depth_image_handle:

				# Perform body detection
				pyK4A.bodyTracker_update()

				# Read and convert the image data to numpy array:
				depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
				depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results  
				depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_GRAY2RGB) 

				# Get body segmentation image
				body_image_color = pyK4A.bodyTracker_get_body_segmentation()

				# Overlay body segmentation on depth image
				combined_image = cv2.addWeighted(depth_color_image, 0.8, body_image_color, 0.2, 0)

				# Draw the skeleton
				for body in pyK4A.body_tracker.bodiesNow:
					skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton)
					combined_image = pyK4A.body_tracker.draw2DSkeleton(skeleton2D, body.id, combined_image)


				cv2.imshow('Segmented Depth Image',combined_image)
				k = cv2.waitKey(1)

				if k==27:    # Esc key to stop
					break