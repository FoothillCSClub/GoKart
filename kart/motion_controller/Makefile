
DEBUG ?=
LDFLAGS ?=
override LDFLAGS += -lm
CFLAGS ?=
override CFLAGS += $(DEBUG)

LIBDIR ?= $(CURDIR)
INCDIR ?=

ARCH = $(shell uname -m)

ifeq ($(ARCH),x86_64)
   override CFLAGS += -fPIC
endif

SRCS = pca9685.c
HDRS = pca9685.h

.PHONY: all

all: $(LIBDIR)/libpca9685.so $(foreach header,$(HDRS),$(INCDIR)/$(header))

$(LIBDIR)/libpca9685.so: $(SRCS) $(HDRS)
	$(CC) $(CFLAGS) -shared -o $@ $(SRCS) $(LDFLAGS)

ifdef INCDIR
$(foreach header,$(HDRS),$(INCDIR)/$(header)): $(HDRS)
	cp $^ $@
endif
