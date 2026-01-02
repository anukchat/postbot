"""
Authentication module providing pluggable auth provider support.

Supports multiple OAuth providers (Supabase, Auth0, Clerk) with a unified interface.
"""
from .base import AuthProvider, AuthUser, AuthSession
from .factory import AuthProviderFactory, get_auth_provider

__all__ = [
    "AuthProvider",
    "AuthUser", 
    "AuthSession",
    "AuthProviderFactory",
    "get_auth_provider"
]
