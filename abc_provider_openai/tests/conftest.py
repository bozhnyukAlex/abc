"""Test configuration and fixtures for abc-provider-openai.

[Created by AI: Claude Code]
"""

import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_openai():
    """Fixture providing a mocked OpenAI client."""
    with patch('openai.OpenAI') as mock:
        # Setup default mock response
        mock_choice = Mock()
        mock_choice.message.content = "echo test\n##DANGERLEVEL=0## Safe command"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def mock_config():
    """Fixture providing a basic valid configuration."""
    return {
        "provider": "openai",
        "api_key": "test_api_key",
    }

@pytest.fixture
def mock_config_full():
    """Fixture providing a full configuration with all options."""
    return {
        "provider": "openai",
        "api_key": "test_api_key",
        "model": "gpt-5-test",
        "temperature": "0.5",
        "max_tokens": "500",
        "timeout": "60",
        "organization": "test_org",
    }

@pytest.fixture
def mock_context():
    """Fixture providing a basic context dictionary."""
    return {
        "shell": "bash",
        "os_info": "Ubuntu 22.04",
    }