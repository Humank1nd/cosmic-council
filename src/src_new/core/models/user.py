"""
User and stakeholder domain models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseModel


class User(BaseModel):
    """Represents a user in the Cosmic Council system"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = kwargs.get('username', '')
        self.email = kwargs.get('email', '')
        self.full_name = kwargs.get('full_name', '')
        self.role = kwargs.get('role', 'user')
        self.permissions = kwargs.get('permissions', [])
        self.preferences = kwargs.get('preferences', {})
        self.last_login = kwargs.get('last_login')
        self.is_active = kwargs.get('is_active', True)
    
    def validate(self) -> bool:
        """Validate user data"""
        if not self.username or not self.email:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'permissions': self.permissions,
            'preferences': self.preferences,
            'last_login': self.last_login,
            'is_active': self.is_active
        }


class Stakeholder(BaseModel):
    """Represents a stakeholder in a problem"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.role = kwargs.get('role', '')
        self.organization = kwargs.get('organization', '')
        self.influence_level = kwargs.get('influence_level', 'medium')
        self.interest_level = kwargs.get('interest_level', 'medium')
        self.contact_info = kwargs.get('contact_info', {})
        self.notes = kwargs.get('notes', '')
    
    def validate(self) -> bool:
        """Validate stakeholder data"""
        if not self.name:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        return {
            **base_dict,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'organization': self.organization,
            'influence_level': self.influence_level,
            'interest_level': self.interest_level,
            'contact_info': self.contact_info,
            'notes': self.notes
        }
