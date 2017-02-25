
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <limits.h>
#include <time.h>
#include <errno.h>
#include <math.h>
#include <stdint.h>

#include <linux/i2c-dev.h>

#include "pca9685.h"

#define NUM_CHAN			16
#define PWM_INCREMENTS			4096
#define INTERNAL_OSC_HZ			25000000

#define MODE1_ADDR			0x00
#define MODE1_SLEEP			0x10
#define MODE1_ALLCALL			0x01
#define MODE1_RESTART			0x80
#define MODE2_ADDR			0x01
#define MODE2_OCH			0x08
#define CHAN_BASE_REG			0x06
#define CHAN_N_FULL_ON			0x10
#define CHAN_N_FULL_OFF			0x10
#define PRESCALE_ADDR			0xfe
#define PRESCALE_MIN			0x03
#define PRESCALE_MAX			0xff

struct pca9685 *pca9685_open(const char *dev, uint8_t bus_addr) {
	struct pca9685 *ret;

	if (!(ret = malloc(sizeof(*ret))))
		return NULL;

	if ((ret->fd = open(dev, O_RDWR)) < 0)
		goto fail;

	if (ioctl(ret->fd, I2C_SLAVE, bus_addr) < 0)
		goto fail;

	return ret;

   fail:
	pca9685_close(ret);

	return NULL;
}

int pca9685_activate(struct pca9685 *pca, unsigned freq) {
	int32_t mode1, mode2, prescale;
	struct timespec timer = {
		.tv_sec = 0,
		.tv_nsec = 500000,
	};

	if ((mode1 = i2c_smbus_read_byte_data(pca->fd, MODE1_ADDR)) < 0)
		return -1;

	if ((mode2 = i2c_smbus_read_byte_data(pca->fd, MODE2_ADDR)) < 0)
		return -1;

	if (!freq) {
		if ((prescale = i2c_smbus_read_byte_data(pca->fd, PRESCALE_ADDR)) < 0)
			return -1;
		pca->freq = round(INTERNAL_OSC_HZ / (PWM_INCREMENTS * (double)prescale));
	}

	mode1 &= ~(MODE1_RESTART | MODE1_SLEEP | MODE1_ALLCALL);
	mode2 |= MODE2_OCH;

	if (i2c_smbus_write_byte_data(pca->fd, MODE2_ADDR, mode2) < 0)
		return -1;

	if (freq && pca9685_set_freq(pca, freq))
		return -1;

	if (i2c_smbus_write_byte_data(pca->fd, MODE1_ADDR, mode1) < 0)
		return -1;

	// the datasheet says we have to wait 500us after flipping off the sleep bit
	while (timer.tv_nsec > 0)
		if (nanosleep(&timer, &timer) == 0)
			break;
		else if (errno != EINTR)
			return -1;

	return 0;
}

int pca9685_set_freq(struct pca9685 *pca, unsigned freq) {
	unsigned prescale;
	int32_t mode1;

	// frequency cannot be set while chip is active.
	if ((mode1 = i2c_smbus_read_byte_data(pca->fd, MODE1_ADDR)) < 0)
		return -1;
	if (!(mode1 & MODE1_SLEEP)) {
		errno = EINVAL;
		return -1;
	}

	prescale = (unsigned) round(INTERNAL_OSC_HZ / (PWM_INCREMENTS * (double) freq)) - 1;
	if (prescale < PRESCALE_MIN || prescale > PRESCALE_MAX) {
		errno = ERANGE;
		return -1;
	}

	if (i2c_smbus_write_byte_data(pca->fd, PRESCALE_ADDR, (uint8_t) prescale))
		return -1;

	pca->freq = freq;

	return 0;
}

int pca9685_set_duty_cycle(struct pca9685 *pca, uint8_t channel, double dc) {
	uint8_t on_lsb, on_msb, off_lsb, off_msb, chan_base_addr;
	unsigned width_increments;

	if (dc > 1.0 || dc < 0.0 || channel >= NUM_CHAN) {
		errno = ERANGE;
		return -1;
	}

	chan_base_addr = CHAN_BASE_REG + (channel * 4);

	if (dc == 1.0) {
		on_lsb = 0x00;
		on_msb = CHAN_N_FULL_ON;
		off_lsb = 0x00;
		off_msb = 0x00;
	} else if (dc == 0.0) {
		on_lsb = 0x00;
		on_msb = 0x00;
		off_lsb = 0x00;
		off_msb = CHAN_N_FULL_OFF;
	} else {
		on_lsb = 0x00;
		on_msb = 0x00;
		width_increments = round((PWM_INCREMENTS-1) * dc);
		off_lsb =  width_increments & 0x00ff;
		off_msb = (width_increments & 0x0f00) >> 8;
	}

	if (
		i2c_smbus_write_byte_data(pca->fd, chan_base_addr + 0,  on_lsb) ||
		i2c_smbus_write_byte_data(pca->fd, chan_base_addr + 1,  on_msb) ||
		i2c_smbus_write_byte_data(pca->fd, chan_base_addr + 2, off_lsb) ||
		i2c_smbus_write_byte_data(pca->fd, chan_base_addr + 3, off_msb)
	)
		return -1;

	return 0;
}

int pca9685_shutdown(struct pca9685 *pca) {
	int32_t mode1;

	if ((mode1 = i2c_smbus_read_byte_data(pca->fd, MODE1_ADDR)) < 0)
		return -1;

	mode1 &= ~MODE1_RESTART;
	mode1 |= MODE1_SLEEP;

	if (i2c_smbus_write_byte_data(pca->fd, MODE1_ADDR, mode1) < 0)
		return -1;

	return 0;
}

void pca9685_close(struct pca9685 *pca) {
	if (pca) {
		if (pca->fd >= 0)
			close(pca->fd);
		free(pca);
	}
}
