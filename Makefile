# Makefile for abc (AI bash/zsh/tcsh Command)

# Variables
PYTHON := python3
INSTALL_DIR := $(HOME)/.local/bin
CONFIG_FILE := $(HOME)/.abc.conf
SHELL := /bin/bash
SHELL_SCRIPTS := abc.sh abc.tcsh

# Files
CONFIG_TEMPLATE := abc.conf.template

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help build install uninstall clean config

help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Install dependencies and package using pipx
	@echo "Installing abc using pipx..."
	$(PYTHON) -m pip install --user --quiet pipx
	$(PYTHON) -m pipx ensurepath
	$(PYTHON) -m pipx install --force .

install: build ## Install shell integration scripts
	@echo "Installing shell integration scripts..."
	mkdir -p $(INSTALL_DIR)
	cp $(SHELL_SCRIPTS) $(INSTALL_DIR)/
	@echo "abc has been installed"
	@echo ""
	@echo "Next steps:"
	@echo "1. Add one of these lines to your shell configuration file:"
	@echo "   For bash/zsh:"
	@echo "     source \"$(INSTALL_DIR)/abc.sh\""
	@echo "   For tcsh:"
	@echo "     source \"$(INSTALL_DIR)/abc.tcsh\""
	@echo "2. Create $(CONFIG_FILE) using $(CONFIG_TEMPLATE) as a template"
	@echo "3. Reload your shell configuration"

uninstall: ## Uninstall abc
	@echo "Uninstalling abc..."
	$(PYTHON) -m pipx uninstall abc-cli
	rm -f $(addprefix $(INSTALL_DIR)/,$(SHELL_SCRIPTS))
	@echo "Removed abc-cli package and shell integration scripts"
	@echo "Remember to remove the 'source' line from your shell configuration file"

clean: ## Remove generated files and caches
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf build/ dist/ *.egg-info/

config: ## Create a config file from the template
	@if [ ! -f $(CONFIG_FILE) ]; then \
		cp $(CONFIG_TEMPLATE) $(CONFIG_FILE); \
		echo "Config file created at $(CONFIG_FILE)"; \
		echo "Please edit it with your API key"; \
	else \
		echo "Config file already exists at $(CONFIG_FILE)"; \
	fi
