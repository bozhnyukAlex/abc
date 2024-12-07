# Installing abc (AI bash/zsh/tcsh Command)

This guide provides two methods for installing abc on your system: a modern Python package installation using pipx (recommended), and the traditional make-based installation.

## Prerequisites

- Python 3.8 or higher
- An API key for the Claude AI model from Anthropic
- bash 4.4 or higher, or zsh 5.0 or higher, or tcsh 6.0 or higher

## Modern Installation (Recommended)

The recommended way to install abc is using pipx, which automatically manages virtual environments for command-line tools:

1. Install pipx if you haven't already:

   ```bash
   python -m pip install --user pipx
   python -m pipx ensurepath
   ```

2. Install abc directly from GitHub:

   ```bash
   pipx install git+https://github.com/alestic/abc.git
   ```

3. Complete install setup

   ```bash
   abc_setup
   ```

   This will:
   - Install shell integration scripts to ~/.local/share/abc
   - Guide you through updating your shell configuration files
   - Create backups of any modified files
   - Provide instructions for API key configuration

   For non-interactive environments or to skip all prompts:

   ```bash
   abc_setup --yes
   ```

4. Follow the printed instructions to:

   - Reload your shell configuration
   - Set up your API key configuration

## Legacy Installation (Make-based)

The traditional make-based installation is still supported:

1. Clone the repository:

   ```
   git clone https://github.com/alestic/abc.git
   cd abc
   ```

2. Build dependencies and install in $HOME/.local/bin/

   ```
   make build install
   ```

3. Add the appropriate shell integration to your shell configuration file:

   For bash users, add to `~/.bashrc`:

   ```bash
   source "$HOME/.local/bin/abc.sh"
   ```

   For zsh users, add to `~/.zshrc`:

   ```zsh
   source "$HOME/.local/bin/abc.sh"
   ```

   For tcsh users, add to `~/.tcshrc`:

   ```tcsh
   source "$HOME/.local/bin/abc.tcsh"
   ```

   Then, reload your shell configuration:

   For bash:

   ```bash
   source ~/.bashrc
   ```

   For zsh:

   ```zsh
   source ~/.zshrc
   ```

   For tcsh:

   ```tcsh
   source ~/.tcshrc
   ```

## Configuration

1. Create an Anthropic API key:
   https://console.anthropic.com/settings/keys

2. Create a configuration file at `~/.abc.conf` with your API key:

   ```ini
   [default]
   api_key = your_api_key_here
   ```

## Verifying the Installation

To verify that abc is installed correctly, run:

```
abc --version
```

This should display the version of abc.

## Updating

### Modern Installation

To update abc to the latest version when installed via pipx:

```bash
pipx upgrade abc-cli
abc_setup  # --yes to skip prompts
```

### Legacy Installation

To update abc when installed via make:

```bash
git pull
make build install
source ~/.bashrc  # or ~/.zshrc for zsh, or ~/.tcshrc for tcsh
```

## Uninstalling

### Modern Installation

To uninstall abc when installed via pipx:

```bash
abc_setup --uninstall  # --yes to skip prompts
pipx uninstall abc-cli
```

The uninstall process will:

- Remove shell integration scripts
- Remove source lines from shell configuration files
- Create backups of any modified files
- Remove the ~/.local/share/abc directory

### Legacy Installation

To uninstall abc when installed via make:

```bash
make uninstall
```

Then remove the `source` line from your shell configuration file (`~/.bashrc`, `~/.zshrc`, or `~/.tcshrc`).
