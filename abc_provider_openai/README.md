# OpenAI Provider for abc

[Created by AI: Claude Code]

This package provides OpenAI/ChatGPT integration for the abc (AI Bash Command) tool.

## Installation

This provider is typically installed as part of the main abc tool:

```bash
# Development install
make install-dev

# Or install directly
pipx inject abc-cli abc-provider-openai
```

## Configuration

Add an OpenAI configuration section to your `~/.abc.conf` file:

```ini
[default]
provider = openai
api_key = {OPENAI_API_KEY}
model = gpt-4-turbo-preview

[gpt-3.5]
provider = openai
api_key = {OPENAI_API_KEY}
model = gpt-3.5-turbo
```

### Supported Models

- `gpt-4-turbo-preview` (default)
- `gpt-4`
- `gpt-3.5-turbo`
- Other OpenAI chat completion models

### Configuration Options

- `provider`: Must be "openai"
- `api_key`: Your OpenAI API key (required)
- `model`: Model to use (optional, defaults to gpt-4-turbo-preview)
- `temperature`: Sampling temperature 0.0-2.0 (optional, default: 0.0, omitted for newer models that don't support 0.0)
- `max_tokens`: Maximum response tokens (optional, default: 1000)
- `timeout`: Request timeout in seconds (optional, default: 30)
- `organization`: OpenAI organization ID (optional)
- `api_base`: Custom API endpoint for Azure OpenAI (optional)
- `api_version`: API version for Azure OpenAI (optional)

### Azure OpenAI Support

For Azure OpenAI deployments:

```ini
[azure]
provider = openai
api_key = YOUR_AZURE_KEY
api_base = https://your-resource.openai.azure.com/
api_version = 2023-12-01-preview
model = your-deployment-name
```

## Usage

Once configured, use abc with your OpenAI configuration:

```bash
# Use default config
abc "list files by size"

# Use specific config section
abc --use gpt-3.5 "find large files"
```

## API Key Setup

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys) and either:

1. Set it in your config file: `api_key = sk-your-key-here`
2. Set environment variable: `export OPENAI_API_KEY=sk-your-key-here`

## Testing

Run the provider tests:

```bash
python -m pytest abc_provider_openai/tests/
```

## Requirements

- Python 3.8+
- OpenAI Python SDK 1.0+
- Valid OpenAI API key