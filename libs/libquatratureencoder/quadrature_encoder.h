
#ifndef _QUADRATURE_ENCODER_H_
#define _QUADRATURE_ENCODER_H_

struct encoder_ctx {
	pthread_mutex_t lock;
	int value;

	int a_fd;
	int b_fd;

	int a_value;
	int b_value;

	unsigned a_number;
	unsigned b_number;

	unsigned err_count;
	int errnum;

	struct timespec last_sampletime;

	pthread_t thread;
};

struct encoder_ctx *qenc_launch_read_loop(unsigned gpio_a, unsigned gpio_b);
int qenc_get_encoder_value(struct encoder_ctx *ctx, int *enc_val, struct timespec *last_sampling);
int qenc_terminate_read_loop(struct encoder_ctx *ctx);

#endif /* _QUADRATURE_ENCODER_H_ */
