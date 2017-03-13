
"""
Wrapper for libquadratureencoder, a C library which uses a background
thread to count the number of rotations in an encoder sensor
"""

from ctypes import *
from os import strerror

clib = CDLL("libquadratureencoder.so", use_errno=True)

def qenc_launch_read_loop_errcheck(res, func, args):
	if not bool(res):
		raise OSError("error launching backround thread to read encoder ticks on GPIOs %u and %u: %s" % (
			args[0], args[1],
			strerror(get_errno())
		))
	return res

qenc_launch_read_loop = clib.qenc_launch_read_loop
qenc_launch_read_loop.argtypes = [c_uint, c_uint]
qenc_launch_read_loop.restype = c_void_p
qenc_launch_read_loop.errcheck = qenc_launch_read_loop_errcheck

def qenc_get_encoder_value_errcheck(res, func, args):
	if res != 0:
		raise OSError("error fetching encoder from background thread: %s" % strerror(get_errno()))
	return res

qenc_get_encoder_value = clib.qenc_get_encoder_value
qenc_get_encoder_value.argtypes = [c_void_p, POINTER(c_int), c_void_p]
qenc_get_encoder_value.restype = c_int
qenc_get_encoder_value.errcheck = qenc_get_encoder_value_errcheck

def qenc_terminate_read_loop_errcheck(res, func, args):
	if res != 0:
		raise OSError("error terminating backround encoder read loop: %s" % strerror(get_errno()))
	return res

qenc_terminate_read_loop = clib.qenc_terminate_read_loop
qenc_terminate_read_loop.argtypes = [c_void_p]
qenc_terminate_read_loop.restype = c_int
qenc_terminate_read_loop.errcheck = qenc_terminate_read_loop_errcheck

class QuadratureEncoder:
	def __init__(self, gpio_a, gpio_b):
		self.enc = None
		self.enc = qenc_launch_read_loop(gpio_a, gpio_b)

	def __enter__(self):
		return self

	def get_value(self):
		val = c_int()
		qenc_get_encoder_value(self.enc, byref(val), None)
		return val.value

	def __int__(self):
		return self.get_value()

	def terminate(self):
		if self.enc:
			qenc_terminate_read_loop(self.enc)
			self.enc = None

	def __exit__(self, ex_type, ex_value, backtrace):
		self.terminate()

	def __del__(self):
		self.terminate()
