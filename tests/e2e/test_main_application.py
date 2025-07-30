"""End-to-End tests for the main application.

This module tests the application's main entry point (main.py) as a black box,
simulating real user interactions and verifying the complete workflow.
"""

import pytest
import subprocess
import sys
import os
from pathlib import Path

# Mark all tests in this file as e2e tests
pytestmark = pytest.mark.e2e


def test_main_script_runs_and_fetches_messages():
    """
    Tests that the main.py script can be executed and successfully
    prints output indicating it has fetched messages.
    
    This test requires real credentials and a live internet connection.
    """
    # Get the path to main.py (should be in the workspace root)
    main_script = Path(__file__).parent.parent.parent / "main.py"
    
    if not main_script.exists():
        pytest.skip(f"main.py not found at {main_script}")
    
    # Check if credentials exist
    credentials_file = main_script.parent / "credentials.json"
    token_file = main_script.parent / "token.json"
    
    if not credentials_file.exists() and not token_file.exists():
        pytest.skip("No credentials.json or token.json found - cannot run E2E test")

    command = [
        sys.executable,  # Path to the current python interpreter
        str(main_script),
    ]

    try:
        # Run the command and capture the output
        # We need to be in the right directory for the script to find its dependencies
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,  # Fail the test if the script returns a non-zero exit code
            timeout=120,  # Longer timeout for real network calls
            cwd=str(main_script.parent),  # Run from the script's directory
        )
        
        # Assert that the script's output contains expected text
        output = result.stdout
        
        assert "Attempting to initialize Gmail client..." in output
        assert "Successfully authenticated and connected" in output
        
        # Check for test sections
        assert "=== TEST 1: Fetching Messages ===" in output
        assert "=== TEST 2: Getting Specific Message" in output
        assert "=== TEST 3: Marking Message as Read" in output
        assert "=== All Tests Completed ===" in output
        
        # Should have found at least some messages
        if "Found" in output and "messages:" in output:
            # Extract number of messages found
            lines = output.split('\n')
            found_line = next((line for line in lines if "Found" in line and "messages:" in line), None)
            if found_line:
                print(f"E2E test verified: {found_line}")

    except subprocess.TimeoutExpired:
        pytest.fail("E2E test timed out - main.py took too long to execute")
    except subprocess.CalledProcessError as e:
        # If the script fails, print its output for easier debugging
        pytest.fail(
            f"E2E test failed when running main.py.\n"
            f"Exit Code: {e.returncode}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )
    except FileNotFoundError:
        pytest.fail("Python interpreter or main.py not found")


def test_main_script_handles_no_credentials_gracefully():
    """
    Tests that main.py handles missing credentials gracefully.
    """
    main_script = Path(__file__).parent.parent.parent / "main.py"
    
    if not main_script.exists():
        pytest.skip(f"main.py not found at {main_script}")

    # Temporarily rename credentials files if they exist
    credentials_file = main_script.parent / "credentials.json"
    token_file = main_script.parent / "token.json"
    
    backup_files = []
    
    try:
        # Backup existing credential files
        if credentials_file.exists():
            backup_cred = credentials_file.with_suffix(".json.backup")
            credentials_file.rename(backup_cred)
            backup_files.append((credentials_file, backup_cred))
            
        if token_file.exists():
            backup_token = token_file.with_suffix(".json.backup")
            token_file.rename(backup_token)
            backup_files.append((token_file, backup_token))

        command = [sys.executable, str(main_script)]

        # Run without credentials - should handle gracefully
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(main_script.parent),
        )
        
        # Script should fail gracefully, not crash
        # Check that it at least tried to initialize
        output = result.stdout + result.stderr
        assert "Attempting to initialize Gmail client..." in output
        
        # Should mention credential issues
        credentials_mentioned = any(word in output.lower() for word in 
                                  ['credentials', 'token', 'auth', 'login'])
        assert credentials_mentioned, "Error output should mention credential issues"

    finally:
        # Restore backup files
        for original, backup in backup_files:
            if backup.exists():
                backup.rename(original)


def test_main_script_syntax_is_valid():
    """
    Tests that main.py has valid Python syntax.
    """
    main_script = Path(__file__).parent.parent.parent / "main.py"
    
    if not main_script.exists():
        pytest.skip(f"main.py not found at {main_script}")

    # Check syntax without executing
    command = [sys.executable, "-m", "py_compile", str(main_script)]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        
        # If we get here, syntax is valid
        print("main.py syntax is valid")

    except subprocess.CalledProcessError as e:
        pytest.fail(f"main.py has syntax errors:\n{e.stderr}")


def test_main_script_imports_work():
    """
    Tests that main.py can import all required modules.
    """
    main_script = Path(__file__).parent.parent.parent / "main.py"
    
    if not main_script.exists():
        pytest.skip(f"main.py not found at {main_script}")

    # Test imports without running main logic
    import_test_code = '''
try:
    import mail_client_api
    import message
    import gmail_client_impl
    import gmail_message_impl
    print("All imports successful")
except ImportError as e:
    print(f"Import error: {e}")
    raise
'''

    command = [sys.executable, "-c", import_test_code]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
            cwd=str(main_script.parent),  # Run from the script's directory
        )
        
        assert "All imports successful" in result.stdout

    except subprocess.CalledProcessError as e:
        pytest.fail(f"main.py imports failed:\n{e.stderr}")


def test_application_structure_integrity():
    """
    Tests that the application has the expected file structure.
    """
    workspace_root = Path(__file__).parent.parent.parent
    
    expected_files = [
        "main.py",
        "pyproject.toml",
        "src/mail_client_api/src/mail_client_api/__init__.py",
        "src/gmail_client_impl/src/gmail_client_impl/__init__.py",
        "src/gmail_client_impl/src/gmail_client_impl/_impl.py",
        "src/gmail_message_impl/src/gmail_message_impl/__init__.py",
        "src/gmail_message_impl/src/gmail_message_impl/_impl.py",
        "src/message/src/message/__init__.py",
    ]
    
    missing_files = []
    
    for file_path in expected_files:
        full_path = workspace_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        pytest.fail(f"Missing required files: {missing_files}")
    
    print("Application structure integrity verified")
