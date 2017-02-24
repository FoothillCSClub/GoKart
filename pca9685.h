
#ifndef _PCA9685_H_
#define _PCA9685_H_

#include <stdint.h>

struct pca9685 {
	int fd;
	unsigned freq;
};

struct pca9685 *pca9685_open(const char *dev, uint8_t bus_addr);
int pca9685_activate(struct pca9685 *pca, unsigned freq);
int pca9685_set_freq(struct pca9685 *pca, unsigned freq);
int pca9685_set_duty_cycle(struct pca9685 *pca, uint8_t channel, double dc);
void pca9685_close(struct pca9685 *pca);

#endif /* _PCA9685_H_ */
