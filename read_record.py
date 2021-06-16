import sys
sys.path.insert(1, 'pyKinectAzure/')

import numpy as np
from pyKinectAzure import pyKinectAzure, _k4a
import record
import cv2



# Path to the module
# TODO: Modify with the path containing the k4a.dll from the Azure Kinect SDK
modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
# under x86_64 linux please use r'/usr/lib/x86_64-linux-gnu/libk4a.so'
# In Jetson please use r'/usr/lib/aarch64-linux-gnu/libk4a.so'

if __name__ == "__main__":

	pyK4A = pyKinectAzure.pyKinectAzure(modulePath)	# 必須載入k4a.dll才不會出錯
	recorder = record.load_record(modulePath)
	recorder.playback_open('./record/test.mkv')
	recorder.get_capture()

	# Get the depth image from the capture
	depth_image_handle = recorder.capture_get_depth_image()
	if depth_image_handle:
		# Read and convert the image data to numpy array:
		depth_image = recorder.image_convert_to_numpy(depth_image_handle)
		depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results  
		depth_color_image = cv2.applyColorMap(depth_color_image, cv2.COLORMAP_JET)
		cv2.namedWindow('Colorized Depth Image',cv2.WINDOW_NORMAL)
		cv2.imshow('Colorized Depth Image',depth_color_image)
		k = cv2.waitKey(1)