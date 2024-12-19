"""Provider interface for abc LLM integrations."""

# NOTE! The `abc`/`ABC` module is part of the Python standard library and should not be confused with the `abc` command and `abc-cli` package.

from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate_command(
        self,
        description: str,
        context: Dict[str, Any],
        system_prompt: str,
    ) -> str:
        """Generate a shell command using the LLM provider.

        Args:
            description: Natural language description of desired command
            context: Dictionary containing generation context
            system_prompt: The system prompt to use

        Returns:
            Generated command string with danger level annotation in format:
            command
            ##DANGERLEVEL=N## justification
        """
        pass

    @abstractmethod
    def get_config_schema(self) -> Dict:
        """Return JSON schema for provider configuration.

        Returns:
            Dict containing JSON schema for provider config section
        """
        pass
