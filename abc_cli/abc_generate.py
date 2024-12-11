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
from typing import List, Dict, Tuple
import re

import anthropic
import distro

VERSION: str = "# 2024.12.09"
PROGRAM_NAME: str = "abc"

# Config file
DEFAULT_CONFIG_FILE: str = '~/.abc.conf'
DEFAULT_CONFIG_SECTION: str = 'default'

# Log format
LOG_FORMAT: str = f'%(asctime)s [{PROGRAM_NAME}] [%(levelname)s] %(message)s'
LOG_FORMAT_DATE: str = '%Y-%m-%d %H:%M:%S'

# LLM Constants
LLM_MODEL: str = "claude-3-5-sonnet-20241022"
LLM_TEMPERATURE: float = 0.0
LLM_MAX_TOKENS: int = 1000

# Constants for danger level parsing
DANGER_LEVEL_PATTERN = r'##DANGERLEVEL=(\d)## (.+)$'
HIGH_DANGER_THRESHOLD = 2
DANGEROUS_PREFIX = '#DANGEROUS# '

def get_os_info():
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

def read_config_file(config_file_path: str) -> dict:
    """Read and parse the configuration file, using only the first section."""
    config = configparser.ConfigParser()
    with open(config_file_path, 'r') as config_file:
        config.read_file(config_file)
    if len(config.sections()) == 0:
        raise configparser.Error(f"Error: No sections found in config file '{config_file_path}'")
    first_section = config.sections()[0]
    return dict(config[first_section])

def get_config(config_file_path: str) -> Dict[str, str]:
    """Read and parse the configuration file, using only the first section."""
    config = configparser.ConfigParser()
    with open(config_file_path, 'r') as config_file:
        config.read_file(config_file)
    if len(config.sections()) == 0:
        raise configparser.Error(f"Error: No sections found in config file '{config_file_path}'")
    first_section = config.sections()[0]
    return dict(config[first_section])

def get_system_prompt(os_info: str, shell: str):
    return f"""<purpose>
    You are an expert in {shell} shell commands for {os_info}.
    Given a natural language description, generate the appropriate {shell} command(s) to accomplish the task.
</purpose>

<instructions>
    <instruction>Generate only the exact {shell} shell command without explanations or preamble.</instruction>
    <instruction>Important: All commands must be on a single-line.</instruction>
    <instruction>Use techniques like semicolons, &&, ||, and pipes to separate multiple commands on the single line.</instruction>
    <instruction>Ensure the output command can be directly copied and pasted into a terminal.</instruction>
    <instruction>Use {shell}-specific syntax.</instruction>
    <instruction>Use commands specific to {os_info} when appropriate.</instruction>
    <instruction>Aim for elegance and simplicity.</instruction>
    <instruction>Consider and handle edge cases (e.g., dot files, whitespace, missing/existing files).</instruction>
    <instruction>Consider and handle unusual environment conditions (e.g., user-defined aliases, environment variables)</instruction>
    <instruction>After generating the command line, evaluate its danger/risk level and add it on the second line in this format: ##DANGERLEVEL=[[CODE]]## [[justification]]</instruction>
</instructions>

<danger-levels>
    <level code="0">Read only, informational command.</level>
    <level code="1">Modifies the system in common ways or generates standard side effects.</level>
    <level code="2">Potential loss of significant data or large/harmful side effects. Should be reviewed carefully.</level>
</danger-levels>

<examples>
    <example>
        <input>
            Description: find the longest python filename
        </input>
        <output>
<![CDATA[
find . -name "*.py" -type f -printf "%f\n" | awk '{{print length, $0}}' | sort -rn | head -1 | cut -d' ' -f2-
##DANGERLEVEL=0## Reading file info, no changes made.
]]>
        </output>
    </example>
    <example>
        <input>
            Description: copy subdir1 contents to subdir2
        </input>
        <output>
<![CDATA[
cp --archive --interactive subdir1/ subdir2/
##DANGERLEVEL=1## Can overwrite existing files in subdir2 with files from subdir1, potentially causing data loss in the destination directory
]]>
        </output>
    </example>
    <example>
        <input>
            Description: delete all system log files
        </input>
        <output>
<![CDATA[
sudo rm -rf /var/log/*
##DANGERLEVEL=2## Highly destructive command that removes critical system logs. Will impact system monitoring, troubleshooting, and security auditing. Could prevent diagnosis of system issues and hide security breaches.
]]>
        </output>
    </example>
</examples>
"""

def generate_command(description: str, api_key: str, os_info: str, shell: str) -> str:
    """Generate a command using the LLM based on the given description and shell."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        system=get_system_prompt(os_info, shell),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Description: {description}\n\n{shell.capitalize()} command(s):"
                    }
                ]
            }
        ]
    )

    logging.debug(f"Response message: {message}")

    return message.content[0].text.strip()

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

        raw_command = generate_command(description, config['api_key'], get_os_info(), args.shell)
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
