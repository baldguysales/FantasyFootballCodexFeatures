"""
Core package for the FF Codex Authentication Service.

This package contains the core functionality and configurations for the authentication service,
including database connections, security utilities, and application settings.
"""
from .config import settings, get_settings
from .database import (
    Base,
    get_db,
    get_async_db,
    get_db_session,
    init_db,
    close_db_connection,
    lifespan,
)
from .logging import logger, setup_logging
from .auth_dependencies import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    get_optional_user,
    credentials_exception,
)

__all__ = [
    # Config
    'settings',
    'get_settings',
    
    # Database
    'Base',
    'get_db',
    'get_async_db',
    'get_db_session',
    'init_db',
    'close_db_connection',
    'lifespan',
    
    # Logging
    'logger',
    'setup_logging',
    
    # Auth Dependencies
    'oauth2_scheme',
    'get_current_user',
    'get_current_active_user',
    'get_current_active_superuser',
    'get_optional_user',
    'credentials_exception',
]
