
DEBUG ?=
LDFLAGS ?=
override LDFLAGS += -lpthread
CFLAGS ?=
override CFLAGS += $(DEBUG)

LIBDIR ?= $(CURDIR)
INCDIR ?=

ARCH = $(shell uname -m)

ifeq ($(ARCH),x86_64)
   override CFLAGS += -fPIC
endif

SRCS = encoder.c
HDRS = quadrature_encoder.h

.PHONY: all

all: $(LIBDIR)/libquadratureencoder.so $(foreach header,$(HDRS),$(INCDIR)/$(header))

$(LIBDIR)/libquadratureencoder.so: $(SRCS) $(HDRS)
	$(CC) $(CFLAGS) -shared -o $@ $(SRCS) $(LDFLAGS)

ifdef INCDIR
$(foreach header,$(HDRS),$(INCDIR)/$(header)): $(HDRS)
	cp $^ $@
endif
