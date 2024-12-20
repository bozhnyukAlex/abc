# abc-provider-anthropic

Anthropic LLM provider for [abc-cli](https://github.com/alestic/abc).

## Configuration

In your `~/.abc.conf`:

```ini
[default]
api_key = {ANTHROPIC_API_KEY}

# Optional settings:
model = claude-3-5-sonnet-20241022
temperature = 0.0
max_tokens = 1000
```

Get your Anthropic API key from the [Anthropic Console](https://console.anthropic.com/settings/keys).

## License

Apache 2.0 - See [LICENSE](../LICENSE)
