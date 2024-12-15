# Development Testing

## Ubuntu

Uninstall everything

```bash
# Remove shell integrations
abc_setup --uninstall --no-prompt

# Remove abc app
pipx uninstall abc-cli

# Remove pipx
sudo apt remove -y pipx

# Move aside config file
mv $HOME/.abc.conf $HOME/dot-abc.conf-$(date +%Y%m%d-%H%M%S)
```

Install with prompts

```bash
curl -fsSL https://getabc.sh/ | bash
```

Install without prompts

```bash
curl -fsSL https://getabc.sh/ | bash -s -- --no-prompt
```
