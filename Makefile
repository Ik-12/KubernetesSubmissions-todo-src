SUBDIRS := $(dir $(wildcard */Makefile))

all: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: all $(SUBDIRS)
