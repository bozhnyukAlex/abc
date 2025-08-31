# Nix Installation Support for abc (Experimental)

This document describes the experimental Nix/NixOS support for the `abc` (AI Bash Command) tool. This is a first draft implementation in response to [issue #24](https://github.com/alestic/abc/issues/24) and we welcome feedback from the Nix community.

## Installation

### Quick Start

```bash
# Install abc with all providers
nix profile install github:alestic/abc

# Source shell integration (needed each session)
source ~/.nix-profile/share/abc/abc.sh

# Create configuration file
mkdir -p ~/.config/abc
cat > ~/.config/abc/config << EOF
[default]
provider = anthropic
api_key = YOUR_ANTHROPIC_API_KEY_HERE
model = claude-sonnet-4-0
EOF
chmod 600 ~/.config/abc/config

# Test it
abc "list files in current directory"
```

### Home-Manager Support

Home-Manager support is not yet available for abc. If you're interested in declarative configuration through Home-Manager, please [request this feature](https://github.com/alestic/abc/issues).

## Configuration

Unlike the traditional `abc` installation method, the Nix version does not include an interactive setup wizard. You must create your configuration file manually at `~/.config/abc/config`:

```ini
[default]
provider = anthropic
api_key = sk-ant-api03-...
model = claude-sonnet-4-0

[aws-bedrock]
region = us-east-1
model = anthropic.claude-sonnet-4-20250514-v1:0
```

## Shell Integration

The Nix installation provides shell integration scripts but does not modify your shell RC files. You have three options:

1. **Manual sourcing** (each session):
   ```bash
   source ~/.nix-profile/share/abc/abc.sh
   ```

2. **Add to your shell RC file**:
   ```bash
   echo 'source ~/.nix-profile/share/abc/abc.sh' >> ~/.bashrc
   ```

3. **Use Home-Manager** (not yet available - see above)

## Differences from Traditional Installation

| Feature | Traditional (pipx) | Nix |
|---------|-------------------|-----|
| Installation | `pipx install abc-cli` | `nix profile install github:alestic/abc` |
| Providers | Installed separately | All bundled |
| Setup wizard | Interactive (`abc_setup`) | Manual config |
| Shell integration | Modifies RC files | Source manually |
| Uninstall | `abc_setup --uninstall` | `nix profile remove abc` |

## Available Packages

- `default` - abc with all providers (recommended)
- `abc-cli` - Core package only
- `abc-provider-anthropic` - Anthropic provider
- `abc-provider-aws-bedrock` - AWS Bedrock provider

## Development Shell

For contributors:

```bash
git clone https://github.com/alestic/abc
cd abc
nix develop

# Shell with all development dependencies
# Source the integration:
source $ABC_SHELL_INTEGRATION/abc.sh
```

## Known Limitations

1. No interactive setup wizard - configuration must be created manually
2. Shell integration requires manual sourcing
3. All providers are bundled - cannot selectively install providers
4. First run does not provide configuration guidance

## Feedback Welcome

This is an experimental first implementation of Nix support for `abc`. We welcome feedback from the Nix community:

- Report issues or suggestions on [issue #24](https://github.com/alestic/abc/issues/24)
- The implementation may change based on community feedback
- Pull requests are welcome to improve the Nix integration

## Technical Details

The Nix implementation:
- Uses a flake-based approach for modern Nix compatibility
- Wraps Python executables to ensure provider discovery works
- Home-Manager module support is planned for future releases
- Maintains compatibility with all existing `abc` functionality

For more details, see the `flake.nix` file in the repository.

---
*[Created by AI: Claude Code]*
