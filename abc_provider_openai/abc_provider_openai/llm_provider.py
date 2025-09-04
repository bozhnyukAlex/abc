"""OpenAI LLM provider implementation.

[Created by AI: Claude Code]
"""

import openai
from typing import Dict, Any

from abc_cli import LLMProvider

DEFAULT_MODEL = 'gpt-5'
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TIMEOUT = 30

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, config: Dict[str, str]):
        """Initialize provider with configuration.

        Args:
            config: Provider configuration from abc.conf
        """
        if config.get('provider') != 'openai':
            raise ValueError("Provider must be 'openai'")

        self.api_key = config['api_key']
        self.model = config.get('model', DEFAULT_MODEL)
        self.temperature = float(config.get('temperature', DEFAULT_TEMPERATURE))
        self.max_tokens = int(config.get('max_tokens', DEFAULT_MAX_TOKENS))
        self.timeout = float(config.get('timeout', DEFAULT_TIMEOUT))
        
        # Optional organization and API base for Azure OpenAI
        self.organization = config.get('organization')
        self.api_base = config.get('api_base')
        self.api_version = config.get('api_version')
        
        # Initialize OpenAI client
        client_kwargs = {
            'api_key': self.api_key,
            'timeout': self.timeout
        }
        
        if self.organization:
            client_kwargs['organization'] = self.organization
            
        if self.api_base:
            client_kwargs['base_url'] = self.api_base
            
        self.client = openai.OpenAI(**client_kwargs)

    def generate_command(
        self,
        description: str,
        context: Dict[str, Any],
        system_prompt: str,
    ) -> str:
        """Generate command using OpenAI GPT models."""
        try:
            # Build request parameters
            request_params = {
                "model": self.model,
                "max_completion_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Description: {description}\n\n{context.get('shell', 'bash').capitalize()} command(s):"
                    }
                ]
            }
            
            # Only add temperature if it's not the default 0.0 (some models don't support 0.0)
            if self.temperature != 0.0:
                request_params["temperature"] = self.temperature
                
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content.strip()
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def get_config_schema(self) -> Dict:
        """Get JSON schema for configuration."""
        return {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "description": "Provider identifier (must be 'openai')",
                    "enum": ["openai"]
                },
                "api_key": {
                    "type": "string",
                    "description": "OpenAI API key"
                },
                "model": {
                    "type": "string",
                    "description": "OpenAI model to use",
                    "default": DEFAULT_MODEL,
                    "examples": ["gpt-5", "gpt-4o", "gpt-4-turbo"]
                },
                "temperature": {
                    "type": "string",
                    "description": "Sampling temperature (0.0-2.0)",
                    "default": str(DEFAULT_TEMPERATURE)
                },
                "max_tokens": {
                    "type": "string",
                    "description": "Maximum completion tokens in response (uses max_completion_tokens parameter)",
                    "default": str(DEFAULT_MAX_TOKENS)
                },
                "timeout": {
                    "type": "string",
                    "description": "Request timeout in seconds",
                    "default": str(DEFAULT_TIMEOUT)
                },
                "organization": {
                    "type": "string",
                    "description": "OpenAI organization ID (optional)"
                },
                "api_base": {
                    "type": "string", 
                    "description": "Custom API endpoint (for Azure OpenAI)"
                },
                "api_version": {
                    "type": "string",
                    "description": "API version (for Azure OpenAI)"
                }
            },
            "required": ["provider", "api_key"]
        }