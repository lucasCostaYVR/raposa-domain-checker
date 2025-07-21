"""
Mock Identity Service Client for Development

This provides a mock implementation of the Identity Service client
for development and testing purposes when the real Identity Service
is not available or configured.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import os

logger = logging.getLogger(__name__)


class MockIdentityServiceClient:
    """Mock client for development and testing"""
    
    def __init__(self, base_url: str = "", service_key: str = ""):
        self.base_url = base_url
        self.service_key = service_key
        # Mock user database
        self.users = {}
        self.tokens = {}
        logger.info("Using Mock Identity Service Client for development")
    
    async def register_user(self, email: str, password: str, 
                          first_name: Optional[str] = None, 
                          last_name: Optional[str] = None) -> Dict[str, Any]:
        """Mock user registration"""
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": True,  # Auto-verify for development
            "subscription_tier": "free",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store user
        self.users[email] = {
            "password": password,  # In real system, this would be hashed
            "user_data": user_data
        }
        
        # Generate tokens
        access_token = f"dev_access_{user_id}_{uuid.uuid4().hex[:8]}"
        refresh_token = f"dev_refresh_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Store tokens
        self.tokens[access_token] = {
            "user_id": user_id,
            "user_data": user_data,
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": user_data
        }
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Mock user login"""
        if email not in self.users:
            raise Exception("User not found")
        
        stored_user = self.users[email]
        if stored_user["password"] != password:
            raise Exception("Invalid password")
        
        user_data = stored_user["user_data"]
        user_id = user_data["id"]
        
        # Generate new tokens
        access_token = f"dev_access_{user_id}_{uuid.uuid4().hex[:8]}"
        refresh_token = f"dev_refresh_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Store tokens
        self.tokens[access_token] = {
            "user_id": user_id,
            "user_data": user_data,
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": user_data
        }
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Mock token validation"""
        if token not in self.tokens:
            return None
        
        token_data = self.tokens[token]
        
        # Check expiration
        if datetime.utcnow() > token_data["expires_at"]:
            return None
        
        return {
            "valid": True,
            "user": token_data["user_data"]
        }
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Mock token refresh"""
        # For development, just generate new tokens
        user_id = str(uuid.uuid4())
        access_token = f"dev_access_{user_id}_{uuid.uuid4().hex[:8]}"
        new_refresh_token = f"dev_refresh_{user_id}_{uuid.uuid4().hex[:8]}"
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mock get user profile"""
        for user_data in self.users.values():
            if user_data["user_data"]["id"] == user_id:
                return user_data["user_data"]
        return None
    
    async def update_user_profile(self, user_id: str, 
                                profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mock profile update"""
        for email, user_data in self.users.items():
            if user_data["user_data"]["id"] == user_id:
                user_data["user_data"].update(profile_data)
                return user_data["user_data"]
        return None
    
    async def change_password(self, user_id: str, current_password: str, 
                            new_password: str) -> bool:
        """Mock password change"""
        for email, user_data in self.users.items():
            if user_data["user_data"]["id"] == user_id:
                if user_data["password"] == current_password:
                    user_data["password"] = new_password
                    return True
                return False
        return False
    
    async def request_email_verification(self, user_id: str) -> bool:
        """Mock email verification request"""
        logger.info(f"Mock: Email verification requested for user {user_id}")
        return True


def get_identity_client():
    """Get configured identity service client (mock for development)"""
    # Check if we're in development mode or missing identity service config
    is_development = os.getenv("ENVIRONMENT") == "development"
    identity_service_key = os.getenv("IDENTITY_SERVICE_KEY")
    
    if is_development or not identity_service_key or identity_service_key == "your-service-key-here":
        logger.info("Using Mock Identity Service Client for development")
        return MockIdentityServiceClient()
    else:
        # Use real identity client
        from .identity_client import IdentityServiceClient
        base_url = os.getenv("IDENTITY_SERVICE_URL", "https://raposa-identity-production.up.railway.app")
        return IdentityServiceClient(base_url, identity_service_key)
