"""
Cosmic Council Refinement Engine - Security Tests
Comprehensive security testing suite for authentication, authorization, and input validation.
"""

import pytest
import asyncio
import json
import hashlib
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from .security import (
    SecurityManager, User, APIKey, Permission, UserRole,
    LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
    get_security_manager, initialize_security
)
from .secure_api import app
from .security_config import get_security_config, validate_security_config, SecurityLevel


class TestSecurityManager:
    """Test cases for SecurityManager."""
    
    @pytest.fixture
    def security_manager(self):
        """Create a test security manager."""
        return SecurityManager()
    
    @pytest.fixture
    def test_user_data(self):
        """Test user data."""
        return UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            role="user"
        )
    
    def test_password_hashing(self, security_manager):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = security_manager.hash_password(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Hash should be verifiable
        assert security_manager.verify_password(password, hashed)
        
        # Wrong password should not verify
        assert not security_manager.verify_password("WrongPassword", hashed)
    
    def test_jwt_token_creation_and_verification(self, security_manager):
        """Test JWT token creation and verification."""
        user_id = "test-user-id"
        permissions = {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        
        # Create token
        token = security_manager.create_access_token(user_id, permissions)
        assert token is not None
        assert len(token) > 0
        
        # Verify token
        payload = security_manager.verify_access_token(token)
        assert payload["sub"] == user_id
        assert set(payload["permissions"]) == {p.value for p in permissions}
        
        # Test expired token
        with patch.object(security_manager, 'access_token_expire_minutes', -1):
            expired_token = security_manager.create_access_token(user_id, permissions)
            with pytest.raises(HTTPException) as exc_info:
                security_manager.verify_access_token(expired_token)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_creation(self, security_manager, test_user_data):
        """Test user creation."""
        # Create user
        user = asyncio.run(security_manager.create_user(test_user_data))
        
        assert user.username == test_user_data.username
        assert user.email == test_user_data.email
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.user_id is not None
        
        # Check if user is stored
        assert test_user_data.username in security_manager.users
        
        # Test duplicate username
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(security_manager.create_user(test_user_data))
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_authentication(self, security_manager, test_user_data):
        """Test user authentication."""
        # Create user
        user = asyncio.run(security_manager.create_user(test_user_data))
        
        # Test successful authentication
        authenticated_user = asyncio.run(
            security_manager.authenticate_user(
                test_user_data.username,
                test_user_data.password
            )
        )
        
        assert authenticated_user is not None
        assert authenticated_user.username == test_user_data.username
        
        # Test failed authentication
        failed_user = asyncio.run(
            security_manager.authenticate_user(
                test_user_data.username,
                "WrongPassword"
            )
        )
        
        assert failed_user is None
        
        # Test non-existent user
        non_existent_user = asyncio.run(
            security_manager.authenticate_user(
                "nonexistent",
                "password"
            )
        )
        
        assert non_existent_user is None
    
    def test_brute_force_protection(self, security_manager, test_user_data):
        """Test brute force protection."""
        # Create user
        user = asyncio.run(security_manager.create_user(test_user_data))
        
        # Attempt multiple failed logins
        for _ in range(security_manager.config["max_login_attempts"]):
            result = asyncio.run(
                security_manager.authenticate_user(
                    test_user_data.username,
                    "WrongPassword"
                )
            )
            assert result is None
        
        # User should be locked
        assert user.locked_until is not None
        assert user.locked_until > datetime.utcnow()
        
        # Authentication should fail even with correct password
        locked_user = asyncio.run(
            security_manager.authenticate_user(
                test_user_data.username,
                test_user_data.password
            )
        )
        
        assert locked_user is None
    
    def test_api_key_creation_and_authentication(self, security_manager, test_user_data):
        """Test API key creation and authentication."""
        # Create user
        user = asyncio.run(security_manager.create_user(test_user_data))
        
        # Create API key
        permissions = {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        api_key = asyncio.run(
            security_manager.create_api_key(
                "test-key",
                user.user_id,
                permissions
            )
        )
        
        assert api_key is not None
        assert len(api_key) > 0
        
        # Authenticate API key
        api_key_record = asyncio.run(
            security_manager.authenticate_api_key(api_key)
        )
        
        assert api_key_record is not None
        assert api_key_record.name == "test-key"
        assert api_key_record.user_id == user.user_id
        assert api_key_record.permissions == permissions
        
        # Test invalid API key
        invalid_key = asyncio.run(
            security_manager.authenticate_api_key("invalid-key")
        )
        
        assert invalid_key is None
    
    def test_permission_checking(self, security_manager):
        """Test permission checking."""
        user_permissions = {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        
        # Test single permission
        assert security_manager.check_permission(user_permissions, Permission.CREATE_PROBLEM)
        assert not security_manager.check_permission(user_permissions, Permission.DELETE_PROBLEM)
        
        # Test multiple permissions
        required_permissions = {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        assert security_manager.check_permissions(user_permissions, required_permissions)
        
        required_permissions = {Permission.CREATE_PROBLEM, Permission.DELETE_PROBLEM}
        assert not security_manager.check_permissions(user_permissions, required_permissions)
    
    def test_rate_limiting(self, security_manager):
        """Test rate limiting."""
        identifier = "test-identifier"
        limit = 5
        window = 60
        
        # Test within limit
        for i in range(limit):
            result = asyncio.run(
                security_manager.rate_limit_check(identifier, limit, window)
            )
            assert result is True
        
        # Test exceeding limit
        result = asyncio.run(
            security_manager.rate_limit_check(identifier, limit, window)
        )
        assert result is False
    
    def test_input_sanitization(self, security_manager):
        """Test input sanitization."""
        # Test SQL injection
        malicious_input = "'; DROP TABLE users; --"
        sanitized = security_manager.sanitize_input(malicious_input)
        assert "DROP TABLE" not in sanitized
        
        # Test XSS
        xss_input = "<script>alert('XSS')</script>"
        sanitized = security_manager.sanitize_input(xss_input)
        assert "<script>" not in sanitized
        
        # Test JavaScript protocol
        js_input = "javascript:alert('XSS')"
        sanitized = security_manager.sanitize_input(js_input)
        assert "javascript:" not in sanitized
    
    def test_problem_input_validation(self, security_manager):
        """Test problem input validation."""
        # Valid input
        valid_data = {
            "title": "Test Problem",
            "description": "This is a test problem description",
            "initial_layer": "deci",
            "max_iterations": 100
        }
        
        validated = security_manager.validate_problem_input(valid_data)
        assert validated["title"] == "Test Problem"
        assert validated["description"] == "This is a test problem description"
        assert validated["initial_layer"] == "deci"
        assert validated["max_iterations"] == 100
        
        # Invalid title length
        invalid_data = {
            "title": "Hi",
            "description": "This is a test problem description",
            "initial_layer": "deci",
            "max_iterations": 100
        }
        
        with pytest.raises(HTTPException) as exc_info:
            security_manager.validate_problem_input(invalid_data)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Invalid layer
        invalid_data = {
            "title": "Test Problem",
            "description": "This is a test problem description",
            "initial_layer": "invalid",
            "max_iterations": 100
        }
        
        with pytest.raises(HTTPException) as exc_info:
            security_manager.validate_problem_input(invalid_data)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestInputValidation:
    """Test cases for input validation."""
    
    def test_login_request_validation(self):
        """Test login request validation."""
        # Valid request
        valid_request = LoginRequest(
            username="testuser",
            password="TestPassword123!"
        )
        assert valid_request.username == "testuser"
        assert valid_request.password == "TestPassword123!"
        
        # Invalid username
        with pytest.raises(ValueError):
            LoginRequest(
                username="test user",  # Contains space
                password="TestPassword123!"
            )
        
        # Invalid password
        with pytest.raises(ValueError):
            LoginRequest(
                username="testuser",
                password="weak"  # Too weak
            )
    
    def test_problem_submission_validation(self):
        """Test problem submission validation."""
        # Valid request
        valid_request = ProblemSubmissionRequest(
            title="Test Problem",
            description="This is a test problem description",
            initial_layer="deci",
            max_iterations=100
        )
        assert valid_request.title == "Test Problem"
        assert valid_request.description == "This is a test problem description"
        assert valid_request.initial_layer == "deci"
        assert valid_request.max_iterations == 100
        
        # Invalid title
        with pytest.raises(ValueError):
            ProblemSubmissionRequest(
                title="Hi",  # Too short
                description="This is a test problem description",
                initial_layer="deci",
                max_iterations=100
            )
        
        # Invalid layer
        with pytest.raises(ValueError):
            ProblemSubmissionRequest(
                title="Test Problem",
                description="This is a test problem description",
                initial_layer="invalid",
                max_iterations=100
            )
    
    def test_user_creation_validation(self):
        """Test user creation validation."""
        # Valid request
        valid_request = UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            role="user"
        )
        assert valid_request.username == "testuser"
        assert valid_request.email == "test@example.com"
        assert valid_request.password == "TestPassword123!"
        assert valid_request.role == "user"
        
        # Invalid email
        with pytest.raises(ValueError):
            UserCreateRequest(
                username="testuser",
                email="invalid-email",
                password="TestPassword123!",
                role="user"
            )
        
        # Invalid role
        with pytest.raises(ValueError):
            UserCreateRequest(
                username="testuser",
                email="test@example.com",
                password="TestPassword123!",
                role="invalid"
            )


class TestSecureAPI:
    """Test cases for secure API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def test_user_data(self):
        """Test user data."""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "user"
        }
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_user_registration(self, client, test_user_data):
        """Test user registration."""
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]
        assert data["is_active"] is True
    
    def test_user_login(self, client, test_user_data):
        """Test user login."""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_protected_endpoint_without_auth(self, client):
        """Test protected endpoint without authentication."""
        response = client.get("/problems")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_auth(self, client, test_user_data):
        """Test protected endpoint with authentication."""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_response = client.post("/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/problems", headers=headers)
        assert response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Test rate limiting."""
        # Make multiple requests quickly
        for _ in range(65):  # Exceed rate limit
            response = client.get("/health")
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        assert response.status_code == 429
    
    def test_input_validation(self, client, test_user_data):
        """Test input validation."""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_response = client.post("/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid problem submission
        invalid_problem = {
            "title": "Hi",  # Too short
            "description": "Test",
            "initial_layer": "deci",
            "max_iterations": 100
        }
        
        response = client.post("/problems", json=invalid_problem, headers=headers)
        assert response.status_code == 422  # Validation error


class TestSecurityConfiguration:
    """Test cases for security configuration."""
    
    def test_default_configuration(self):
        """Test default security configuration."""
        config = get_security_config()
        
        assert config.environment == SecurityLevel.DEVELOPMENT
        assert config.debug is True
        assert config.enable_rate_limiting is True
        assert config.enable_security_logging is True
        assert config.enable_input_sanitization is True
        assert config.min_password_length == 8
        assert config.max_login_attempts == 5
    
    def test_production_configuration_validation(self):
        """Test production configuration validation."""
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'production',
            'DEBUG': 'false',
            'JWT_SECRET_KEY': 'production-secret-key'
        }):
            config = get_security_config()
            issues = validate_security_config(config)
            
            # Should have no issues for proper production config
            assert len(issues) == 0
    
    def test_development_configuration_validation(self):
        """Test development configuration validation."""
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'development',
            'DEBUG': 'true',
            'JWT_SECRET_KEY': 'development-secret-key'
        }):
            config = get_security_config()
            issues = validate_security_config(config)
            
            # Should have no issues for development config
            assert len(issues) == 0
    
    def test_invalid_production_configuration(self):
        """Test invalid production configuration."""
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'production',
            'DEBUG': 'true',  # Should be false in production
            'JWT_SECRET_KEY': 'development-secret-key',  # Should be changed
            'ENABLE_RATE_LIMITING': 'false',  # Should be true in production
            'ENABLE_SECURITY_LOGGING': 'false'  # Should be true in production
        }):
            config = get_security_config()
            issues = validate_security_config(config)
            
            # Should have multiple issues
            assert len(issues) > 0
            assert any("Debug mode should be disabled" in issue for issue in issues)
            assert any("JWT secret key must be changed" in issue for issue in issues)
            assert any("Rate limiting should be enabled" in issue for issue in issues)
            assert any("Security logging should be enabled" in issue for issue in issues)


class TestSecurityIntegration:
    """Integration tests for security features."""
    
    @pytest.fixture
    def security_manager(self):
        """Create test security manager."""
        return SecurityManager()
    
    def test_end_to_end_authentication_flow(self, security_manager):
        """Test complete authentication flow."""
        # Create user
        user_data = UserCreateRequest(
            username="integrationuser",
            email="integration@example.com",
            password="IntegrationPassword123!",
            role="user"
        )
        
        user = asyncio.run(security_manager.create_user(user_data))
        assert user is not None
        
        # Authenticate user
        authenticated_user = asyncio.run(
            security_manager.authenticate_user(
                user_data.username,
                user_data.password
            )
        )
        assert authenticated_user is not None
        
        # Create access token
        token = security_manager.create_access_token(
            authenticated_user.user_id,
            authenticated_user.permissions
        )
        assert token is not None
        
        # Verify token
        payload = security_manager.verify_access_token(token)
        assert payload["sub"] == authenticated_user.user_id
        
        # Create API key
        api_key = asyncio.run(
            security_manager.create_api_key(
                "integration-key",
                authenticated_user.user_id,
                authenticated_user.permissions
            )
        )
        assert api_key is not None
        
        # Authenticate API key
        api_key_record = asyncio.run(
            security_manager.authenticate_api_key(api_key)
        )
        assert api_key_record is not None
    
    def test_security_metrics(self, security_manager):
        """Test security metrics collection."""
        # Create some test data
        user_data = UserCreateRequest(
            username="metricsuser",
            email="metrics@example.com",
            password="MetricsPassword123!",
            role="user"
        )
        
        user = asyncio.run(security_manager.create_user(user_data))
        
        # Simulate some failed login attempts
        for _ in range(3):
            asyncio.run(
                security_manager.authenticate_user(
                    user_data.username,
                    "WrongPassword"
                )
            )
        
        # Check metrics
        assert len(security_manager.users) > 0
        assert user.failed_login_attempts == 3
        
        # Test rate limiting metrics
        identifier = "test-metrics"
        for _ in range(5):
            asyncio.run(
                security_manager.rate_limit_check(identifier, 5, 60)
            )
        
        assert identifier in security_manager.rate_limits
        assert len(security_manager.rate_limits[identifier]) == 5


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
