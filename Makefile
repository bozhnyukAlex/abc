# Makefile for abc (AI bash/zsh/tcsh Command)

# Variables
PYTHON := python3
CONFIG_FILE := $(HOME)/.abc.conf
SHELL := /bin/bash

# Files
CONFIG_TEMPLATE := abc.conf.template

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help install uninstall clean config tree

help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install-pipx:
	@$(PYTHON) -m pip install --user --quiet pipx
	@$(PYTHON) -m pipx ensurepath

install: install-pipx ## Install abc
	@echo "Installing abc using pipx..."
	@$(PYTHON) -m pipx install --force .
	@abc_setup

setup: ## Re-create the config file
	@abc_setup

uninstall: ## Uninstall abc
	@echo "Uninstalling abc..."
	@abc_setup --uninstall
	@$(PYTHON) -m pipx uninstall abc-cli

tree: ## Show a file tree
	@git ls-files | tree --fromfile -a --filesfirst
