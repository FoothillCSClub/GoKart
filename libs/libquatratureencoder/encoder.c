
#include <stdio.h>
#include <pthread.h>
#include <time.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <poll.h>
#include <errno.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "quadrature_encoder.h"

#define BUF_SIZE			1024
#define GPIO_PREFIX			"/sys/class/gpio"
#define GPIO_EXPORT_FILE		GPIO_PREFIX "/export"
#define GPIO_UNEXPORT_FILE		GPIO_PREFIX "/unexport"
#define GPIO_EDGE_TYPE_NONE		"none"
#define GPIO_EDGE_TYPE_RISING		"rising"
#define GPIO_EDGE_TYPE_FALLING		"falling"
#define GPIO_EDGE_TYPE_BOTH		"both"
#define GPIO_DIR_IN			"in"
#define GPIO_DIR_OUT			"out"

static int stuff_file(const char *file, const char *string, size_t len) {
	FILE *fh;
	size_t s;
	int ret = 0;

	if (!(fh = fopen(file, "w")))
		return -1;

	len = (len == -1) ? strlen(string) : len;

	s = fwrite(string, 1, len, fh);
	if (s != len)
		ret = -1;

	if (fclose(fh))
		ret = -1;

	return ret;
}

static int send_export_number(unsigned number, const char *file) {
	char number_str[15];
	snprintf(number_str, sizeof(number_str), "%u", number);

	return stuff_file(file, number_str, -1);
}

static inline int export_gpio(unsigned number) {
	return send_export_number(number, GPIO_EXPORT_FILE);
}

static inline int unexport_gpio(unsigned number) {
	return send_export_number(number, GPIO_UNEXPORT_FILE);
}

static int set_gpio_direction(unsigned number, const char *dir) {
	char gpio_dir_file[FILENAME_MAX+1];

	snprintf(gpio_dir_file, sizeof(gpio_dir_file), GPIO_PREFIX "/gpio%u/direction", number);

	return stuff_file(gpio_dir_file, dir, -1);
}

static int set_gpio_edge(unsigned number, const char *edge) {
	char gpio_edge_file[FILENAME_MAX+1];

	snprintf(gpio_edge_file, sizeof(gpio_edge_file), GPIO_PREFIX "/gpio%u/edge", number);

	return stuff_file(gpio_edge_file, edge, -1);
}

static inline int get_gpio_value(int valfd, int *out) {
	char buf[2];

	if (
		lseek(valfd, 0, SEEK_SET) != 0 ||
		read(valfd, buf, sizeof(buf)) != sizeof(buf)
	)
		return -1;

	*out = (buf[0] == '1') ? 1 : 0;

	return 0;
}

inline void subtract_timespecs(
	const struct timespec *a,
	const struct timespec *b,
	struct timespec *res
) {
	res->tv_sec = a->tv_sec - b->tv_sec;
	res->tv_nsec = a->tv_nsec - b->tv_nsec;
	if (res->tv_nsec < 0) {
		res->tv_nsec += 1000000000;
		res->tv_sec -= 1;
	}
}

static void *read_loop(void *arg) {
	struct encoder_ctx *ctx = arg;
	struct pollfd pollfds[2];
	int a = ctx->a_value, b = ctx->b_value, old_a, old_b, diff, dummy;
	struct timespec start_sample, end_sample;

	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, &dummy);

	while (1) {
		pollfds[0].fd = ctx->a_fd;
		pollfds[0].events = POLLIN | POLLPRI;
		pollfds[1].fd = ctx->b_fd;
		pollfds[1].events = POLLIN | POLLPRI;

		if (poll(pollfds, 2, -1) < 0)
			goto error;

		clock_gettime(CLOCK_MONOTONIC, &start_sample);

		old_a = a;
		old_b = b;

		if (
			get_gpio_value(ctx->a_fd, &a) ||
			get_gpio_value(ctx->b_fd, &b)
		)
			goto error;

		if (a == old_a && b == old_b)
			continue;

		if (a != old_a && b != old_b) {
			errno = EIO;
			goto error;
		}

		if (old_a == 0 && a == 1)
			diff = old_b * 2 - 1;
		else if (old_a == 1 && a == 0)
			diff = old_b * -2 + 1;
		else if (old_b == 0 && b == 1)
			diff = old_a * -2 + 1;
		else // (old_b == 1 && b == 0)
			diff = old_a * 2 - 1;

		pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &dummy);
		if (pthread_mutex_lock(&ctx->lock))
			goto error;

		ctx->value += diff;

		clock_gettime(CLOCK_MONOTONIC, &end_sample);
		subtract_timespecs(&end_sample, &start_sample, &ctx->last_sampletime);

		pthread_mutex_unlock(&ctx->lock);
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, &dummy);

		continue;

	   error:

		if (!pthread_mutex_lock(&ctx->lock)) {
			++ctx->err_count;
			ctx->errnum = errno;
			pthread_mutex_unlock(&ctx->lock);
		}
		
	}

	return NULL; /* NOT REACHED */
}

int qenc_get_encoder_value(struct encoder_ctx *ctx, int *enc_val, struct timespec *last_sampling) {
	int ret = 0;

	if (pthread_mutex_lock(&ctx->lock))
		return -1;

	if (ctx->err_count) {
		ret = -ctx->err_count;
		ctx->err_count = 0;
		errno = ctx->errnum;
	} else {
		if (enc_val)
			*enc_val = ctx->value;
		if (last_sampling)
			*last_sampling = ctx->last_sampletime;
	}

	pthread_mutex_unlock(&ctx->lock);

	return ret;
}

struct encoder_ctx *qenc_launch_read_loop(unsigned gpio_a, unsigned gpio_b) {
	char gpio_a_filename[FILENAME_MAX+1];
	char gpio_b_filename[FILENAME_MAX+1];
	struct encoder_ctx *ctx;
	pthread_attr_t thread_attr;
	struct sched_param thread_priority = {
		.sched_priority = 99,
	};

	if (!(ctx = calloc(1, sizeof(*ctx))))
		return NULL;
	ctx->a_fd = -1;
	ctx->b_fd = -1;
	pthread_mutex_init(&ctx->lock, NULL);
	ctx->a_number = gpio_a;
	ctx->b_number = gpio_b;

	if (
		export_gpio(gpio_a) ||
		export_gpio(gpio_b) ||
		set_gpio_direction(gpio_a, GPIO_DIR_IN) ||
		set_gpio_direction(gpio_b, GPIO_DIR_IN) ||
		set_gpio_edge(gpio_a, GPIO_EDGE_TYPE_BOTH) ||
		set_gpio_edge(gpio_b, GPIO_EDGE_TYPE_BOTH)
	)
		goto fail;

	snprintf(gpio_a_filename, sizeof(gpio_a_filename), GPIO_PREFIX "/gpio%u/value", gpio_a);
	snprintf(gpio_b_filename, sizeof(gpio_b_filename), GPIO_PREFIX "/gpio%u/value", gpio_b);
	if (
		(ctx->a_fd = open(gpio_a_filename, O_RDONLY)) < 0 ||
		(ctx->b_fd = open(gpio_b_filename, O_RDONLY)) < 0
	)
		goto fail;

	if (
		get_gpio_value(ctx->a_fd, &ctx->a_value) ||
		get_gpio_value(ctx->b_fd, &ctx->b_value)
	)
		goto fail;

	if (
		pthread_attr_init(&thread_attr) ||
		pthread_attr_setschedpolicy(&thread_attr, SCHED_FIFO) ||
		pthread_attr_setschedparam(&thread_attr, &thread_priority) ||
		pthread_create(&ctx->thread, &thread_attr, read_loop, ctx)
	)
		goto fail;

	pthread_attr_destroy(&thread_attr);

	return ctx;

   fail:
	if (ctx->a_fd >= 0)
		close(ctx->a_fd);
	if (ctx->b_fd >= 0)
		close(ctx->b_fd);

	unexport_gpio(gpio_a);
	unexport_gpio(gpio_b);

	free(ctx);

	return NULL;
}

int qenc_terminate_read_loop(struct encoder_ctx *ctx) {
	int ret = 0;

	if (
		pthread_cancel(ctx->thread) ||
		pthread_join(ctx->thread, NULL) ||
		pthread_mutex_destroy(&ctx->lock)
	)
		return -1;

	if (
		close(ctx->a_fd) |
		close(ctx->a_fd) |
		unexport_gpio(ctx->a_number) |
		unexport_gpio(ctx->b_number)
	)
		ret = -1;

	free(ctx);

	return ret;
}
