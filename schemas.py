"""
Pydantic Schemas for Request/Response Validation
Define your API request and response models here.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    environment: str
    database: str

# Add your request/response schemas here
# Example:
# class UserCreateRequest(BaseModel):
#     email: EmailStr
#     username: str
#     password: str
# 
# class UserResponse(BaseModel):
#     id: int
#     email: str
#     username: str
#     created_at: datetime
#     is_active: bool
#     
#     class Config:
#         from_attributes = True
