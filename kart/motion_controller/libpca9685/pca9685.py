
from ctypes import *
from os import strerror

clib = CDLL("libpca9685.so", use_errno=True)

class c_pca9685(Structure):
	_fields_ =	[("fd", c_int),
			 ("freq", c_uint)]
c_pca9685_p = POINTER(c_pca9685)

def pca9685_open_errcheck(res, func, args):
	if not bool(res):
		raise OSError("error opening I2C address 0x%.2x on device %s: %s" % (
			args[1],
			str(args[0], encoding="UTF-8"),
			strerror(get_errno())
		))
	return res

pca9685_open = clib.pca9685_open
pca9685_open.argtypes = [c_char_p, c_uint8]
pca9685_open.restype = c_pca9685_p
pca9685_open.errcheck = pca9685_open_errcheck 

pca9685_activate = clib.pca9685_activate
pca9685_activate.argtypes = [c_pca9685_p, c_uint]
pca9685_activate.restype = c_int

pca9685_set_freq = clib.pca9685_set_freq
pca9685_set_freq.argtypes = [c_pca9685_p, c_uint]
pca9685_set_freq.resype = c_int

pca9685_set_duty_cycle = clib.pca9685_set_duty_cycle
pca9685_set_duty_cycle.argtypes = [c_pca9685_p, c_uint8, c_double]
pca9685_set_duty_cycle.restype = c_int

pca9685_set_pulse_width = clib.pca9685_set_pulse_width
pca9685_set_pulse_width.argtypes = [c_pca9685_p, c_uint8, c_uint]
pca9685_set_pulse_width.restype = c_int

pca9685_shutdown = clib.pca9685_shutdown
pca9685_shutdown.argtypes = [c_pca9685_p]
pca9685_shutdown.restype = c_int

def pca9685_io_errcheck(res, func, args):
	if func is pca9685_activate:
		verb = "activating"
	elif func is pca9685_set_freq:
		verb = "setting the frequency of"
	elif func is pca9685_set_duty_cycle:
		verb = "setting duty cycle on"
	elif func is pca9685_set_pulse_width:
		verb = "setting pulse width on"
	elif func is pca9685_shutdown:
		verb = "shutting down"

	if res != 0:
		raise OSError("error %s PCA9685: %s" % (verb, strerror(get_errno())))

pca9685_activate.errcheck = pca9685_io_errcheck
pca9685_set_freq.errcheck = pca9685_io_errcheck
pca9685_set_duty_cycle.errcheck = pca9685_io_errcheck
pca9685_set_pulse_width.errcheck = pca9685_io_errcheck
pca9685_shutdown.errcheck = pca9685_io_errcheck

pca9685_close = clib.pca9685_close
pca9685_close.argtypes = [c_pca9685_p]
pca9685_close.restype = None

class PwmChannel:
	def __init__(self, chip, channel):
		if not isinstance(chip, PwmChip):
			raise TypeError("expected PwmChip, got " + type(chip))
		self.chip = chip
		self.channel = channel

	def set_duty_cycle(self, duty_cycle):
		self.chip.set_duty_cycle(self.channel, duty_cycle)
	duty_cycle = property(fset=set_duty_cycle)

	def set_pulse_width(self, pulse_width):
		self.chip.set_pulse_width(self.channel, pulse_width)
	pulse_width = property(fset=set_pulse_width)

class PwmChip:
	def __init__(self, device_file, bus_address):
		self.pca = None
		self.pca = pca9685_open(bytes(device_file, encoding="UTF-8"), bus_address)

	def __enter__(self): pass

	def activate(self, frequency=0):
		pca9685_activate(self.pca, frequency)

	def set_freq(self, frequency):
		pca9685_set_freq(self.pca, frequency)

	def get_channel(self, channel):
		return PwmChannel(self, channel)

	def set_duty_cycle(self, channel, duty_cycle):
		pca9685_set_duty_cycle(self.pca, channel, duty_cycle)

	def set_pulse_width(self, channel, usecs):
		pca9685_set_pulse_width(self.pca, channel, usecs)

	def shutdown(self):
		pca9685_shutdown(self.pca)

	def close(self):
		if self.pca:
			pca9685_close(self.pca)
			self.pca = None

	def __exit__(self, ex_type, ex_value, backtrace):
		self.shutdown()

	def __del__(self):
		self.close()
