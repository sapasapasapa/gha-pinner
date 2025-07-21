import os
import tempfile
from unittest.mock import patch

from src.editor import _pin_actions_in_workflow_content, pin_action_in_file, _is_sha_reference, _is_private_action


def test_is_sha_reference():
    """Test the _is_sha_reference function"""
    # Valid SHA (40 hex characters)
    assert _is_sha_reference("1234567890abcdef1234567890abcdef12345678") == True
    # Invalid SHA (too short)
    assert _is_sha_reference("1234567890abcdef") == False
    # Invalid SHA (non-hex characters)
    assert _is_sha_reference("1234567890abcdef1234567890abcdefzzzzzzzz") == False
    # Invalid SHA (too long)
    assert _is_sha_reference("1234567890abcdef1234567890abcdef123456789") == False


def test_is_private_action():
    """Test the _is_private_action function"""
    # Local action
    assert _is_private_action("./my-local-action") == True
    # Docker action
    assert _is_private_action("docker://alpine:3.14") == True
    # Action with variable
    assert _is_private_action("actions/checkout@{{ env.CHECKOUT_VERSION }}") == True
    # Standard GitHub action
    assert _is_private_action("actions/checkout@v3") == False


def test_pin_actions_in_workflow_content():
    """Test pinning actions in workflow content"""
    mock_workflow_content = """
name: Test GitHub Action

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Run a simple command
        run: echo "This is a basic GitHub Action"
    """

    # Mock the get_action_sha function to return a fixed SHA
    with patch("src.editor.get_action_sha", return_value="abc123def456"):
        # Mock the print_pinned_action function to avoid console output
        with patch("src.editor.print_pinned_action"):
            result = _pin_actions_in_workflow_content(mock_workflow_content)

    # Check that the actions were properly pinned with comments
    assert "uses: actions/checkout@abc123def456 # v3" in result
    assert "uses: actions/setup-node@abc123def456 # v3" in result


def test_pin_actions_already_pinned():
    """Test that already pinned actions are not modified"""
    mock_workflow_content = """
name: Test GitHub Action with Pinned Actions

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@1234567890abcdef1234567890abcdef12345678 # v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
    """

    # Mock the get_action_sha function to return a fixed SHA
    with patch("src.editor.get_action_sha", return_value="abc123def456"):
        # Mock the print_pinned_action function to avoid console output
        with patch("src.editor.print_pinned_action"):
            result = _pin_actions_in_workflow_content(mock_workflow_content)

    # Check that the already pinned action was not modified
    assert "uses: actions/checkout@1234567890abcdef1234567890abcdef12345678 # v3" in result
    # Check that the non-pinned action was pinned
    assert "uses: actions/setup-node@abc123def456 # v3" in result


def test_pin_private_actions():
    """Test that private actions are not modified"""
    mock_workflow_content = """
name: Test GitHub Action with Private Actions

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - name: Local Action
        uses: ./local-action
      
      - name: Docker Action
        uses: docker://alpine:3.14
        
      - name: Action with Variable
        uses: actions/checkout@${{ env.CHECKOUT_VERSION }}
        
      - name: Standard Action
        uses: actions/setup-node@v3
    """

    # Mock the get_action_sha function to return a fixed SHA
    with patch("src.editor.get_action_sha", return_value="abc123def456"):
        # Mock the print_pinned_action function to avoid console output
        with patch("src.editor.print_pinned_action"):
            result = _pin_actions_in_workflow_content(mock_workflow_content)

    # Check that private actions were not modified
    assert "uses: ./local-action" in result
    assert "uses: docker://alpine:3.14" in result
    assert "uses: actions/checkout@${{ env.CHECKOUT_VERSION }}" in result
    # Check that the standard action was pinned
    assert "uses: actions/setup-node@abc123def456 # v3" in result


def test_pin_action_in_file():
    """Test pinning actions in a file"""
    # Create a temporary file with workflow content
    mock_workflow_content = """
name: Test GitHub Action

jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Run a simple command
        run: echo "This is a basic GitHub Action"
    """

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(mock_workflow_content)
        temp_file_path = temp_file.name

    try:
        # Mock the get_action_sha function to return a fixed SHA
        with patch("src.editor.get_action_sha", return_value="abc123def456"):
            # Mock the print_pinned_action function to avoid console output
            with patch("src.editor.print_pinned_action"):
                # Call the function to pin actions in the file
                pin_action_in_file(temp_file_path)

        # Read the updated file content
        with open(temp_file_path, "r") as f:
            updated_content = f.read()

        # Check that the action was properly pinned with comment
        assert "uses: actions/checkout@abc123def456 # v3" in updated_content

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_pin_action_in_nonexistent_file():
    """Test pinning actions in a nonexistent file"""
    with patch("builtins.print") as mock_print:
        pin_action_in_file("nonexistent_file.yml")
        mock_print.assert_called_with(
            "Error: File 'nonexistent_file.yml' does not exist."
        )


def test_pin_action_in_file_exception():
    """Test exception handling when pinning actions in a file"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=Exception("Test exception")):
            with patch("builtins.print") as mock_print:
                pin_action_in_file(temp_file_path)
                mock_print.assert_called_with(
                    f"Error processing file '{temp_file_path}': Test exception"
                )

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
