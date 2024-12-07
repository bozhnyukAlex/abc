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
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s [abc] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

def create_share_dir():
    """Create ~/.local/share/abc directory if it doesn't exist."""
    share_dir = Path.home() / '.local' / 'share' / 'abc'
    share_dir.mkdir(parents=True, exist_ok=True)
    return share_dir

def uninstall():
    """Remove shell integration scripts and package files."""
    try:
        # Remove ~/.local/share/abc directory
        share_dir = Path.home() / '.local' / 'share' / 'abc'
        if share_dir.exists():
            shutil.rmtree(share_dir)
            logging.info(f"Removed directory: {share_dir}")

        return 0

    except Exception as e:
        logging.error(f"Uninstall failed: {e}")
        return 1

def setup_shell_scripts():
    """Setup shell integration scripts and configuration template."""
    try:
        # Get the directory where our package resources are installed
        with importlib.resources.path('abc_cli', 'abc.sh') as shell_script:
            package_dir = shell_script.parent

        # Create ~/.local/share/abc
        share_dir = create_share_dir()

        # Copy shell scripts and make them executable
        scripts = ['abc.sh', 'abc.tcsh']
        for script in scripts:
            source = package_dir / script
            target = share_dir / script

            # Copy file and preserve permissions
            shutil.copy2(source, target)
            target.chmod(0o755)  # Make executable
            logging.info(f"Installed: {target}")

        # Copy configuration template
        template_source = package_dir / 'abc.conf.template'
        template_target = share_dir / 'abc.conf.template'
        shutil.copy2(template_source, template_target)
        logging.info(f"Installed: {template_target}")

        # Print success message with next steps
        print("\nShell integration scripts have been installed successfully!")
        print("\nNext steps:")
        print("1. Add one of these lines to your shell configuration file:")
        print("\n   For bash/zsh:")
        print(f"     source \"{share_dir}/abc.sh\"")
        print("\n   For tcsh:")
        print(f"     source \"{share_dir}/abc.tcsh\"")
        print("\n2. Reload your shell configuration:")
        print("   For bash:  source ~/.bashrc")
        print("   For zsh:   source ~/.zshrc")
        print("   For tcsh:  source ~/.tcshrc")
        print("\n3. Create your configuration file:")
        print(f"   cp -i {share_dir}/abc.conf.template ~/.abc.conf")
        print("   Then edit ~/.abc.conf and add your API key")

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
        args = parser.parse_args()

        if args.uninstall:
            return uninstall()
        else:
            return setup_shell_scripts()

    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        return 1

if __name__ == '__main__':
    sys.exit(main())
