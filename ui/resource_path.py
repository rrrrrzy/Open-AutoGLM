"""Utility functions for resource path handling in packaged applications."""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for both development and PyInstaller builds.
    
    When running as a PyInstaller bundle:
    - sys.frozen is True
    - sys._MEIPASS contains the temporary folder where PyInstaller extracts resources
    
    Args:
        relative_path: Relative path to the resource file
        
    Returns:
        Absolute path to the resource file
        
    Example:
        >>> icon_path = get_resource_path("image.png")
        >>> config_path = get_resource_path("resources/privacy_policy.txt")
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def is_packaged() -> bool:
    """
    Check if the application is running as a packaged executable.
    
    Returns:
        True if running as PyInstaller bundle, False otherwise
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
