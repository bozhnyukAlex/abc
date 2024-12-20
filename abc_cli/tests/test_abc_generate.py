import pytest
from abc_cli.abc_generate import process_generated_command

def test_process_generated_command_with_cdata():
    """Test that CDATA tags are properly stripped from commands."""
    input_command = """<![CDATA[
echo $PATH | tr ':' '\n' | sort | uniq -c
##DANGERLEVEL=0## Reads and displays environment variable, no changes made.
]]>"""
    expected_output = """echo $PATH | tr ':' '\n' | sort | uniq -c"""

    result = process_generated_command(input_command)
    assert result == expected_output

def test_process_generated_command_without_cdata():
    """Test that commands without CDATA tags are processed normally."""
    input_command = """echo $PATH | tr ':' '\n' | sort | uniq -c
##DANGERLEVEL=0## Reads and displays environment variable, no changes made."""
    expected_output = """echo $PATH | tr ':' '\n' | sort | uniq -c"""

    result = process_generated_command(input_command)
    assert result == expected_output

def test_process_generated_command_dangerous():
    """Test that dangerous commands are properly marked."""
    input_command = """rm -rf /
##DANGERLEVEL=2## This command is extremely dangerous and could delete all files."""
    expected_output = """#DANGEROUS# rm -rf /"""

    result = process_generated_command(input_command)
    assert result == expected_output

def test_process_generated_command_dangerous_with_cdata():
    """Test that dangerous commands with CDATA tags are properly handled."""
    input_command = """<![CDATA[
rm -rf /
##DANGERLEVEL=2## This command is extremely dangerous and could delete all files.
]]>"""
    expected_output = """#DANGEROUS# rm -rf /"""

    result = process_generated_command(input_command)
    assert result == expected_output
