
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <time.h>
#include <errno.h>
#include <endian.h>

#include <linux/i2c-dev.h>

#include "ads1115.h"

#define ALTER_CONFIG(reg, mask, offset, val)		((reg) = ((reg) & ~(mask)) | (((int) (val)) << (offset)))

static inline int set_reg_pointer(ads1115_t ads, uint8_t regnum) {
	if (ads->regnum != regnum && write(ads->fd, &regnum, sizeof(regnum)) < 0)
		return -1;
	ads->regnum = regnum;

	return 0;
}

static int get_reg(ads1115_t ads, uint8_t regnum, uint16_t *out) {
	uint16_t reg;

	if (
		set_reg_pointer(ads, regnum) ||
		read(ads->fd, &reg, sizeof(reg)) < 0
	)
		return -1;

	*out = be16toh(reg);

	return 0;
}

static int set_reg(ads1115_t ads, uint8_t regnum, uint16_t regval) {
	uint8_t data[sizeof(regnum) + sizeof(regval)];

	data[0] = regnum;
	*((uint16_t *) (data + sizeof(regnum))) = htobe16(regval);

	if (write(ads->fd, data, sizeof(data)) < 0)
		return -1;
	ads->regnum = regnum;

	return 0;
}

static inline long get_sps(ads1115_t ads) {
	switch ((enum ads1115_data_rate) ((ads->config & ADS1115_DATA_RATE_MASK) >> ADS1115_DATA_RATE_OFFSET)) {
		case ADS1115_DATA_RATE_8SPS:
			return 8;
		case ADS1115_DATA_RATE_16SPS:
			return 16;
		case ADS1115_DATA_RATE_32SPS:
			return 32;
		case ADS1115_DATA_RATE_64SPS:
			return 64;
		case ADS1115_DATA_RATE_128SPS:
			return 128;
		case ADS1115_DATA_RATE_250SPS:
			return 250;
		case ADS1115_DATA_RATE_475SPS:
			return 475;
		case ADS1115_DATA_RATE_860SPS:
			return 860;
		default:
			return 0;
	}
}

ads1115_t ads1115_open(
	const char *dev,
	uint8_t slave_addr,
	enum ads1115_mux_config muxconf,
	enum ads1115_pga_gain pgaconf,
	enum ads1115_mode mode,
	enum ads1115_data_rate datarate
) {
	ads1115_t ads = NULL;

	if (!(ads = malloc(sizeof(*ads))))
		return NULL;
	ads->fd = -1;

	if ((ads->fd = open(dev, O_RDWR)) < 0)
		goto fail;

	if (ioctl(ads->fd, I2C_SLAVE, slave_addr))
		goto fail;

	if (ads1115_config(ads, muxconf, pgaconf, mode, datarate))
		goto fail;

	return ads;

   fail:
	ads1115_free(ads);

	return NULL;
}

int ads1115_config(
	ads1115_t ads,
	enum ads1115_mux_config muxconf,
	enum ads1115_pga_gain pgaconf,
	enum ads1115_mode mode,
	enum ads1115_data_rate datarate
) {
	uint16_t config_reg;

	if (get_reg(ads, ADS1115_REG_CONFIG, &config_reg))
		return -1;

	if (muxconf != ADS1115_MUX_CONFIG_DEFAULT)
		ALTER_CONFIG(config_reg, ADS1115_MUX_CONFIG_MASK, ADS1115_MUX_CONFIG_OFFSET, muxconf);
	if (pgaconf != ADS1115_PGA_GAIN_DEFAULT)
		ALTER_CONFIG(config_reg, ADS1115_PGA_GAIN_MASK, ADS1115_PGA_GAIN_OFFSET, pgaconf);
	if (mode != ADS1115_MODE_DEFAULT)
		ALTER_CONFIG(config_reg, ADS1115_MODE_MASK, ADS1115_MODE_OFFSET, mode);
	if (datarate != ADS1115_DATA_RATE_DEFAULT)
		ALTER_CONFIG(config_reg, ADS1115_DATA_RATE_MASK, ADS1115_DATA_RATE_OFFSET, datarate);

	config_reg &= ~ADS1115_OP_STATUS_MASK;

	if (set_reg(ads, ADS1115_REG_CONFIG, config_reg))
		return -1;

	config_reg |= ADS1115_OP_STATUS_MASK;
	ads->config = config_reg;

	return 0;
}

int ads1115_sample(ads1115_t ads, int16_t *res) {
	enum ads1115_mode mode;
	int s;
	struct timespec waittime;
	struct timespec timer;

	mode = (enum ads1115_mode) ((ads->config & ADS1115_MODE_MASK) >> ADS1115_MODE_OFFSET);

	if (mode == ADS1115_MODE_ONE_SHOT) {
		if (set_reg(ads, ADS1115_REG_CONFIG, ads->config))
			return -1;

		waittime.tv_sec = 0;
		waittime.tv_nsec = 1000000000L / get_sps(ads);
		do {
			timer = waittime;
			do {
				s = nanosleep(&timer, &timer);
			} while (s && errno == EINTR && timer.tv_nsec > 0);
			if (s)
				return -1;

			if (get_reg(ads, ADS1115_REG_CONFIG, &ads->config))
				return -1;
		} while (!(ads->config & ADS1115_OP_STATUS_MASK));
	}

	if (get_reg(ads, ADS1115_REG_CONVERSION, res))
		return -1;

	return 0;
}

void ads1115_free(ads1115_t ads) {
	if (ads->fd >= 0)
		close(ads->fd);
	free(ads);
}
