# Installing abc (AI bash/zsh/tcsh Command)

This guide provides instructions for installing abc on your system using pipx.

## Prerequisites

- Linux or macOS
- Python 3.8 or higher
- bash 4.4+, zsh 5.0+, or tcsh 6.0+
- An API key for the Claude AI model from Anthropic

## Installation

1. Install pipx, if you haven't already:

   ```bash
   # macOS
   brew install pipx
   pipx ensurepath

   # Ubuntu 23.04 or above
   sudo apt install pipx
   pipx ensurepath

   # Fedora
   sudo dnf install pipx
   pipx ensurepath

   # Arch
   sudo pacman -S python-pipx
   pipx ensurepath

   # Alternative: using pip
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   ```

2. Install abc using pipx:

   From GitHub:

   ```bash
   pipx install git+https://github.com/alestic/abc.git
   abc_setup
   ```

   Alternative:

   ```bash
   git clone https://github.com/alestic/abc.git
   cd abc
   pipx install .
   abc_setup
   ```

   This will:
   - Install shell integration scripts
   - Update your shell rc files
   - Guide you through API key setup
   - Create backups of any modified files

3. Start a new terminal or reload your shell rc file:

   ```bash
   # For bash
   source ~/.bashrc

   # For zsh
   source ~/.zshrc

   # For tcsh
   source ~/.tcshrc
   ```

## Verifying the Installation

To verify that abc is installed correctly:

```bash
abc --version
abc hi
```

## Updating

To update abc to the latest version:

```bash
pipx upgrade abc-cli
abc_setup
```

## Uninstalling

To remove abc from your system:

```bash
abc_setup --uninstall
pipx uninstall abc-cli
```

## Files and Locations

- Shell integration: `~/.local/share/abc/`
- Configuration: `~/.abc.conf`
- Shell configuration:
  - bash: `~/.bashrc`
  - zsh: `~/.zshrc`
  - tcsh: `~/.tcshrc`

## Troubleshooting

1. If you see "command not found: pipx" during installation:
   - Run: `pipx ensurepath`
   - Start a new terminal

2. If abc commands don't work after installation:
   - Ensure your shell rc file was sourced
   - Check that `~/.abc.conf` exists and contains your API key
   - Verify the shell integration with `type abc`

3. For other issues:
   - Check the error message
   - Verify Python version: `python3 --version`
   - Ensure shell version meets requirements
