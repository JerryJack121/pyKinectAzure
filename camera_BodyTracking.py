import sys
sys.path.insert(1, 'pyKinectAzure/')

import numpy as np
from pyKinectAzure.pyKinectAzure import pyKinectAzure, _k4a
from kinectBodyTracker import kinectBodyTracker, _k4abt
import cv2
import time

from utils.utils import Util

# Path to the module
# TODO: Modify with the path containing the k4a.dll from the Azure Kinect SDK
# 修改路徑
modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
bodyTrackingModulePath = 'C:\\Program Files\\Azure Kinect Body Tracking SDK\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll'
# under x86_64 linux please use r'/usr/lib/x86_64-linux-gnu/libk4a.so'
# In Jetson please use r'/usr/lib/aarch64-linux-gnu/libk4a.so'

if __name__ == "__main__":

	# Initialize the library with the path containing the module
	pyK4A = pyKinectAzure(modulePath)

	# Open device
	pyK4A.device_open()

	# Modify camera configuration
	device_config = pyK4A.config
	device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = _k4a.K4A_DEPTH_MODE_NFOV_UNBINNED
	print(device_config)

	# Start cameras using modified configuration
	pyK4A.device_start_cameras(device_config)

	# Initialize the body tracker
	pyK4A.bodyTracker_start(bodyTrackingModulePath)

	k = 0
	while True:
		# Start time
		start = time.time()
		# Get capture
		pyK4A.device_get_capture()

		# Get the depth image from the capture
		depth_image_handle = pyK4A.capture_get_depth_image()


		# Check the image has been read correctly
		if depth_image_handle:

			# Perform body detection
			pyK4A.bodyTracker_update()

			# Read and convert the image data to numpy array:
			# 將深度圖像轉換為RGB三通道，用於可視化
			depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
			depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results 
			depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_GRAY2RGB) 

			# Get body segmentation image
			body_image_color = pyK4A.bodyTracker_get_body_segmentation()

			# 按比例重疊深度圖像與人體區塊圖像
			combined_image = cv2.addWeighted(depth_color_image, 0.8, body_image_color, 0.2, 0)

			# Draw the skeleton
			for body in pyK4A.body_tracker.bodiesNow:	# 遍覽畫面中出現的目標
				skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton)
				combined_image = pyK4A.body_tracker.draw2DSkeleton(skeleton2D, body.id, combined_image)
				# 取得3維關節座標
				skeleton3D = pyK4A.bodyTracker_3Dskeleton(body.skeleton)	

				util = Util(skeleton2D, skeleton3D, combined_image)
				# 顯示3維關節座標在輸出影像上
				# util.show_coordinate_on_2Dimage(['SHOULDER_RIGHT', 'ELBOW_RIGHT', 'WRIST_RIGHT'])	
				# 顯示關節角度在輸出影像上
				util.show_angel_on_2Dimage(['SHOULDER_RIGHT', 'ELBOW_RIGHT', 'WRIST_RIGHT'])	
				# 顯示3維關節座標在輸出影像上
				# util.show_coordinate_on_2Dimage(['SHOULDER_LEFT', 'ELBOW_LEFT', 'WRIST_LEFT'])	
				# 顯示關節角度在輸出影像上
				util.show_angel_on_2Dimage(['SHOULDER_LEFT', 'ELBOW_LEFT', 'WRIST_LEFT'])	

				combined_image = util.combined_image

			# Overlay body segmentation on depth image
			cv2.imshow('Segmented Depth Image',combined_image)
			k = cv2.waitKey(1)

			# End time
			end = time.time()
			# FPS
			print('FPS:{:.1f}'.format(1/(end-start)))

			# Release the image
			pyK4A.image_release(depth_image_handle)
			pyK4A.image_release(pyK4A.body_tracker.segmented_body_img)

		pyK4A.capture_release()
		pyK4A.body_tracker.release_frame()

		if k==27:    # Esc key to stop
			break
		elif k == ord('q'):
			cv2.imwrite('outputImage.jpg',combined_image)

	pyK4A.device_stop_cameras()
	pyK4A.device_close()