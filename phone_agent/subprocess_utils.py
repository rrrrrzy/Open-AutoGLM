"""Subprocess utilities for hiding console windows on Windows."""

import subprocess
import sys


def get_subprocess_creation_flags() -> int:
    """
    Get creation flags for subprocess to hide console window on Windows.
    
    On Windows, this returns CREATE_NO_WINDOW flag to prevent console window popup.
    On other platforms, returns 0 (no flags).
    
    Returns:
        Creation flags for subprocess.run/Popen
    """
    if sys.platform == 'win32':
        # Hide console window on Windows
        return subprocess.CREATE_NO_WINDOW
    return 0


def run_hidden(*args, **kwargs):
    """
    Run subprocess.run with console window hidden on Windows.
    
    This is a wrapper around subprocess.run that automatically adds
    the CREATE_NO_WINDOW flag on Windows to prevent console popup.
    
    Args:
        *args: Positional arguments for subprocess.run
        **kwargs: Keyword arguments for subprocess.run
        
    Returns:
        CompletedProcess instance from subprocess.run
        
    Example:
        >>> result = run_hidden(['adb', 'devices'], capture_output=True, text=True)
        >>> result = run_hidden(cmd, timeout=10, check=True)
    """
    # Add creation flags if not already present
    if 'creationflags' not in kwargs:
        kwargs['creationflags'] = get_subprocess_creation_flags()
    
    return subprocess.run(*args, **kwargs)


class HiddenPopen(subprocess.Popen):
    """
    Popen subclass that hides console window on Windows.
    
    Usage:
        >>> process = HiddenPopen(['adb', 'shell', 'ls'], stdout=subprocess.PIPE)
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize Popen with hidden console window on Windows."""
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = get_subprocess_creation_flags()
        super().__init__(*args, **kwargs)
