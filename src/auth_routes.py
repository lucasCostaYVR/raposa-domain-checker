"""
Authentication endpoints for user registration, login, and profile management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import User as UserModel
from src.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, 
    UserProfileResponse, UserProfileUpdateRequest, PasswordChangeRequest
)
from src.auth_dependencies import get_current_user, User
from src.identity_client import get_identity_client
from src.email_service import get_email_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    identity_client = Depends(get_identity_client)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (minimum 8 characters)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **opt_in_marketing**: Opt-in to marketing communications
    
    Returns JWT tokens for immediate authentication.
    """
    try:
        print(f"[DEBUG] Registering user: {request.email}")
        # Register with Identity Service
        identity_response = await identity_client.register_user(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name
        )
        print(f"[DEBUG] Identity response: {identity_response}")
        
        # Create local user record
        user = UserModel(
            id=str(identity_response["id"]),  # Convert integer ID to string
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            email_verified=identity_response.get("is_verified", False),
            subscription_tier="free"  # Default tier for new users
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send welcome email in background
        if request.opt_in_marketing:
            background_tasks.add_task(
                send_welcome_email,
                request.email,
                request.first_name or "there"
            )
        
        # Log the user in to get tokens
        login_response = await identity_client.login_user(
            email=request.email,
            password=request.password
        )
        
        if not login_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration successful, but login failed. Please try logging in manually."
            )
        
        # Return tokens
        return TokenResponse(
            access_token=login_response["access_token"],
            refresh_token=login_response["refresh_token"],
            token_type="bearer",
            expires_in=login_response.get("expires_in", 3600)
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
    identity_client = Depends(get_identity_client)
):
    """
    Authenticate user and get access tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT tokens for API access.
    """
    try:
        # Authenticate with Identity Service
        identity_response = await identity_client.login_user(
            email=request.email,
            password=request.password
        )
        
        # Update local user record
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        if user:
            user.last_login = datetime.utcnow()
            # Sync any updated profile data
            user_data = identity_response.get("user", {})
            if user_data:
                user.email_verified = user_data.get("email_verified", user.email_verified)
                user.subscription_tier = user_data.get("subscription_tier", user.subscription_tier)
            db.commit()
        
        return TokenResponse(
            access_token=identity_response["access_token"],
            refresh_token=identity_response["refresh_token"],
            token_type="bearer",
            expires_in=identity_response.get("expires_in", 3600)
        )
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    identity_client = Depends(get_identity_client)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new JWT tokens.
    """
    try:
        identity_response = await identity_client.refresh_token(refresh_token)
        
        if not identity_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return TokenResponse(
            access_token=identity_response["access_token"],
            refresh_token=identity_response["refresh_token"],
            token_type="bearer",
            expires_in=identity_response.get("expires_in", 3600)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information.
    
    Requires valid JWT token.
    """
    # Get local user data for additional fields
    local_user = db.query(UserModel).filter(UserModel.id == str(current_user.id)).first()
    
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email_verified=current_user.email_verified,
        subscription_tier=current_user.subscription_tier,
        created_at=local_user.created_at if local_user else current_user.created_at,
        last_login=local_user.last_login if local_user else None
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    identity_client = Depends(get_identity_client)
):
    """
    Update user profile information.
    
    - **first_name**: Updated first name
    - **last_name**: Updated last name
    
    Requires valid JWT token.
    """
    try:
        # Update in Identity Service
        await identity_client.update_user_profile(
            user_id=current_user.id,
            profile_data=request.dict(exclude_unset=True)
        )
        
        # Update local record
        local_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if local_user:
            if request.first_name is not None:
                local_user.first_name = request.first_name
            if request.last_name is not None:
                local_user.last_name = request.last_name
            local_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(local_user)
        
        # Return updated profile
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=request.first_name or current_user.first_name,
            last_name=request.last_name or current_user.last_name,
            email_verified=current_user.email_verified,
            subscription_tier=current_user.subscription_tier,
            created_at=local_user.created_at if local_user else current_user.created_at,
            last_login=local_user.last_login if local_user else None
        )
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed. Please try again."
        )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    identity_client = Depends(get_identity_client)
):
    """
    Change user password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    
    Requires valid JWT token.
    """
    try:
        success = await identity_client.change_password(
            user_id=current_user.id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed. Please try again."
        )


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def request_email_verification(
    current_user: User = Depends(get_current_user),
    identity_client = Depends(get_identity_client)
):
    """
    Request email verification for current user.
    
    Requires valid JWT token.
    """
    try:
        success = await identity_client.request_email_verification(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification request failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification request failed. Please try again."
        )


async def send_welcome_email(email: str, first_name: str):
    """Send welcome email to new user"""
    try:
        email_service = get_email_service()
        await email_service.send_welcome_email(
            to_email=email,
            user_name=first_name
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
