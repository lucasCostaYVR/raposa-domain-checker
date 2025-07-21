"""
Authentication dependencies for FastAPI

Provides dependency injection for user authentication, token validation,
and authorization checks using the Raposa Identity Service.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .identity_client import get_identity_client

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


class User:
    """User model from JWT token data"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.id = str(user_data.get("id"))  # Convert to string for DB consistency
        self.email = user_data.get("email")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.email_verified = user_data.get("email_verified", False)
        self.created_at = user_data.get("created_at")
        self.subscription_tier = user_data.get("subscription_tier", "free")
        self.raw_data = user_data
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email or "Unknown User"
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in ["premium", "pro", "enterprise"]


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    identity_client = Depends(get_identity_client)
) -> Optional[User]:
    """
    Get current user from JWT token (optional).
    Returns None if no token provided or token is invalid.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = await identity_client.validate_token(token)
        
        if user_data and user_data.get("id"):
            return User(user_data)
        else:
            return None
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    identity_client = Depends(get_identity_client)
) -> User:
    """
    Get current user from JWT token (required).
    Raises 401 if no token provided or token is invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user_data = await identity_client.validate_token(token)
        
        if user_data and user_data.get("id"):
            return User(user_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user with email verification requirement.
    Raises 403 if user's email is not verified.
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email address."
        )
    
    return current_user


async def get_premium_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user with premium subscription requirement.
    Raises 403 if user doesn't have premium subscription.
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required for this feature."
        )
    
    return current_user


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    Handles X-Forwarded-For and X-Real-IP headers for proxy setups.
    """
    # Check X-Forwarded-For header (comma-separated list, first is original client)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"
