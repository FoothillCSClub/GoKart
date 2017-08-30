
SRCS = ads1115.c
HDRS = ads1115.h

LIBDIR ?= .
BINDIR ?= .
DEBUG ?=

.PHONY: all

all: $(LIBDIR)/libads1115.so

$(LIBDIR)/libads1115.so: $(SRCS) $(HDRS)
	$(CC) $(DEBUG) -shared -o $@ $(SRCS)

$(BINDIR)/ads1115_test: test.c
	$(CC) $(DEBUG) -o $@ $^ -L $(LIBDIR) -lads1115
