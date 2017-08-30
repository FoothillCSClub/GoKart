
#include <stdio.h>
#include <err.h>
#include <stdlib.h>
#include <unistd.h>

#include "ads1115.h"

int main(void) {
	ads1115_t ads;
	uint16_t val;

	if (!(ads = ads1115_open(
		"/dev/i2c-1", 0x48,
		ADS1115_MUX_CONFIG_SINGLE_AIN0,
		ADS1115_PGA_GAIN_4V096,
		ADS1115_MODE_ONE_SHOT,
		ADS1115_DATA_RATE_250SPS
	)))
		err(EXIT_FAILURE, "error opening ADC device");

	while (1) {
		if (usleep(100000))
			err(EXIT_FAILURE, "error while sleeping");

		if (ads1115_sample(ads, &val))
			err(EXIT_FAILURE, "error retreiving sample from ADS");

		fprintf(stdout, "\rADC value = 0x%.4x", (unsigned) val);
		fflush(stdout);
	}

	return 0; /* NOT REACHED */
}
