#!/usr/bin/env python3
"""
abc_setup - Setup script for abc shell integration

This script manages shell integration scripts and configuration for abc.
"""

import argparse
import importlib.resources
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s [abc] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# Marker lines for shell configuration
MARKER_BEGIN = "# >>> abc initialize >>>"
MARKER_MIDDLE = "# !! Contents within this block are managed by 'abc_setup' !!"
MARKER_END = "# <<< abc initialize <<<"

# Global timestamp for backups
BACKUP_TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

def is_interactive():
    """Check if we're running interactively."""
    return sys.stdin.isatty()

def prompt_user(message, default=True):
    """Prompt user for yes/no confirmation."""
    if not is_interactive():
        return default

    while True:
        response = input(f"{message} [Y/n] ").lower().strip()
        if response in ['', 'y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

def backup_file(file_path):
    """Create a backup of a file with the global timestamp."""
    if not file_path.exists():
        return None

    backup_path = file_path.with_suffix(f'.bak_{BACKUP_TIMESTAMP}')
    shutil.copy2(file_path, backup_path)
    return backup_path

def create_share_dir():
    """Create ~/.local/share/abc directory if it doesn't exist."""
    share_dir = Path.home() / '.local' / 'share' / 'abc'
    share_dir.mkdir(parents=True, exist_ok=True)
    return share_dir

def get_shell_rc_files():
    """Get paths to shell rc files."""
    home = Path.home()
    return {
        'bash': home / '.bashrc',
        'zsh': home / '.zshrc',
        'tcsh': home / '.tcshrc'
    }

def check_source_block(file_path):
    """Check if source block exists in file."""
    if not file_path.exists():
        return False

    with open(file_path, 'r') as f:
        content = f.read()
        return MARKER_BEGIN in content

def add_source_line(file_path, source_line, yes=False):
    """Add source line to shell rc file."""
    if check_source_block(file_path):
        logging.info(f"Source block already exists in {file_path}")
        return True

    message = f"\nWould you like to add abc shell integration to {file_path}?\n"
    message += f"  {source_line}\n"
    message += "This is needed for shell integration."

    if not yes and not prompt_user(message):
        logging.info(f"Skipped modifying {file_path}")
        return False

    # Backup file before modifying
    backup = backup_file(file_path)
    if backup:
        logging.info(f"Created backup: {backup}")

    # Create file if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Add source block
    mode = 'a' if file_path.exists() else 'w'
    with open(file_path, mode) as f:
        if mode == 'a':
            f.write('\n')  # Add newline before our content
        f.write(f"{MARKER_BEGIN}\n")
        f.write(f"{MARKER_MIDDLE}\n")
        f.write(f"{source_line}\n")
        f.write(f"{MARKER_END}\n")

    logging.info(f"Updated {file_path}")
    return True

def remove_source_block(file_path):
    """Remove source block from shell rc file."""
    if not file_path.exists():
        return True

    if not check_source_block(file_path):
        return True

    # Backup file before modifying
    backup = backup_file(file_path)
    if backup:
        logging.info(f"Created backup: {backup}")

    # Read file content
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find and remove the block
    in_block = False
    new_lines = []
    for line in lines:
        if MARKER_BEGIN in line:
            in_block = True
            continue
        elif MARKER_END in line:
            in_block = False
            continue
        elif not in_block:
            new_lines.append(line)

    # Write back the file without the block
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    logging.info(f"Removed source block from {file_path}")
    return True

def get_venv_python():
    """Get the Python interpreter path from the current virtual environment."""
    # When running via pipx, we're already in the right virtualenv
    return sys.executable

def update_shell_script(source_path, target_path, venv_python):
    """Update shell script to use the virtualenv Python."""
    with open(source_path, 'r') as f:
        content = f.read()

    # Replace python3 with the full path to the virtualenv Python
    updated_content = content.replace('\\python3', f'\\{venv_python}')

    with open(target_path, 'w') as f:
        f.write(updated_content)
    target_path.chmod(0o755)  # Make executable

def uninstall(yes=False):
    """Remove shell integration scripts and package files."""
    try:
        message = "\nThis will remove abc shell integration files and configuration. Continue?"
        if not yes and not prompt_user(message):
            print("Uninstall cancelled")
            return 0

        # Remove source blocks from rc files
        rc_files = get_shell_rc_files()
        for rc_file in rc_files.values():
            remove_source_block(rc_file)

        # Remove ~/.local/share/abc directory
        share_dir = Path.home() / '.local' / 'share' / 'abc'
        if share_dir.exists():
            shutil.rmtree(share_dir)
            logging.info(f"Removed directory: {share_dir}")

        print("\nUninstallation complete. You may now run:")
        print("pipx uninstall abc-cli")

        return 0

    except Exception as e:
        logging.error(f"Uninstall failed: {e}")
        return 1

def setup_shell_scripts(yes=False):
    """Setup shell integration scripts and configuration template."""
    try:
        message = "\nThis will set up abc shell integration. Continue?"
        if not yes and not prompt_user(message):
            print("Setup cancelled")
            return 0

        # Get the directory where our package resources are installed
        with importlib.resources.path('abc_cli', 'abc.sh') as shell_script:
            package_dir = shell_script.parent

        # Create ~/.local/share/abc
        share_dir = create_share_dir()

        # Get virtualenv Python path
        venv_python = get_venv_python()
        logging.info(f"Using Python interpreter: {venv_python}")

        # Copy and update shell scripts
        scripts = ['abc.sh', 'abc.tcsh']
        for script in scripts:
            source = package_dir / script
            target = share_dir / script
            update_shell_script(source, target, venv_python)
            logging.info(f"Installed: {target}")

        # Copy configuration template
        template_source = package_dir / 'abc.conf.template'
        template_target = share_dir / 'abc.conf.template'
        shutil.copy2(template_source, template_target)
        logging.info(f"Installed: {template_target}")

        # Update shell rc files
        rc_files = get_shell_rc_files()
        source_lines = {
            'bash': f'source "{share_dir}/abc.sh"',
            'zsh': f'source "{share_dir}/abc.sh"',
            'tcsh': f'source "{share_dir}/abc.tcsh"'
        }

        modified = False
        for shell, rc_file in rc_files.items():
            if add_source_line(rc_file, source_lines[shell], yes):
                modified = True

        if modified:
            print("\nShell configuration files have been updated.")
            print("To activate the changes, either:")
            print("1. Start a new terminal, or")
            print("2. Run one of these commands in your current terminal:")
            print("   For bash:  source ~/.bashrc")
            print("   For zsh:   source ~/.zshrc")
            print("   For tcsh:  source ~/.tcshrc")

        # Configuration setup instructions
        if not Path.home() / '.abc.conf':
            print("\nTo complete setup, create your configuration file:")
            print(f"1. cp {share_dir}/abc.conf.template ~/.abc.conf")
            print("2. Edit ~/.abc.conf and add your API key")

        return 0

    except Exception as e:
        logging.error(f"Setup failed: {e}")
        return 1

def main():
    """Main entry point."""
    try:
        parser = argparse.ArgumentParser(description="Setup abc shell integration")
        parser.add_argument('--uninstall', action='store_true',
                          help="Remove shell integration scripts")
        parser.add_argument('--yes', '-y', action='store_true',
                          help="Answer yes to all prompts")
        args = parser.parse_args()

        # Default to --yes in non-interactive mode
        yes = args.yes or not is_interactive()

        if args.uninstall:
            return uninstall(yes)
        else:
            return setup_shell_scripts(yes)

    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        return 1

if __name__ == '__main__':
    sys.exit(main())
