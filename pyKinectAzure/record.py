import _k4arecord
import _k4a
import numpy as np

class record:

	def __init__(self, modulePath, device_handle, device_configuration,filepath):

		self.k4arecord = _k4arecord.k4arecord(modulePath)
		self.record_handle = _k4arecord.k4a_record_t()
		self.header_written = False

		self.create_recording(device_handle, device_configuration, filepath)

	def __del__(self):

		self.close()

	def create_recording(self, device_handle, device_configuration, filepath):
		_k4arecord.VERIFY(self.k4arecord.k4a_record_create(filepath.encode('utf-8'), device_handle, device_configuration, self.record_handle),"Failed to create recording!")


	def is_valid(self):
		return self.record_handle != None

	def close(self):
		if self.is_valid():
			self.k4arecord.k4a_record_close(self.record_handle)
			self.record_handle = None

	def flush(self):
		if self.is_valid():		
			_k4arecord.VERIFY(self.k4arecord.k4a_record_flush(self.record_handle),"Failed to flush!")

	def write_header(self):
		if self.is_valid():
			_k4arecord.VERIFY(self.k4arecord.k4a_record_write_header(self.record_handle),"Failed to write header!")

	def write_capture(self, capture_handle):
			
		if not self.is_valid():
			raise NameError('Recording not found')

		if not self.header_written:
			self.write_header()
			self.header_written = True
		_k4arecord.VERIFY(self.k4arecord.k4a_record_write_capture(self.record_handle, capture_handle),"Failed to write capture!")

class load_record:

	def __init__(self, modulePath):
		self.k4a = _k4a.k4a()
		self.k4arecord = _k4arecord.k4arecord(modulePath)
		self.playback_handle = _k4arecord.k4a_playback_t()
		self.capture_handle = _k4a.k4a_capture_t()	

	def playback_open(self, filepath):
		self.k4arecord.k4a_playback_open(filepath.encode('utf-8'), self.playback_handle)
	
	def get_capture(self):
		_k4arecord.VERIFY(self.k4arecord.k4a_playback_get_next_capture(self.playback_handle, self.capture_handle), "Get capture failed!")
		
	def capture_get_depth_image(self):
		return(self.k4a.k4a_capture_get_depth_image(self.capture_handle))
	
	def image_get_buffer(self, image_handle):
		"""Get the image buffer.

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		ctypes.POINTER(ctypes.c_uint8): The function will return NULL if there is an error, and will normally return a pointer to the image buffer.
										Since all k4a_image_t instances are created with an image buffer, this function should only return NULL if the
										image_handle is invalid.

		Remarks:
		Use this buffer to access the raw image data.
		"""

		return self.k4a.k4a_image_get_buffer(image_handle)

	def image_get_size(self, image_handle):
		"""Get the image buffer size.

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		int: The function will return 0 if there is an error, and will normally return the image size.
		Since all k4a_image_t instances are created with an image buffer, this function should only return 0 if the
		image_handle is invalid.

		Remarks:
		Use this function to know what the size of the image buffer is returned by k4a_image_get_buffer().
		"""

		return int(self.k4a.k4a_image_get_size(image_handle))
	
	def image_get_width_pixels(self, image_handle):
		"""Get the image width in pixels.

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		int: This function is not expected to fail, all k4a_image_t's are created with a known width. If the part
		image_handle is invalid, the function will return 0.
		"""

		return int(self.k4a.k4a_image_get_width_pixels(image_handle))

	def image_get_height_pixels(self, image_handle):
		"""Get the image height in pixels.

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		int: This function is not expected to fail, all k4a_image_t's are created with a known height. If the part
		image_handle is invalid, the function will return 0.
		"""

		return int(self.k4a.k4a_image_get_height_pixels(image_handle))
	
	def image_get_format(self, image_handle):
		"""Get the format of the image.

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		int: This function is not expected to fail, all k4a_image_t's are created with a known format. If the
		image_handle is invalid, the function will return ::K4A_IMAGE_FORMAT_CUSTOM.

		Remarks:
		Use this function to determine the format of the image buffer.
		"""

		return int(self.k4a.k4a_image_get_format(image_handle))

	def image_convert_to_numpy(self, image_handle):
		"""Get the image data as a numpy array

		Parameters:
		image_handle (k4a_image_t): Handle to the Image

		Returns:
		numpy.ndarray: Numpy array with the image data
		"""

		# Get the pointer to the buffer containing the image data
		buffer_pointer = self.image_get_buffer(image_handle)

		# Get the size of the buffer
		image_size = self.image_get_size(image_handle)
		image_width = self.image_get_width_pixels(image_handle)
		image_height = self.image_get_height_pixels(image_handle)

		# Get the image format
		image_format = self.image_get_format(image_handle)

		# Read the data in the buffer
		buffer_array = np.ctypeslib.as_array(buffer_pointer,shape=(image_size,))

		# Parse buffer based on image format
		if image_format == _k4a.K4A_IMAGE_FORMAT_COLOR_MJPG:
			return cv2.imdecode(np.frombuffer(buffer_array, dtype=np.uint8), -1)
		elif image_format == _k4a.K4A_IMAGE_FORMAT_COLOR_NV12:
			yuv_image = np.frombuffer(buffer_array, dtype=np.uint8).reshape(int(image_height*1.5),image_width)
			return cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_NV12)
		elif image_format == _k4a.K4A_IMAGE_FORMAT_COLOR_YUY2:
			yuv_image = np.frombuffer(buffer_array, dtype=np.uint8).reshape(image_height,image_width,2)
			return cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_YUY2)
		elif image_format == _k4a.K4A_IMAGE_FORMAT_COLOR_BGRA32:
			return np.frombuffer(buffer_array, dtype=np.uint8).reshape(image_height,image_width,4)
		elif image_format == _k4a.K4A_IMAGE_FORMAT_DEPTH16:
			return np.frombuffer(buffer_array, dtype="<u2").reshape(image_height,image_width)#little-endian 16 bits unsigned Depth data
		elif image_format == _k4a.K4A_IMAGE_FORMAT_IR16:
			return np.frombuffer(buffer_array, dtype="<u2").reshape(image_height,image_width)#little-endian 16 bits unsigned IR data. For more details see: https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.2.x/namespace_microsoft_1_1_azure_1_1_kinect_1_1_sensor_a7a3cb7a0a3073650bf17c2fef2bfbd1b.html
		elif image_format == _k4a.K4A_IMAGE_FORMAT_CUSTOM8:
			return np.frombuffer(buffer_array, dtype="<u1").reshape(image_height,image_width)
