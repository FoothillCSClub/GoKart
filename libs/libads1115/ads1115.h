
#ifndef _ADS1115_H_
#define _ADS1115_H_

#include <stdint.h>

#define ADS1115_REG_CONVERSION			0x0
#define ADS1115_REG_CONFIG			0x1
#define ADS1115_REG_THRESH_L			0x2
#define ADS1115_REG_THRESH_H			0x3

#define ADS1115_OP_STATUS_MASK			0x8000
#define ADS1115_MUX_CONFIG_MASK			0x7000
#define ADS1115_MUX_CONFIG_OFFSET		12
#define ADS1115_PGA_GAIN_MASK			0x0e00
#define ADS1115_PGA_GAIN_OFFSET			9
#define ADS1115_MODE_MASK			0x0100
#define ADS1115_MODE_OFFSET			8
#define ADS1115_DATA_RATE_MASK			0x00e0
#define ADS1115_DATA_RATE_OFFSET		5

struct ads1115 {
	int fd;
	uint16_t config;
	uint8_t regnum;
};

typedef struct ads1115 *ads1115_t;

enum ads1115_mux_config {
	ADS1115_MUX_CONFIG_DEFAULT = -1,
	ADS1115_MUX_CONFIG_DIFF_AIN0_AIN1 = 0x0,
	ADS1115_MUX_CONFIG_DIFF_AIN0_AIN3 = 0x1,
	ADS1115_MUX_CONFIG_DIFF_AIN1_AIN3 = 0x2,
	ADS1115_MUX_CONFIG_DIFF_AIN2_AIN3 = 0x3,
	ADS1115_MUX_CONFIG_SINGLE_AIN0 = 0x4,
	ADS1115_MUX_CONFIG_SINGLE_AIN1 = 0x5,
	ADS1115_MUX_CONFIG_SINGLE_AIN2 = 0x6,
	ADS1115_MUX_CONFIG_SINGLE_AIN3 = 0x7,
};

enum ads1115_pga_gain {
	ADS1115_PGA_GAIN_DEFAULT = -1,
	ADS1115_PGA_GAIN_6V144 = 0x0,
	ADS1115_PGA_GAIN_4V096 = 0x1,
	ADS1115_PGA_GAIN_2V048 = 0x2,
	ADS1115_PGA_GAIN_1V024 = 0x3,
	ADS1115_PGA_GAIN_0V512 = 0x4,
	ADS1115_PGA_GAIN_0V256 = 0x5,
};

enum ads1115_mode {
	ADS1115_MODE_DEFAULT = -1,
	ADS1115_MODE_CONTINUOUS = 0x0,
	ADS1115_MODE_ONE_SHOT = 0x1,
};

enum ads1115_data_rate {
	ADS1115_DATA_RATE_DEFAULT = -1,
	ADS1115_DATA_RATE_8SPS = 0x0,
	ADS1115_DATA_RATE_16SPS = 0x1,
	ADS1115_DATA_RATE_32SPS = 0x2,
	ADS1115_DATA_RATE_64SPS = 0x3,
	ADS1115_DATA_RATE_128SPS = 0x4,
	ADS1115_DATA_RATE_250SPS = 0x5,
	ADS1115_DATA_RATE_475SPS = 0x6,
	ADS1115_DATA_RATE_860SPS = 0x7,
};

ads1115_t ads1115_open(
	const char *dev,
	uint8_t slave_addr,
	enum ads1115_mux_config muxconf,
	enum ads1115_pga_gain pgaconf,
	enum ads1115_mode mode,
	enum ads1115_data_rate datarate
);

int ads1115_config(
	ads1115_t ads,
	enum ads1115_mux_config muxconf,
	enum ads1115_pga_gain pgaconf,
	enum ads1115_mode mode,
	enum ads1115_data_rate datarate
);

int ads1115_sample(ads1115_t ads, int16_t *res);

void ads1115_free(ads1115_t ads);

#endif /* _ADS1115_H_ */
