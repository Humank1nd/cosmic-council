"""
Unit tests for validation utilities.
"""

import pytest
from src.utils.validation import (
    validate_input, validate_email, validate_uuid,
    validate_string_length, validate_numeric_range
)


class TestValidation:
    """Test validation utilities."""
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid input
        assert validate_input("test", data_type=str) == True
        assert validate_input(123, data_type=int) == True
        assert validate_input({"key": "value"}, required_fields=["key"]) == True
        
        # Invalid input
        assert validate_input(None) == False
        assert validate_input("test", data_type=int) == False
        assert validate_input({"key": "value"}, required_fields=["missing"]) == False
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
        
        # Invalid emails
        assert validate_email("invalid-email") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
    
    def test_validate_uuid(self):
        """Test UUID validation."""
        # Valid UUIDs
        assert validate_uuid("123e4567-e89b-12d3-a456-426614174000") == True
        assert validate_uuid("00000000-0000-0000-0000-000000000000") == True
        
        # Invalid UUIDs
        assert validate_uuid("invalid-uuid") == False
        assert validate_uuid("123") == False
        assert validate_uuid("") == False
    
    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid lengths
        assert validate_string_length("test", min_length=1, max_length=10) == True
        assert validate_string_length("", min_length=0) == True
        
        # Invalid lengths
        assert validate_string_length("", min_length=1) == False
        assert validate_string_length("very long string", max_length=5) == False
        assert validate_string_length(123) == False  # Not a string
    
    def test_validate_numeric_range(self):
        """Test numeric range validation."""
        # Valid ranges
        assert validate_numeric_range(5, min_value=1, max_value=10) == True
        assert validate_numeric_range(0, min_value=0) == True
        assert validate_numeric_range(100, max_value=100) == True
        
        # Invalid ranges
        assert validate_numeric_range(5, min_value=10) == False
        assert validate_numeric_range(5, max_value=1) == False
        assert validate_numeric_range("not a number") == False
