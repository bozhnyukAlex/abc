#!/usr/bin/env python3
"""
abc_setup - Setup script for abc shell integration

This script manages shell integration scripts and configuration for abc.

Command line options:
  --uninstall   Remove shell integration scripts and optionally configuration
  --no-prompt   Skip all prompts and use default values (useful for automation)

Examples:
  # Normal installation with prompts
  abc_setup

  # Non-interactive installation with defaults
  abc_setup --no-prompt

  # Remove shell integration
  abc_setup --uninstall

  # Non-interactive uninstall (leaves configuration file in place)
  abc_setup --uninstall --no-prompt
"""

import argparse
import importlib.resources
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
import getpass

# Constants
SHELL_RC_FILES = {
    'bash': '.bashrc',
    'zsh': '.zshrc',
    'tcsh': '.tcshrc'
}

MARKER_BEGIN = "# >>> abc initialize >>>"
MARKER_MIDDLE = "# !! Contents within this block are managed by 'abc_setup' !!"
MARKER_END = "# <<< abc initialize <<<"

# Setup logging
logging.basicConfig(
    format='%(asctime)s [abc] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

def get_terminal_input(prompt='', default=None, sensitive=False):
    """Get user input from terminal, handling both interactive and non-interactive cases."""
    if not sys.stderr.isatty():
        return default

    print(prompt, end='', file=sys.stderr, flush=True)
    try:
        if sensitive:
            response = getpass.getpass(prompt='')
        else:
            with open('/dev/tty', 'r') as tty:
                response = tty.readline().strip()
    except (OSError, IOError):
        print(file=sys.stderr)
        return default

    print(file=sys.stderr)
    return response if response else default

def prompt_user(message, default=True, no_prompt=False):
    """Prompt user for yes/no confirmation."""
    if no_prompt:
        return default

    prompt = f"{message} [{'Y/n' if default else 'y/N'}] "
    response = get_terminal_input(prompt, 'y' if default else 'n')
    return response.lower() in ['y', 'yes']

def backup_file(file_path, timestamp):
    """Create a backup of a file with timestamp."""
    backup_path = file_path.with_suffix(f'.bak_{timestamp}')
    shutil.copy2(file_path, backup_path)
    logging.info(f"Created backup: {backup_path}")

def modify_rc_file(file_path, source_line, remove=False):
    """Add or remove source block from rc file. Returns True if file was modified."""
    file_path = Path.home() / file_path

    # Check if file exists
    if not file_path.exists():
        logging.info(f"Skipping {file_path}: file not found")
        return False

    # Read existing content
    with open(file_path, 'r') as f:
        content = f.readlines()

    # Process content
    if remove:
        # Remove existing block
        new_content = []
        in_block = False
        found_block = False
        for line in content:
            if MARKER_BEGIN in line:
                in_block = True
                found_block = True
            elif MARKER_END in line:
                in_block = False
            elif not in_block:
                new_content.append(line)
        if not found_block:
            return False
        content = new_content
    else:
        # Check if block already exists
        if any(MARKER_BEGIN in line for line in content):
            logging.info(f"Skipping {file_path}: abc block already exists")
            return False

        # Add new block
        if content and content[-1].strip():
            content.append('\n')  # Add newline if file doesn't end with one
        content.extend([
            f"{MARKER_BEGIN}\n",
            f"{MARKER_MIDDLE}\n",
            f"{source_line}\n",
            f"{MARKER_END}\n"
        ])

    # Write back
    with open(file_path, 'w') as f:
        f.writelines(content)

    if remove:
        logging.info(f"Removed abc block from {file_path}")
    else:
        logging.info(f"Added abc block to {file_path}")

    return True

def setup_config(no_prompt=False):
    """Set up abc configuration file with API key."""
    config_file = Path.home() / '.abc.conf'

    # Check if we should configure
    if config_file.exists() and not prompt_user("\nConfiguration file already exists. Would you like to reconfigure it?", default=False, no_prompt=no_prompt):
        return True

    try:
        # Backup existing config if it exists
        if config_file.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file(config_file, timestamp)

        # Get the template content
        with importlib.resources.path('abc_cli', 'abc.conf.template') as template_path:
            with open(template_path, 'r') as f:
                template_content = f.read()

        # Prompt for API key if interactive
        print("\nPlease enter your Anthropic API key", file=sys.stderr)
        print("(You can get this from https://console.anthropic.com/settings/keys)", file=sys.stderr)
        api_key = get_terminal_input("API key: ", '{ANTHROPIC_API_KEY}', sensitive=True)

        # Write configuration
        config_content = template_content.replace('{ANTHROPIC_API_KEY}', api_key)
        with open(config_file, 'w') as f:
            f.write(config_content)

        logging.info(f"Created configuration file: {config_file}")
        return True

    except (OSError, IOError) as e:
        logging.error(f"Configuration setup failed: {e}")
        return False

def setup_shell_scripts(no_prompt=False):
    """Setup shell integration scripts and configuration template."""
    if not prompt_user("\nAbout to add abc files to $HOME/.local/share/ Continue?", no_prompt=no_prompt):
        print("Setup cancelled")
        return 0

    try:
        # Get package resources
        with importlib.resources.path('abc_cli', 'abc.sh') as shell_script:
            package_dir = shell_script.parent

        # Create ~/.local/share/abc
        share_dir = Path.home() / '.local' / 'share' / 'abc'
        share_dir.mkdir(parents=True, exist_ok=True)

        # Copy and update shell scripts
        venv_python = sys.executable  # Get virtualenv Python path
        scripts = ['abc.sh', 'abc.tcsh']
        for script in scripts:
            source = package_dir / script
            target = share_dir / script

            # Update Python path and copy
            with open(source, 'r') as f:
                content = f.read().replace('\\python3', f'\\{venv_python}')
            with open(target, 'w') as f:
                f.write(content)
            target.chmod(0o755)
            logging.info(f"Installed: {target}")

        # Copy configuration template
        template_source = package_dir / 'abc.conf.template'
        template_target = share_dir / 'abc.conf.template'
        shutil.copy2(template_source, template_target)
        logging.info(f"Installed: {template_target}")

        if not prompt_user("\nAbout to add abc commands to shell rc files. Continue?", no_prompt=no_prompt):
            print("Setup cancelled")
            return 0

        # Update shell rc files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        modified = False
        found_shells = []

        for shell, rc_file in SHELL_RC_FILES.items():
            source_line = f'source "{share_dir}/abc.{shell if shell == "tcsh" else "sh"}"'
            rc_path = Path.home() / rc_file
            if not rc_path.exists():
                continue
            found_shells.append(shell)
            if modify_rc_file(rc_file, source_line):
                modified = True
                backup_file(rc_path, timestamp)

        if modified:
            print("\nShell configuration files have been updated.")

        if found_shells:
            print("\nTo activate the changes, either:")
            print("1. Start a new terminal, or")
            print("2. Run one of these commands in your current terminal:")
            for shell in found_shells:
                rc_file = SHELL_RC_FILES[shell]
                print(f"   For {shell}:  source ~/{rc_file}")

        # Set up configuration
        if not setup_config(no_prompt):
            print("\nWarning: Configuration setup failed. You will need to manually configure ~/.abc.conf")
            print(f"You can use {share_dir}/abc.conf.template as a template")

        return 0

    except (OSError, IOError) as e:
        logging.error(f"Setup failed: {e}")
        return 1

def uninstall(no_prompt=False):
    """Remove shell integration scripts and package files."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        modified = False
        found_shells = []

        if prompt_user("\nWould you like to remove abc shell integration files from ~/.local/share/abc?", default=True, no_prompt=no_prompt):
            # Remove ~/.local/share/abc directory
            share_dir = Path.home() / '.local' / 'share' / 'abc'
            if share_dir.exists():
                shutil.rmtree(share_dir)
                logging.info(f"Removed directory: {share_dir}")

        if prompt_user("\nWould you like to remove abc commands from your shell rc files?", default=True, no_prompt=no_prompt):
            # Remove source blocks from rc files
            for shell, rc_file in SHELL_RC_FILES.items():
                rc_path = Path.home() / rc_file
                if not rc_path.exists():
                    continue
                found_shells.append(shell)
                if modify_rc_file(rc_file, '', remove=True):
                    modified = True
                    backup_file(rc_path, timestamp)

        # Optionally remove configuration
        config_file = Path.home() / '.abc.conf'
        if config_file.exists() and prompt_user("\nWould you like to remove the configuration file (~/.abc.conf)?", default=False, no_prompt=no_prompt):
            backup_file(config_file, timestamp)
            config_file.unlink()
            logging.info("Removed configuration file")

        print("\nUninstallation complete. You may now run:")
        print("pipx uninstall abc-cli")

        return 0

    except (OSError, IOError) as e:
        logging.error(f"Uninstall failed: {e}")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Setup abc shell integration")
    parser.add_argument('--uninstall', action='store_true',
                      help="Remove shell integration scripts")
    parser.add_argument('--no-prompt', action='store_true',
                      help="Skip all prompts and use default values")
    args = parser.parse_args()

    try:
        if args.uninstall:
            return uninstall(args.no_prompt)
        else:
            return setup_shell_scripts(args.no_prompt)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1

if __name__ == '__main__':
    sys.exit(main())
