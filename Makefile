.PHONY: all clear-filesystem-cache-files help pack_plugin

all: help

help:
	@echo "Available targets:"
	@echo "  make clear-filesystem-cache-files"
	@echo "  make pack_plugin"

clear-filesystem-cache-files:
	./scripts/clear_filesystem_cache.sh

pack_plugin:
	$(MAKE) clear-filesystem-cache-files
	./scripts/pack_plugin.sh
