#!/usr/bin/env python3
"""
abc_setup - Setup script for abc shell integration

This script manages shell integration scripts and configuration for abc.
"""

import argparse
import importlib.resources
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

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

def is_interactive():
    """Check if we're running interactively."""
    return sys.stdin.isatty()

def prompt_user(message):
    """Prompt user for yes/no confirmation."""
    if not is_interactive():
        return True

    response = input(f"{message} [Y/n] ").lower().strip()
    return response in ['', 'y', 'yes']

def backup_files(files, timestamp):
    """Create backups of multiple files with the same timestamp."""
    backups = []
    for file_path in files:
        if not file_path.exists():
            continue
        backup_path = file_path.with_suffix(f'.bak_{timestamp}')
        shutil.copy2(file_path, backup_path)
        backups.append(backup_path)
        logging.info(f"Created backup: {backup_path}")
    return backups

def modify_rc_file(file_path, source_line, remove=False):
    """Add or remove source block from rc file."""
    file_path = Path.home() / file_path

    # Read existing content
    content = []
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.readlines()

    # Process content
    if remove:
        # Remove existing block
        new_content = []
        in_block = False
        for line in content:
            if MARKER_BEGIN in line:
                in_block = True
            elif MARKER_END in line:
                in_block = False
            elif not in_block:
                new_content.append(line)
        content = new_content
    else:
        # Check if block already exists
        if any(MARKER_BEGIN in line for line in content):
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
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.writelines(content)

    return True

def setup_config(yes=False):
    """Set up abc configuration file with API key."""
    config_file = Path.home() / '.abc.conf'

    if config_file.exists():
        if not yes and not prompt_user("\nConfiguration file already exists. Would you like to reconfigure it?"):
            return True
        # Backup existing config
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_files([config_file], timestamp)

    if not yes and not prompt_user("\nWould you like to set up the abc configuration file?"):
        print("Configuration setup skipped")
        return True

    try:
        # Get the template content
        with importlib.resources.path('abc_cli', 'abc.conf.template') as template_path:
            with open(template_path, 'r') as f:
                template_content = f.read()

        # Prompt for API key if interactive
        if is_interactive():
            print("\nPlease enter your Anthropic API key")
            print("(You can get this from https://console.anthropic.com/settings/keys)")
            api_key = input("API key: ").strip()

            # Update template with provided key
            config_content = template_content.replace('{ANTHROPIC_API_KEY}', api_key)
        else:
            # In non-interactive mode, just copy template
            config_content = template_content

        # Write configuration
        with open(config_file, 'w') as f:
            f.write(config_content)

        logging.info(f"Created configuration file: {config_file}")
        return True

    except (OSError, IOError) as e:
        logging.error(f"Configuration setup failed: {e}")
        return False

def setup_shell_scripts(yes=False):
    """Setup shell integration scripts and configuration template."""
    if not yes and not prompt_user("\nThis will set up abc shell integration. Continue?"):
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

        # Update shell rc files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        modified = False

        for shell, rc_file in SHELL_RC_FILES.items():
            source_line = f'source "{share_dir}/abc.{shell if shell == "tcsh" else "sh"}"'
            if modify_rc_file(rc_file, source_line):
                modified = True
                backup_files([Path.home() / rc_file], timestamp)

        if modified:
            print("\nShell configuration files have been updated.")
            print("To activate the changes, either:")
            print("1. Start a new terminal, or")
            print("2. Run one of these commands in your current terminal:")
            print("   For bash:  source ~/.bashrc")
            print("   For zsh:   source ~/.zshrc")
            print("   For tcsh:  source ~/.tcshrc")

        # Set up configuration
        if not setup_config(yes):
            print("\nWarning: Configuration setup failed. You will need to manually configure ~/.abc.conf")
            print(f"You can use {share_dir}/abc.conf.template as a template")

        return 0

    except (OSError, IOError) as e:
        logging.error(f"Setup failed: {e}")
        return 1

def uninstall(yes=False):
    """Remove shell integration scripts and package files."""
    if not yes and not prompt_user("\nThis will remove abc shell integration files and configuration. Continue?"):
        print("Uninstall cancelled")
        return 0

    try:
        # Backup and remove rc file modifications
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rc_files = [Path.home() / rc_file for rc_file in SHELL_RC_FILES.values()]
        backup_files(rc_files, timestamp)

        for rc_file in SHELL_RC_FILES.values():
            modify_rc_file(rc_file, '', remove=True)

        # Remove ~/.local/share/abc directory
        share_dir = Path.home() / '.local' / 'share' / 'abc'
        if share_dir.exists():
            shutil.rmtree(share_dir)
            logging.info(f"Removed directory: {share_dir}")

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
    parser.add_argument('--yes', '-y', action='store_true',
                      help="Answer yes to all prompts")
    args = parser.parse_args()

    try:
        if args.uninstall:
            return uninstall(args.yes or not is_interactive())
        else:
            return setup_shell_scripts(args.yes or not is_interactive())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1

if __name__ == '__main__':
    sys.exit(main())
