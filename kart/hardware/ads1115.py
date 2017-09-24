"""
Module wrapping C code to read the I2C-attached ADS1115 ADC.
Used to measure the angle of the steering wheel.
"""

from ctypes import *
from os import strerror

clib = CDLL("libads1115.so", use_errno=True)

class c_ads1115(Structure):
	pass

c_ads1115_p = POINTER(c_ads1115)

# [XXX] obnoxious hack: because the ctypes library doesn't support enum types,
# define all of our configuration parameters as integers and blindly assume
# that they will always have the same binary representation as the respective
# enum constants in the C header.

MUX_CONFIG_DEFAULT = c_int(-1)
MUX_CONFIG_DIFF_AIN0_AIN1 = c_int(0x0)
MUX_CONFIG_DIFF_AIN0_AIN3 = c_int(0x1)
MUX_CONFIG_DIFF_AIN1_AIN3 = c_int(0x2)
MUX_CONFIG_DIFF_AIN2_AIN3 = c_int(0x3)
MUX_CONFIG_SINGLE_AIN0 = c_int(0x4)
MUX_CONFIG_SINGLE_AIN1 = c_int(0x5)
MUX_CONFIG_SINGLE_AIN2 = c_int(0x6)
MUX_CONFIG_SINGLE_AIN3 = c_int(0x7)

PGA_GAIN_DEFAULT = c_int(-1)
PGA_GAIN_6V144 = c_int(0x0)
PGA_GAIN_4V096 = c_int(0x1)
PGA_GAIN_2V048 = c_int(0x2)
PGA_GAIN_1V024 = c_int(0x3)
PGA_GAIN_0V512 = c_int(0x4)
PGA_GAIN_0V256 = c_int(0x5)

MODE_DEFAULT = c_int(-1)
MODE_CONTINUOUS = c_int(0x0)
MODE_ONE_SHOT = c_int(0x1)

DATA_RATE_DEFAULT = c_int(-1)
DATA_RATE_8SPS = c_int(0x0)
DATA_RATE_16SPS = c_int(0x1)
DATA_RATE_32SPS = c_int(0x2)
DATA_RATE_64SPS = c_int(0x3)
DATA_RATE_128SPS = c_int(0x4)
DATA_RATE_250SPS = c_int(0x5)
DATA_RATE_475SPS = c_int(0x6)
DATA_RATE_860SPS = c_int(0x7)

def ads1115_open_errcheck(res, func, args):
	if not bool(res):
		raise OSError("error setting up ADS1115 device at I2C address 0x%.2x on device %s: %s" % (
			args[1],
			str(args[0], encoding="UTF-8"),
			strerror(get_errno())
		))
	return res

ads1115_open = clib.ads1115_open
ads1115_open.argtypes = [c_char_p, c_uint8, c_int, c_int, c_int, c_int]
ads1115_open.restype = c_ads1115_p
ads1115_open.errcheck = ads1115_open_errcheck 

def ads1115_config_errcheck(res, func, args):
	if res != 0:
		raise OSError("error configuring ADS1115 device: %s" % strerror(get_errno()))
	return res

ads1115_config = clib.ads1115_config
ads1115_config.argtypes = [c_ads1115_p, c_int, c_int, c_int, c_int]
ads1115_config.restype = c_int
ads1115_config.errcheck = ads1115_config_errcheck

def ads1115_sample_errcheck(res, func, args):
	if res != 0:
		raise OSError("error fetching sample data from ADS1115 device: %s" % strerror(get_errno()))
	return res

ads1115_sample = clib.ads1115_sample
ads1115_sample.argtypes = [c_ads1115_p, POINTER(c_int6)]
ads1115_sample.restype = c_int
ads1115_sample.errcheck = ads1115_sample_errcheck

ads1115_free = clib.ads1115_free
ads1115_free.argtypes = [c_ads1115_p]
ads1115_free.restype = None

class Ads1115:
	def __init__(self, device_file, bus_address, mux_config, pga_config, mode, data_rate):
		self.ads = None
		self.ads = ads1115_open(
			bytes(device_file, encoding="UTF-8"),
			bus_address,
			mux_config,
			pga_config,
			mode,
			data_rate
		)

	def config(self, mux_config, pga_config, mode, data_rate):
		ads1115_config(self.ads, mux_config, mode, data_rate)

	def sample(self):
		tmp = c_int16(0)
		ads1115_sample(self.ads, pointer(tmp))
		return tmp.value

	def free(self):
		if self.ads:
			ads1115_free(self.ads)
			self.ads = None

	def __del__(self):
		self.free()

	def __exit__(self):
		self.free()
