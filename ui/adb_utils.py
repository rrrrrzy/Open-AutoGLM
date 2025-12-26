"""ADB utility functions for UI automation."""

import time
from phone_agent.subprocess_utils import run_hidden


def wake_screen(device_id: str = "") -> bool:
    """
    Wake up the device screen using ADB.
    
    Args:
        device_id: Device ID (empty for default device)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Build ADB command
        adb_cmd = ["adb"]
        if device_id:
            adb_cmd.extend(["-s", device_id])
        
        # Press power key to wake
        cmd = adb_cmd + ["shell", "input", "keyevent", "224"]
        result = run_hidden(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to wake screen: {result.stderr}")
            return False
        
        time.sleep(2)
        
        # Swipe up to unlock (x1 y1 x2 y2 duration_ms)
        cmd = adb_cmd + ["shell", "input", "swipe", "500", "1500", "500", "500", "300"]
        result = run_hidden(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to unlock screen: {result.stderr}")
            return False
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"Error waking screen: {e}")
        return False


def lock_screen(device_id: str = "") -> bool:
    """
    Lock the device screen using ADB.
    
    Args:
        device_id: Device ID (empty for default device)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Build ADB command
        adb_cmd = ["adb"]
        if device_id:
            adb_cmd.extend(["-s", device_id])
        
        # Press power key to lock (keyevent 223 = KEYCODE_SLEEP)
        cmd = adb_cmd + ["shell", "input", "keyevent", "223"]
        result = run_hidden(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to lock screen: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error locking screen: {e}")
        return False


def kill_app(package_name: str, device_id: str = "") -> bool:
    """
    Force stop an app using ADB.
    
    Args:
        package_name: Package name of the app (e.g., "com.example.app")
        device_id: Device ID (empty for default device)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not package_name:
            print("Package name is required")
            return False
        
        # Build ADB command
        adb_cmd = ["adb"]
        if device_id:
            adb_cmd.extend(["-s", device_id])
        
        # Force stop the app
        cmd = adb_cmd + ["shell", "am", "force-stop", package_name]
        result = run_hidden(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to kill app {package_name}: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error killing app: {e}")
        return False
