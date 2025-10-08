"""
Validation utilities for the Cosmic Council system.
"""

import re
import uuid
from typing import Any, Dict, List, Optional
from email_validator import validate_email as _validate_email, EmailNotValidError


def validate_input(data: Any, required_fields: List[str] = None, data_type: type = None) -> bool:
    """Validate input data"""
    try:
        # Check if data is None
        if data is None:
            return False
        
        # Check data type
        if data_type and not isinstance(data, data_type):
            return False
        
        # Check required fields for dictionaries
        if isinstance(data, dict) and required_fields:
            for field in required_fields:
                if field not in data:
                    return False
        
        return True
        
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email address"""
    try:
        _validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID string"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
    """Validate string length"""
    if not isinstance(text, str):
        return False
    
    if len(text) < min_length:
        return False
    
    if max_length and len(text) > max_length:
        return False
    
    return True


def validate_numeric_range(value: Any, min_value: float = None, max_value: float = None) -> bool:
    """Validate numeric value is within range"""
    try:
        num_value = float(value)
        
        if min_value is not None and num_value < min_value:
            return False
        
        if max_value is not None and num_value > max_value:
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate data against JSON schema (simplified)"""
    try:
        for field, rules in schema.items():
            if field not in data:
                if rules.get('required', False):
                    return False
                continue
            
            value = data[field]
            
            # Check type
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                return False
            
            # Check string length
            if isinstance(value, str):
                min_length = rules.get('min_length', 0)
                max_length = rules.get('max_length')
                if not validate_string_length(value, min_length, max_length):
                    return False
            
            # Check numeric range
            if isinstance(value, (int, float)):
                min_value = rules.get('min_value')
                max_value = rules.get('max_value')
                if not validate_numeric_range(value, min_value, max_value):
                    return False
        
        return True
        
    except Exception:
        return False


def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return 0 <= file_size <= max_size
