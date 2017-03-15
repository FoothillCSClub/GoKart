
LIBDIR ?= $(CURDIR)
BINDIR ?= $(CURDIR)
INCDIR ?=

DEBUG ?=
LDFLAGS ?=
override LDFLAGS += -L $(LIBDIR) -lpthread
CFLAGS ?=
override CFLAGS += $(DEBUG) -Wall

ifdef INCDIR
override CFLAGS += -I $(INCDIR)
endif

ARCH = $(shell uname -m)

ifeq ($(ARCH),x86_64)
   override CFLAGS += -fPIC
endif

SRCS = encoder.c
HDRS = quadrature_encoder.h

.PHONY: all tests

all: $(LIBDIR)/libquadratureencoder.so $(foreach header,$(HDRS),$(INCDIR)/$(header))

tests: $(BINDIR)/encoder_test

$(LIBDIR)/libquadratureencoder.so: $(SRCS) $(HDRS)
	$(CC) $(CFLAGS) -shared -o $@ $(SRCS) $(LDFLAGS)

ifdef INCDIR
$(foreach header,$(HDRS),$(INCDIR)/$(header)): $(HDRS)
	cp $^ $@
endif

$(BINDIR)/encoder_test: encoder_test.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) -lquadratureencoder
