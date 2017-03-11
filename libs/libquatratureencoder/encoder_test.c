
#include <stdio.h>
#include <stdlib.h>
#include <err.h>
#include <signal.h>

#include <quadrature_encoder.h>

#define GPIO_A				23
#define GPIO_B				24

struct encoder_ctx *ctx = NULL;

void cleanup(int dummy) {
	if (ctx) {
		qenc_terminate_read_loop(ctx);
		free(ctx);
	}

	exit(EXIT_FAILURE);
}

int main(void) {
	int enc_val;
	struct timespec delay = {
		.tv_sec = 0,
		.tv_nsec = 500000000,
	};
	struct sigaction int_handler = {
		.sa_handler = cleanup,
	};
	struct timespec last_sampling;

	if (sigaction(SIGINT, &int_handler, NULL))
		err(EXIT_FAILURE, "error establishing interrupt handler");

	if (!(ctx = qenc_launch_read_loop(GPIO_A, GPIO_B)))
		err(EXIT_FAILURE, "error launching read loop");

	while (1) {
		if (qenc_get_encoder_value(ctx, &enc_val, &last_sampling))
			warn("error reading encoder value");
		else
			printf(" < %+7d (%lu.%09ld) >\n", enc_val, last_sampling.tv_sec, last_sampling.tv_nsec);

		if (nanosleep(&delay, NULL))
			warn("error in nanosleep()");
	}

	return 0; /* NOT REACHED */
}
