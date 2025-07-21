"""
Raposa Identity Service Client

Handles communication with the Raposa Identity Service for user authentication,
profile management, and JWT token validation.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


class IdentityServiceClient:
    """Client for interacting with the Raposa Identity Service"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    async def register_user(self, email: str, password: str, 
                          first_name: Optional[str] = None, 
                          last_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Register a new user with the identity service"""
        try:
            # Generate a valid username from email (letters, numbers, underscores, hyphens only)
            username = email.split('@')[0].replace('.', '_').replace('+', '_')
            # Ensure username only contains valid characters
            import re
            username = re.sub(r'[^a-zA-Z0-9_-]', '_', username)
            
            payload = {
                "email": email,
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
            
            print(f"[DEBUG] Registration payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/register",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"[DEBUG] Registration response status: {response.status_code}")
                print(f"[DEBUG] Registration response text: {response.text}")
                
                if response.status_code == 201:
                    return response.json()
                else:
                    logger.error(f"Registration failed with status {response.status_code}: {response.text}")
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to register user: {e}")
            return None
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get JWT tokens"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    headers=self.headers,
                    json={
                        "email": email,
                        "password": password
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to login user: {e}")
            raise
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers={
                        **self.headers,
                        "Authorization": f"Bearer {token}"
                    }
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to validate token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh JWT token using refresh token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/refresh",
                    headers=self.headers,
                    json={"refresh_token": refresh_token}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to refresh token: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, 
                                profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/users/{user_id}",
                    headers=self.headers,
                    json=profile_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to update user profile: {e}")
            return None
    
    async def change_password(self, user_id: str, current_password: str, 
                            new_password: str) -> bool:
        """Change user password"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/{user_id}/change-password",
                    headers=self.headers,
                    json={
                        "current_password": current_password,
                        "new_password": new_password
                    }
                )
                return response.status_code == 200
        except httpx.HTTPError as e:
            logger.error(f"Failed to change password: {e}")
            return False
    
    async def request_email_verification(self, user_id: str) -> bool:
        """Request email verification for user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/{user_id}/verify-email",
                    headers=self.headers
                )
                return response.status_code == 200
        except httpx.HTTPError as e:
            logger.error(f"Failed to request email verification: {e}")
            return False


@lru_cache()
def get_identity_client() -> IdentityServiceClient:
    """Get configured identity service client"""
    base_url = os.getenv("IDENTITY_SERVICE_URL", "https://raposa-identity-production.up.railway.app")
    
    return IdentityServiceClient(base_url)
