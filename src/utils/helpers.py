"""
Helper utilities for the Agent Orchestrator system.
"""

import uuid
import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import re


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def format_timestamp(timestamp: Union[datetime, str], format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_string)
    
    return str(timestamp)


def parse_timestamp(timestamp_string: str) -> Optional[datetime]:
    """Parse timestamp string to datetime object"""
    try:
        # Handle ISO format with timezone
        if timestamp_string.endswith('Z'):
            timestamp_string = timestamp_string[:-1] + '+00:00'
        
        return datetime.fromisoformat(timestamp_string)
    except ValueError:
        try:
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_string, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None


def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    # Truncate if too long
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key: str = None) -> List[Any]:
    """Remove duplicates from list"""
    if key:
        seen = set()
        return [item for item in lst if item.get(key) not in seen and not seen.add(item.get(key))]
    else:
        return list(dict.fromkeys(lst))


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with dot notation"""
    keys = key.split('.')
    value = dictionary
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default


def safe_set(dictionary: Dict[str, Any], key: str, value: Any) -> None:
    """Safely set value in dictionary with dot notation"""
    keys = key.split('.')
    current = dictionary
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    current[keys[-1]] = value


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using specified algorithm"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits
    
    if include_symbols:
        characters += "!@#$%^&*"
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters"""
    if not data or len(data) <= visible_chars:
        return "*" * len(data) if data else ""
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def convert_bytes_to_human_readable(bytes_value: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def is_valid_json(json_string: str) -> bool:
    """Check if string is valid JSON"""
    try:
        import json
        json.loads(json_string)
        return True
    except (ValueError, TypeError):
        return False


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    return re.sub(r'\s+', ' ', text.strip())


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def get_timestamp_utc() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)
