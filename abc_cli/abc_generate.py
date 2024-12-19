#!/usr/bin/env python3
"""
abc_generate - AI Bash Command Generator

Website, source code, and documentation:

  https://getabc.sh
  https://github.com/alestic/abc

Credits:

  Written by Claude 3.5 Sonnet
  Prompt crafting by Eric Hammond
"""

import argparse
import configparser
import logging
import os
import sys
from typing import Dict
import re
import distro

from .providers import LLMProvider
from .providers.anthropic import AnthropicProvider
from .providers.prompts import get_system_prompt

VERSION: str = "# 2024.12.15"
PROGRAM_NAME: str = "abc"

# Config file
DEFAULT_CONFIG_FILE: str = '~/.abc.conf'
DEFAULT_CONFIG_SECTION: str = 'default'

# Log format
LOG_FORMAT: str = f'%(asctime)s [{PROGRAM_NAME}] [%(levelname)s] %(message)s'
LOG_FORMAT_DATE: str = '%Y-%m-%d %H:%M:%S'

# Constants for danger level parsing
DANGER_LEVEL_PATTERN = r'##DANGERLEVEL=(\d)## (.+)$'
HIGH_DANGER_THRESHOLD = 2
DANGEROUS_PREFIX = '#DANGEROUS# '

def get_os_info() -> str:
    """Get formatted OS information."""
    system = distro.name(pretty=True)
    version = distro.version(pretty=True)
    return f"{system} {version}".strip() or "POSIX"

def setup_logging(log_level: int) -> None:
    """Set up logging configuration."""
    logging.basicConfig(level=log_level, format=LOG_FORMAT, datefmt=LOG_FORMAT_DATE)

def create_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser for command-line arguments."""
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description="abc - AI Bash Command Generator")
    parser.add_argument('-c', '--config', type=argparse.FileType('r'),
                        default=os.environ.get('ABC_CONFIG', os.path.expanduser(DEFAULT_CONFIG_FILE)),
                        help='Path to configuration file')
    parser.add_argument('--version', action='version', version=VERSION,
                        help='Display the program version and exit')
    parser.add_argument('--shell', choices=['bash', 'zsh', 'tcsh'], default='bash',
                        help='Specify the shell to generate commands for (default: bash)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--verbose', action='store_const',
                       const=logging.INFO, dest='log_level',
                       help='Provide detailed information about the program execution')
    group.add_argument('--debug', action='store_const',
                       const=logging.DEBUG, dest='log_level',
                       help='Provide debug information, use this only when troubleshooting')
    parser.set_defaults(log_level=logging.WARNING)

    parser.add_argument('description', nargs=argparse.REMAINDER,
                        help='English description of the desired shell command')
    return parser

def get_config(config_file_path: str) -> Dict[str, str]:
    """Read and parse the configuration file, using only the first section."""
    config = configparser.ConfigParser()
    with open(config_file_path, 'r') as config_file:
        config.read_file(config_file)
    if len(config.sections()) == 0:
        raise configparser.Error(f"Error: No sections found in config file '{config_file_path}'")
    first_section = config.sections()[0]
    return dict(config[first_section])

def get_provider(config: Dict[str, str]) -> LLMProvider:
    """Get the configured LLM provider.

    Currently defaults to Anthropic provider for backward compatibility.
    Will be enhanced to support provider selection in the future.
    """
    return AnthropicProvider(config)

def process_generated_command(command: str) -> str:
    """Process the generated command based on its danger level."""
    lines = command.splitlines()
    if not lines:
        return command  # Empty command, return as is

    # Check if the last line contains danger level information
    danger_match = re.match(DANGER_LEVEL_PATTERN, lines[-1])
    if not danger_match:
        return command  # No danger level provided or invalid format, return as is

    command_lines = lines[:-1]  # All lines except the last one
    danger_level = int(danger_match.group(1))
    justification = danger_match.group(2)

    if danger_level >= HIGH_DANGER_THRESHOLD:
        print(f"Warning: This command is potentially dangerous. {justification}", file=sys.stderr)
        command_lines[0] = f"{DANGEROUS_PREFIX}{command_lines[0]}"

    return '\n'.join(command_lines)

def main() -> int:
    try:
        parser = create_argument_parser()
        args = parser.parse_args()

        setup_logging(args.log_level)

        config_file_path = args.config.name if args.config else os.environ.get('ABC_CONFIG', os.path.expanduser(DEFAULT_CONFIG_FILE))
        config = get_config(config_file_path)

        if 'api_key' not in config:
            raise ValueError("API key not found in configuration")

        description = " ".join(args.description)
        if not description:
            raise ValueError("No description provided")

        logging.info(f"Generating {args.shell} command for: {description}")

        # Get provider and context
        provider = get_provider(config)
        context = {
            'shell': args.shell,
            'os_info': get_os_info()
        }

        # Generate command
        raw_command = provider.generate_command(
            description=description,
            context=context,
            system_prompt=get_system_prompt(context)
        )

        processed_command = process_generated_command(raw_command)
        print(processed_command)

        return 0

    except (ValueError, configparser.Error) as e:
        logging.error(f"{e}")
        return 1
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
