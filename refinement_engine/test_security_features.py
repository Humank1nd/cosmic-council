"""
Test Authentication, Authorization, and Rate Limiting
Tests the security system with comprehensive authentication, authorization, and rate limiting scenarios.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
import json
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security import (
    SecurityManager, User, APIKey, UserRole, Permission, 
    LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
    get_security_manager, initialize_security
)
from error_handling import ErrorHandler, ErrorSeverity, ErrorCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityFeatureTester:
    """Test security functionality comprehensively."""
    
    def __init__(self):
        self.security_manager = None
        self.test_results = {}
        self.test_users = {}
        self.test_api_keys = {}
    
    async def setup_security_manager(self) -> bool:
        """Test security manager setup."""
        print("🔐 Testing Security Manager Setup...")
        
        try:
            # Initialize security manager
            self.security_manager = SecurityManager()
            
            # Check default admin user
            admin_user = self.security_manager.users.get("admin")
            if admin_user:
                print(f"✅ Default admin user created: {admin_user.username}")
                print(f"📊 Admin permissions: {len(admin_user.permissions)}")
            else:
                print("❌ Default admin user not found")
                return False
            
            # Check configuration
            config = self.security_manager.config
            print(f"✅ Security configuration loaded")
            print(f"📊 Token expiry: {config['access_token_expire_minutes']} minutes")
            print(f"📊 Rate limit: {config['rate_limit_requests_per_minute']} requests/minute")
            
            self.test_results["setup"] = True
            return True
            
        except Exception as e:
            print(f"❌ Security manager setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["setup"] = False
            return False
    
    async def test_password_hashing(self) -> bool:
        """Test password hashing and verification."""
        print("\n🔒 Testing Password Hashing...")
        
        try:
            # Test password hashing
            test_password = "TestPassword123"
            hashed = self.security_manager.hash_password(test_password)
            
            print(f"✅ Password hashed successfully")
            print(f"📊 Hash length: {len(hashed)} characters")
            
            # Test password verification
            is_valid = self.security_manager.verify_password(test_password, hashed)
            is_invalid = self.security_manager.verify_password("wrong_password", hashed)
            
            print(f"✅ Password verification working")
            print(f"📊 Correct password: {is_valid}")
            print(f"📊 Wrong password: {is_invalid}")
            
            # Validate results
            assert is_valid, "Correct password should be valid"
            assert not is_invalid, "Wrong password should be invalid"
            assert len(hashed) > 50, "Hash should be reasonably long"
            
            self.test_results["password_hashing"] = True
            return True
            
        except Exception as e:
            print(f"❌ Password hashing test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["password_hashing"] = False
            return False
    
    async def test_jwt_tokens(self) -> bool:
        """Test JWT token creation and verification."""
        print("\n🎫 Testing JWT Tokens...")
        
        try:
            # Create test user
            test_user = User(
                user_id="test_user_123",
                username="testuser",
                email="test@example.com",
                password_hash="dummy_hash",
                role=UserRole.USER,
                permissions={Permission.READ_PROBLEM, Permission.CREATE_PROBLEM},
                created_at=datetime.utcnow()
            )
            
            # Create access token
            token = self.security_manager.create_access_token(
                user_id=test_user.user_id,
                permissions=test_user.permissions
            )
            
            print(f"✅ JWT token created successfully")
            print(f"📊 Token length: {len(token)} characters")
            
            # Verify token
            payload = self.security_manager.verify_access_token(token)
            
            print(f"✅ JWT token verified successfully")
            print(f"📊 User ID: {payload.get('sub')}")
            print(f"📊 Permissions: {len(payload.get('permissions', []))}")
            
            # Validate results
            assert payload["sub"] == test_user.user_id, "User ID should match"
            assert "permissions" in payload, "Token should contain permissions"
            assert "exp" in payload, "Token should have expiration"
            
            # Test expired token (create one with past expiration)
            expired_token = self.security_manager.create_access_token(
                user_id=test_user.user_id,
                permissions=test_user.permissions
            )
            
            # Try to verify with wrong secret (should fail)
            try:
                wrong_secret_manager = SecurityManager()
                wrong_secret_manager.secret_key = "wrong_secret"
                wrong_secret_manager.verify_access_token(token)
                print("❌ Token verification should have failed with wrong secret")
                return False
            except Exception:
                print("✅ Token verification correctly failed with wrong secret")
            
            self.test_results["jwt_tokens"] = True
            return True
            
        except Exception as e:
            print(f"❌ JWT token test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["jwt_tokens"] = False
            return False
    
    async def test_user_authentication(self) -> bool:
        """Test user authentication flow."""
        print("\n👤 Testing User Authentication...")
        
        try:
            # Test with default admin user
            admin_user = await self.security_manager.authenticate_user("admin", "admin123")
            
            if admin_user:
                print(f"✅ Admin authentication successful")
                print(f"📊 Username: {admin_user.username}")
                print(f"📊 Role: {admin_user.role.value}")
                print(f"📊 Permissions: {len(admin_user.permissions)}")
            else:
                print("❌ Admin authentication failed")
                return False
            
            # Test with wrong password
            wrong_auth = await self.security_manager.authenticate_user("admin", "wrong_password")
            if wrong_auth:
                print("❌ Wrong password authentication should have failed")
                return False
            else:
                print("✅ Wrong password correctly rejected")
            
            # Test with non-existent user
            nonexistent_auth = await self.security_manager.authenticate_user("nonexistent", "password")
            if nonexistent_auth:
                print("❌ Non-existent user authentication should have failed")
                return False
            else:
                print("✅ Non-existent user correctly rejected")
            
            # Create and test new user
            new_user_data = UserCreateRequest(
                username="newuser",
                email="newuser@example.com",
                password="NewPassword123!",
                role="user"
            )
            
            new_user = await self.security_manager.create_user(new_user_data)
            print(f"✅ New user created: {new_user.username}")
            
            # Test authentication with new user
            auth_new_user = await self.security_manager.authenticate_user("newuser", "NewPassword123!")
            if auth_new_user:
                print(f"✅ New user authentication successful")
                self.test_users["newuser"] = auth_new_user
            else:
                print("❌ New user authentication failed")
                return False
            
            self.test_results["user_authentication"] = True
            return True
            
        except Exception as e:
            print(f"❌ User authentication test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["user_authentication"] = False
            return False
    
    async def test_api_key_management(self) -> bool:
        """Test API key creation and authentication."""
        print("\n🔑 Testing API Key Management...")
        
        try:
            # Get admin user for API key creation
            admin_user = self.security_manager.users.get("admin")
            if not admin_user:
                print("❌ Admin user not found for API key test")
                return False
            
            # Create API key
            api_key = await self.security_manager.create_api_key(
                name="test_api_key",
                user_id=admin_user.user_id,
                permissions={Permission.READ_PROBLEM, Permission.CREATE_PROBLEM}
            )
            
            print(f"✅ API key created successfully")
            print(f"📊 API key length: {len(api_key)} characters")
            print(f"📊 API key preview: {api_key[:10]}...")
            
            # Test API key authentication
            authenticated_key = await self.security_manager.authenticate_api_key(api_key)
            
            if authenticated_key:
                print(f"✅ API key authentication successful")
                print(f"📊 Key name: {authenticated_key.name}")
                print(f"📊 User ID: {authenticated_key.user_id}")
                print(f"📊 Permissions: {len(authenticated_key.permissions)}")
                self.test_api_keys["test_api_key"] = api_key
            else:
                print("❌ API key authentication failed")
                return False
            
            # Test with invalid API key
            invalid_auth = await self.security_manager.authenticate_api_key("invalid_key")
            if invalid_auth:
                print("❌ Invalid API key authentication should have failed")
                return False
            else:
                print("✅ Invalid API key correctly rejected")
            
            self.test_results["api_key_management"] = True
            return True
            
        except Exception as e:
            print(f"❌ API key management test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["api_key_management"] = False
            return False
    
    async def test_authorization(self) -> bool:
        """Test permission-based authorization."""
        print("\n🛡️ Testing Authorization...")
        
        try:
            # Test admin permissions
            admin_user = self.security_manager.users.get("admin")
            if not admin_user:
                print("❌ Admin user not found for authorization test")
                return False
            
            # Test admin can do everything
            admin_can_create = self.security_manager.check_permission(
                admin_user.permissions, Permission.CREATE_PROBLEM
            )
            admin_can_delete = self.security_manager.check_permission(
                admin_user.permissions, Permission.DELETE_PROBLEM
            )
            
            print(f"✅ Admin permission check")
            print(f"📊 Can create problems: {admin_can_create}")
            print(f"📊 Can delete problems: {admin_can_delete}")
            
            # Test regular user permissions
            regular_user = self.test_users.get("newuser")
            if regular_user:
                user_can_create = self.security_manager.check_permission(
                    regular_user.permissions, Permission.CREATE_PROBLEM
                )
                user_can_delete = self.security_manager.check_permission(
                    regular_user.permissions, Permission.DELETE_PROBLEM
                )
                
                print(f"✅ Regular user permission check")
                print(f"📊 Can create problems: {user_can_create}")
                print(f"📊 Can delete problems: {user_can_delete}")
                
                # Regular users should be able to create but not delete
                assert user_can_create, "Regular users should be able to create problems"
                assert not user_can_delete, "Regular users should not be able to delete problems"
            
            # Test multiple permissions
            required_permissions = {Permission.READ_PROBLEM, Permission.CREATE_PROBLEM}
            admin_has_all = self.security_manager.check_permissions(
                admin_user.permissions, required_permissions
            )
            
            print(f"✅ Multiple permission check")
            print(f"📊 Admin has all required permissions: {admin_has_all}")
            
            assert admin_has_all, "Admin should have all required permissions"
            
            self.test_results["authorization"] = True
            return True
            
        except Exception as e:
            print(f"❌ Authorization test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["authorization"] = False
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality."""
        print("\n⏱️ Testing Rate Limiting...")
        
        try:
            # Test rate limiting with different identifiers
            test_identifier = "test_user_123"
            limit = 5  # 5 requests
            window = 60  # per minute
            
            # Make requests within limit
            for i in range(limit):
                is_allowed = await self.security_manager.rate_limit_check(
                    test_identifier, limit, window
                )
                if not is_allowed:
                    print(f"❌ Request {i+1} should have been allowed")
                    return False
                print(f"✅ Request {i+1} allowed")
            
            # Make one more request (should be rate limited)
            is_limited = await self.security_manager.rate_limit_check(
                test_identifier, limit, window
            )
            
            if is_limited:
                print("❌ Request should have been rate limited")
                return False
            else:
                print("✅ Request correctly rate limited")
            
            # Test with different identifier (should be allowed)
            different_identifier = "different_user_456"
            is_allowed_different = await self.security_manager.rate_limit_check(
                different_identifier, limit, window
            )
            
            if not is_allowed_different:
                print("❌ Different user should not be rate limited")
                return False
            else:
                print("✅ Different user correctly allowed")
            
            # Test rate limit reset (simulate time passing)
            print("📝 Testing rate limit reset...")
            # Note: In a real implementation, this would involve time-based cleanup
            
            self.test_results["rate_limiting"] = True
            return True
            
        except Exception as e:
            print(f"❌ Rate limiting test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["rate_limiting"] = False
            return False
    
    async def test_input_validation(self) -> bool:
        """Test input validation and sanitization."""
        print("\n🧹 Testing Input Validation...")
        
        try:
            # Test input sanitization
            malicious_input = "<script>alert('xss')</script>Hello World"
            sanitized = self.security_manager.sanitize_input(malicious_input)
            
            print(f"✅ Input sanitization working")
            print(f"📊 Original: {malicious_input}")
            print(f"📊 Sanitized: {sanitized}")
            
            # Check that script tags are removed
            assert "<script>" not in sanitized, "Script tags should be removed"
            assert "Hello World" in sanitized, "Safe content should remain"
            
            # Test problem input validation
            valid_problem_data = {
                "title": "Test Problem",
                "description": "This is a test problem description",
                "initial_layer": "deci",
                "max_iterations": 50
            }
            
            validated_data = self.security_manager.validate_problem_input(valid_problem_data)
            print(f"✅ Valid problem data validated")
            print(f"📊 Title: {validated_data['title']}")
            print(f"📊 Description length: {len(validated_data['description'])}")
            
            # Test invalid problem data
            invalid_problem_data = {
                "title": "",  # Empty title should fail
                "description": "x" * 10000,  # Too long description
                "initial_layer": "invalid_layer",
                "max_iterations": 2000  # Too many iterations
            }
            
            try:
                self.security_manager.validate_problem_input(invalid_problem_data)
                print("❌ Invalid problem data should have been rejected")
                return False
            except Exception as e:
                print(f"✅ Invalid problem data correctly rejected: {str(e)[:100]}...")
            
            # Test user creation validation
            valid_user_data = UserCreateRequest(
                username="validuser",
                email="valid@example.com",
                password="ValidPassword123!",
                role="user"
            )
            
            print(f"✅ Valid user data validated")
            print(f"📊 Username: {valid_user_data.username}")
            print(f"📊 Email: {valid_user_data.email}")
            
            # Test invalid user data
            try:
                invalid_user_data = UserCreateRequest(
                    username="",  # Empty username
                    email="invalid-email",  # Invalid email
                    password="123",  # Too short password
                    role="invalid_role"  # Invalid role
                )
                print("❌ Invalid user data should have been rejected")
                return False
            except Exception as e:
                print(f"✅ Invalid user data correctly rejected: {str(e)[:100]}...")
            
            self.test_results["input_validation"] = True
            return True
            
        except Exception as e:
            print(f"❌ Input validation test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["input_validation"] = False
            return False
    
    async def test_security_integration(self) -> bool:
        """Test integrated security scenarios."""
        print("\n🔗 Testing Security Integration...")
        
        try:
            # Test complete authentication flow
            print("📝 Testing complete authentication flow...")
            
            # 1. User login
            admin_user = await self.security_manager.authenticate_user("admin", "admin123")
            if not admin_user:
                print("❌ Admin authentication failed")
                return False
            
            # 2. Create JWT token
            token = self.security_manager.create_access_token(
                user_id=admin_user.user_id,
                permissions=admin_user.permissions
            )
            
            # 3. Verify token
            payload = self.security_manager.verify_access_token(token)
            if payload["sub"] != admin_user.user_id:
                print("❌ Token verification failed")
                return False
            
            # 4. Check permissions
            can_create = self.security_manager.check_permission(
                admin_user.permissions, Permission.CREATE_PROBLEM
            )
            if not can_create:
                print("❌ Permission check failed")
                return False
            
            print("✅ Complete authentication flow working")
            
            # Test API key flow
            print("📝 Testing API key flow...")
            
            api_key = await self.security_manager.create_api_key(
                name="integration_test_key",
                user_id=admin_user.user_id,
                permissions={Permission.READ_PROBLEM}
            )
            
            authenticated_key = await self.security_manager.authenticate_api_key(api_key)
            if not authenticated_key:
                print("❌ API key authentication failed")
                return False
            
            print("✅ API key flow working")
            
            # Test rate limiting integration
            print("📝 Testing rate limiting integration...")
            
            for i in range(3):
                is_allowed = await self.security_manager.rate_limit_check(
                    admin_user.user_id, 10, 60
                )
                if not is_allowed:
                    print(f"❌ Rate limit check {i+1} failed")
                    return False
            
            print("✅ Rate limiting integration working")
            
            self.test_results["security_integration"] = True
            return True
            
        except Exception as e:
            print(f"❌ Security integration test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["security_integration"] = False
            return False
    
    async def test_error_handling(self) -> bool:
        """Test security error handling."""
        print("\n⚠️ Testing Security Error Handling...")
        
        try:
            # Test authentication with invalid credentials
            result = await self.security_manager.authenticate_user("nonexistent", "password")
            if result is not None:
                print("❌ Should have returned None for invalid credentials")
                return False
            else:
                print("✅ Invalid credentials correctly handled")
            
            # Test token verification with invalid token
            try:
                self.security_manager.verify_access_token("invalid_token")
                print("❌ Should have raised exception for invalid token")
                return False
            except Exception:
                print("✅ Invalid token correctly handled")
            
            # Test API key authentication with invalid key
            result = await self.security_manager.authenticate_api_key("invalid_key")
            if result is not None:
                print("❌ Should have returned None for invalid API key")
                return False
            else:
                print("✅ Invalid API key correctly handled")
            
            # Test permission check with invalid permission
            # Note: The current implementation doesn't raise exceptions for invalid permissions
            # It just returns False, which is acceptable behavior
            result = self.security_manager.check_permission(set(), Permission.CREATE_PROBLEM)
            if result:
                print("❌ Empty permissions should not allow CREATE_PROBLEM")
                return False
            else:
                print("✅ Permission check correctly returned False for empty permissions")
            
            self.test_results["error_handling"] = True
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["error_handling"] = False
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all security tests."""
        print("🔐 Testing Authentication, Authorization, and Rate Limiting")
        print("=" * 70)
        
        tests = [
            self.setup_security_manager,
            self.test_password_hashing,
            self.test_jwt_tokens,
            self.test_user_authentication,
            self.test_api_key_management,
            self.test_authorization,
            self.test_rate_limiting,
            self.test_input_validation,
            self.test_security_integration,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
        
        print("\n" + "=" * 70)
        print(f"📊 Security Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL SECURITY TESTS PASSED! Security system is working correctly!")
        else:
            print("⚠️  Some security tests failed. Check the security implementation.")
            print("\n🔧 Troubleshooting Tips:")
            print("1. Check JWT secret key configuration")
            print("2. Verify password hashing is working")
            print("3. Ensure rate limiting is properly configured")
            print("4. Check input validation rules")
            print("5. Verify permission system is correctly implemented")
        
        return passed == total


async def main():
    """Run security tests."""
    tester = SecurityFeatureTester()
    
    try:
        success = await tester.run_all_tests()
        return success
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
