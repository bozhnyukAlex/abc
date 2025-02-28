# ABC CLI Codebase Guide

## Project Architecture
- PRIMARY USER INTERFACE: Shell function/alias (`abc`) installed in user's shell
- Core workflow:
  1. User types `abc description of command` in their shell
  2. Shell function calls Python backend to generate command via LLM
  3. Shell function presents generated command on the NEXT shell prompt
  4. User can edit command before execution
  5. Command is added to shell history when executed
- Providers: Plugin architecture allows different LLM backends (Anthropic, AWS, etc.)
- Configuration: ~/.abc.conf or XDG_CONFIG_HOME/abc/config

## Build & Test Commands
- Install: `make install`
- Uninstall: `make uninstall` 
- Setup config: `make setup`
- Run tests: `python -m pytest`
- Run specific test: `python -m pytest abc_cli/tests/test_abc_generate.py::test_function_name`
- Test with coverage: `python -m pytest --cov=abc_cli`
- Install plugin for development: `pipx inject abc-cli -e ./abc_provider_name`

## Code Style Guidelines
- Shell integration: Must seamlessly integrate with bash, zsh, and tcsh
- Python ≥ 3.8 compatibility
- Type hints required for Python code
- Shell scripts: Quote variables, use safe defaults
- Error handling: Use specific exceptions
- Provider implementation: Follow LLMProvider interface
- Installation: Shell integration must be idempotent
- Testing must cover Python backend AND shell integration