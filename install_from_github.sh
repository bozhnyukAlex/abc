#!/bin/bash
# abc/install_from_github.sh - Install pipx and use to install abc from GitHub

set -e  # Exit on error
set -u  # Exit on undefined variable

# Default values
NO_PROMPT=false
NO_PROMPT_OPTION=
FORCE=false
FORCE_OPTION=

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-prompt)
            NO_PROMPT=true
            NO_PROMPT_OPTION="--no-prompt"
            shift
            ;;
        --force)
            FORCE=true
            FORCE_OPTION="--force"
            shift
            ;;
        *)
            error "Unknown argument: $1"
            ;;
    esac
done

# Logging setup
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [abc] [INFO] $1"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [abc] [ERROR] $1" >&2
    exit 1
}

is_interactive() {
    # Check if stderr is connected to a terminal
    # This works even when stdin is a pipe
    [[ -t 2 ]]
}

prompt_user() {
    local message=$1
    local default=${2:-"y"}  # Default to yes

    # Skip prompt if --no-prompt flag is set or not interactive
    if $NO_PROMPT || ! is_interactive; then
        if [ "$default" = "y" ]; then
            echo "yes"
        else
            echo "no"
        fi
        return
    fi

    # Prompt user on stderr to avoid pipe interference
    local prompt
    if [ "$default" = "y" ]; then
        prompt=" [Y/n] "
    else
        prompt=" [y/N] "
    fi

    echo -n "$message$prompt" >&2
    read -r response </dev/tty  # Read directly from terminal

    # Add newline since we used echo -n above
    echo >&2

    response=${response,,}  # Convert to lowercase

    if [[ -z "$response" ]]; then
        response=$default
    fi

    if [[ "$response" =~ ^(yes|y)$ ]]; then
        echo "yes"
    else
        echo "no"
    fi
}

install_pipx() {
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log "Detected macOS - Installing pipx via Homebrew..."
        if command -v brew &> /dev/null; then
            if [[ "$(prompt_user "About to install pipx via Homebrew. Continue?" "y")" = "yes" ]]; then
                brew install pipx || error "Failed to install pipx via Homebrew"
            else
                log "Installation cancelled by user"
                exit 0
            fi
        else
            error "Homebrew not found. Please install Homebrew first."
        fi

    elif command -v apt &> /dev/null; then
        log "Detected Debian/Ubuntu - Installing pipx via apt..."
        if [[ "$(prompt_user "About to install pipx via apt. This requires sudo access. Continue?" "y")" = "yes" ]]; then
            sudo apt update || error "Failed to update apt"
            sudo apt install -y pipx || error "Failed to install pipx via apt"
        else
            log "Installation cancelled by user"
            exit 0
        fi

    elif command -v dnf &> /dev/null; then
        log "Detected RedHat/Fedora - Installing pipx via dnf..."
        if [[ "$(prompt_user "About to install pipx via dnf. This requires sudo access. Continue?" "y")" = "yes" ]]; then
            sudo dnf install -y pipx || error "Failed to install pipx via dnf"
        else
            log "Installation cancelled by user"
            exit 0
        fi

    elif command -v pacman &> /dev/null; then
        log "Detected Arch Linux - Installing pipx via pacman..."
        if [[ "$(prompt_user "About to install pipx via pacman. This requires sudo access. Continue?" "y")" = "yes" ]]; then
            sudo pacman -S --noconfirm python-pipx || error "Failed to install pipx via pacman"
        else
            log "Installation cancelled by user"
            exit 0
        fi

    elif command -v yum &> /dev/null; then
        log "Detected older RedHat/CentOS - Installing pipx via yum..."
        if [[ "$(prompt_user "About to install pipx via yum. This requires sudo access. Continue?" "y")" = "yes" ]]; then
            sudo yum install -y python3-pip || error "Failed to install python3-pip via yum"
            python3 -m pip install --user pipx || error "Failed to install pipx via pip"
        else
            log "Installation cancelled by user"
            exit 0
        fi

    else
        log "Unable to detect package manager. Installing pipx via pip..."
        if [[ "$(prompt_user "About to install pipx via pip. Continue?" "y")" = "yes" ]]; then
            python3 -m pip install --user pipx || error "Failed to install pipx via pip"
        else
            log "Installation cancelled by user"
            exit 0
        fi
    fi
}

main() {
    log "Starting abc installation from GitHub..."

    # Check if pipx is already installed
    if command -v pipx &> /dev/null; then
        log "pipx is already installed"
    else
        log "pipx not found. Installation required."
        install_pipx
    fi

    # Ensure pipx is in PATH
    log "Ensuring pipx apps are in PATH..."
    pipx ensurepath || error "Failed to ensure pipx apps are in PATH"

    # Check if abc is already installed
    if pipx list | grep -q "abc-cli"; then
        log "abc is already installed, attempting upgrade..."
        if [[ "$(prompt_user "About to upgrade abc via pipx. Continue?" "y")" = "yes" ]]; then
            pipx upgrade abc-cli || error "Failed to upgrade abc"
            log "Upgrading Anthropic provider..."
            pipx inject abc-cli abc-provider-anthropic@git+https://github.com/alestic/abc.git#subdirectory=abc_provider_anthropic $FORCE_OPTION || error "Failed to upgrade Anthropic provider"
            log "Upgrading AWS Bedrock provider..."
            pipx inject abc-cli abc-provider-aws-bedrock@git+https://github.com/alestic/abc.git#subdirectory=abc_provider_aws_bedrock $FORCE_OPTION || error "Failed to upgrade AWS Bedrock provider"
        else
            log "Upgrade cancelled by user"
            exit 0
        fi
    else
        log "Installing abc from GitHub..."
        if [[ "$(prompt_user "About to install abc via pipx. Continue?" "y")" = "yes" ]]; then
            pipx install git+https://github.com/alestic/abc.git $FORCE_OPTION || error "Failed to install abc via pipx"
            log "Installing Anthropic provider..."
            pipx inject abc-cli abc-provider-anthropic@git+https://github.com/alestic/abc.git#subdirectory=abc_provider_anthropic $FORCE_OPTION || error "Failed to install Anthropic provider"
            log "Installing AWS Bedrock provider..."
            pipx inject abc-cli abc-provider-aws-bedrock@git+https://github.com/alestic/abc.git#subdirectory=abc_provider_aws_bedrock $FORCE_OPTION || error "Failed to install AWS Bedrock provider"
        else
            log "Installation cancelled by user"
            exit 0
        fi
    fi

    # Run abc setup in a login shell to get updated PATH
    log "Running abc setup..."
    bash -l -c "abc_setup $NO_PROMPT_OPTION" || error "Failed to run abc setup"

    log "Installation completed successfully!"
}

# Handle interrupts gracefully
trap 'echo -e "\nInstallation cancelled by user"; exit 1' INT

main "$@"
