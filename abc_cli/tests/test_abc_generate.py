import pytest
from pathlib import Path

from abc_cli.abc_generate import load_rules_content, process_generated_command, resolve_rules_path
from abc_cli.prompts import get_system_prompt

@pytest.mark.unit
def test_process_generated_command_with_cdata():
    """Test that CDATA tags are properly stripped from commands."""
    input_command = """<![CDATA[
echo $PATH | tr ':' '\n' | sort | uniq -c
##DANGERLEVEL=0## Reads and displays environment variable, no changes made.
]]>"""
    expected_output = """echo $PATH | tr ':' '\n' | sort | uniq -c"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_without_cdata():
    """Test that commands without CDATA tags are processed normally."""
    input_command = """echo $PATH | tr ':' '\n' | sort | uniq -c
##DANGERLEVEL=0## Reads and displays environment variable, no changes made."""
    expected_output = """echo $PATH | tr ':' '\n' | sort | uniq -c"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_dangerous():
    """Test that dangerous commands are properly marked."""
    input_command = """rm -rf /
##DANGERLEVEL=2## This command is extremely dangerous and could delete all files."""
    expected_output = """#DANGEROUS# rm -rf /"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_dangerous_with_cdata():
    """Test that dangerous commands with CDATA tags are properly handled."""
    input_command = """<![CDATA[
rm -rf /
##DANGERLEVEL=2## This command is extremely dangerous and could delete all files.
]]>"""
    expected_output = """#DANGEROUS# rm -rf /"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_with_bash_code_block():
    """Test that bash code blocks are properly stripped from commands."""
    input_command = """```bash
ls -la
##DANGERLEVEL=0## Lists files in current directory, no changes made.
```"""
    expected_output = """ls -la"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_with_sh_code_block():
    """Test that sh code blocks are properly stripped from commands."""
    input_command = """```sh
echo "Hello World"
##DANGERLEVEL=0## Displays text, no changes made.
```"""
    expected_output = """echo "Hello World\""""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_with_generic_code_block():
    """Test that generic code blocks are properly stripped from commands."""
    input_command = """```
pwd
##DANGERLEVEL=0## Displays current directory, no changes made.
```"""
    expected_output = """pwd"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_with_dangerous_code_block():
    """Test that dangerous commands in code blocks are properly marked."""
    input_command = """```bash
sudo rm -rf /tmp/*
##DANGERLEVEL=2## This command could delete important files.
```"""
    expected_output = """#DANGEROUS# sudo rm -rf /tmp/*"""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_process_generated_command_with_code_block_and_cdata():
    """Test that both code blocks and CDATA are handled together."""
    input_command = """```bash
<![CDATA[
echo "test"
##DANGERLEVEL=0## Simple echo command.
]]>
```"""
    expected_output = """echo "test\""""

    result = process_generated_command(input_command)
    assert result == expected_output

@pytest.mark.unit
def test_get_system_prompt_includes_extra_rules():
    """Test that additional rules are appended to the system prompt."""
    prompt = get_system_prompt({"shell": "bash", "os_info": "POSIX"}, extra_rules="# Extra rule")

    assert "<additional-rules>" in prompt
    assert "# Extra rule" in prompt

@pytest.mark.unit
def test_get_system_prompt_without_extra_rules():
    """Test that prompt does not include additional rules block by default."""
    prompt = get_system_prompt({"shell": "bash", "os_info": "POSIX"})

    assert "<additional-rules>" not in prompt

@pytest.mark.unit
def test_resolve_rules_path_prefers_cli_path(tmp_path, monkeypatch):
    """Test that CLI rules override config rules and resolve from cwd."""
    config_file = tmp_path / "config.ini"
    config_file.write_text("[default]\nprovider = mock_provider\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_rules_path("rules.md", "config-rules.md", str(config_file))

    assert resolved == tmp_path / "rules.md"

@pytest.mark.unit
def test_resolve_rules_path_uses_config_directory(tmp_path):
    """Test that config rule paths are resolved relative to config location."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "abc.conf"
    config_file.write_text("[default]\nprovider = mock_provider\n", encoding="utf-8")

    resolved = resolve_rules_path(None, "rules.md", str(config_file))

    assert resolved == config_dir / "rules.md"

@pytest.mark.unit
def test_load_rules_content_reads_markdown(tmp_path):
    """Test reading additional rules from a markdown file."""
    rules_file = tmp_path / "rules.md"
    rules_file.write_text("# Rules\n\nBe strict.\n", encoding="utf-8")

    result = load_rules_content(rules_file)

    assert result == "# Rules\n\nBe strict."

@pytest.mark.unit
def test_load_rules_content_missing_file():
    """Test missing rules file raises a readable error."""
    with pytest.raises(ValueError, match="Could not read rules file"):
        load_rules_content(Path("/definitely/missing/rules.md"))
