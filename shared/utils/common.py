"""
Common utility functions for the Cosmic Council system.
Provides frequently used helper functions and utilities.
"""

import uuid
import re
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from enum import Enum

def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime as ISO string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()

def validate_email(email: str) -> bool:
    """Validate an email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string by removing dangerous characters and limiting length."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()
    
    return text

def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm."""
    if algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length."""
    return secrets.token_urlsafe(length)

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text."""
    # Remove HTML tags and special characters
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words and filter
    words = text.lower().split()
    words = [word for word in words if len(word) > 3]
    
    # Count word frequency
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def clean_html(html: str) -> str:
    """Clean HTML by removing tags and entities."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    
    # Decode HTML entities
    import html
    text = html.unescape(text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_uuid(uuid_string: str) -> bool:
    """Validate if a string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime with specified format."""
    return dt.strftime(format_string)

def parse_datetime(date_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime from string."""
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError:
        return None

def timezone_aware(dt: datetime) -> datetime:
    """Make datetime timezone aware if it isn't already."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def validate_enterprise_type(enterprise_type: str) -> bool:
    """Validate enterprise type."""
    valid_types = ["red_research", "orange_logistics", "yellow_development", 
                   "green_budget", "blue_market", "purple_support"]
    return enterprise_type in valid_types

def validate_cycle_status(status: str) -> bool:
    """Validate cycle status."""
    valid_statuses = ["draft", "active", "completed", "failed", "cancelled"]
    return status in valid_statuses

def make_request(url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Make an HTTP request (placeholder for actual implementation)."""
    # TODO: Implement actual HTTP request functionality
    return {"status": "not_implemented", "url": url, "method": method}

def check_url(url: str) -> bool:
    """Check if a URL is accessible."""
    # TODO: Implement actual URL checking
    return True

def get_client_ip(request) -> str:
    """Get client IP address from request."""
    # TODO: Implement actual IP extraction
    return "127.0.0.1"

def read_file(file_path: str) -> str:
    """Read file contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path: str, content: str) -> None:
    """Write content to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def ensure_directory(directory_path: str) -> None:
    """Ensure directory exists."""
    import os
    os.makedirs(directory_path, exist_ok=True)

def get_file_hash(file_path: str) -> str:
    """Get SHA-256 hash of file."""
    import hashlib
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def encrypt_data(data: str, key: str) -> str:
    """Encrypt data (placeholder for actual implementation)."""
    # TODO: Implement actual encryption
    return data

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt data (placeholder for actual implementation)."""
    # TODO: Implement actual decryption
    return encrypted_data
