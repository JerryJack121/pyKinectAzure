import _k4arecord
import _k4a
from _k4arecordTypes import *
from _k4atypes import *
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
		self.calibration = 	_k4a.k4a_calibration_t()

	def playback_open(self, filepath):
		self.k4arecord.k4a_playback_open(filepath.encode('utf-8'), self.playback_handle)
	
	def	playback_close(self):
		self.k4arecord.k4a_playback_close(self.playback_handle)
	
	def get_capture(self):

			result = self.k4arecord.k4a_playback_get_next_capture(self.playback_handle, self.capture_handle)
			if result == K4A_RESULT_SUCCEEDED:
				return self.capture_handle
			else:
				return None

		
		
	def capture_get_depth_image(self):
		return(self.k4a.k4a_capture_get_depth_image(self.capture_handle))

	def capture_get_color_image(self):
		return self.k4a.k4a_capture_get_color_image(self.capture_handle)
	
	def playback_get_calibration(self):
		self.k4arecord.k4a_playback_get_calibration(self.playback_handle, self.calibration)
		return self.calibration