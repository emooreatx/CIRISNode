import pytest
import os
from cirisnode.matrix.bot import send_matrix_message

def test_matrix_logging_disabled():
    # Ensure MATRIX_LOGGING_ENABLED is set to false for this test
    original_value = os.getenv("MATRIX_LOGGING_ENABLED")
    os.environ["MATRIX_LOGGING_ENABLED"] = "false"
    
    # Call the function - it should return early since logging is disabled
    result = send_matrix_message("Test message")
    assert result is None
    
    # Restore original value
    if original_value is not None:
        os.environ["MATRIX_LOGGING_ENABLED"] = original_value
    else:
        del os.environ["MATRIX_LOGGING_ENABLED"]

def test_matrix_logging_enabled_incomplete_config():
    # Ensure MATRIX_LOGGING_ENABLED is set to true for this test
    original_enabled = os.getenv("MATRIX_LOGGING_ENABLED")
    original_url = os.getenv("MATRIX_HOMESERVER_URL")
    original_token = os.getenv("MATRIX_ACCESS_TOKEN")
    original_room = os.getenv("MATRIX_ROOM_ID")
    
    os.environ["MATRIX_LOGGING_ENABLED"] = "true"
    os.environ["MATRIX_HOMESERVER_URL"] = ""
    os.environ["MATRIX_ACCESS_TOKEN"] = ""
    os.environ["MATRIX_ROOM_ID"] = ""
    
    # Call the function - it should return early due to incomplete config
    result = send_matrix_message("Test message with incomplete config")
    assert result is None
    
    # Restore original values
    if original_enabled is not None:
        os.environ["MATRIX_LOGGING_ENABLED"] = original_enabled
    else:
        del os.environ["MATRIX_LOGGING_ENABLED"]
        
    if original_url is not None:
        os.environ["MATRIX_HOMESERVER_URL"] = original_url
    else:
        del os.environ["MATRIX_HOMESERVER_URL"]
        
    if original_token is not None:
        os.environ["MATRIX_ACCESS_TOKEN"] = original_token
    else:
        del os.environ["MATRIX_ACCESS_TOKEN"]
        
    if original_room is not None:
        os.environ["MATRIX_ROOM_ID"] = original_room
    else:
        del os.environ["MATRIX_ROOM_ID"]
