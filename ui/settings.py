"""Settings manager for Phone Agent UI."""

from PyQt6.QtCore import QSettings


class SettingsManager:
    """Manage application settings using QSettings."""

    def __init__(self):
        """Initialize settings manager."""
        self.settings = QSettings("PhoneAgent", "PhoneAgent")

    def get_base_url(self) -> str:
        """Get base URL setting."""
        return self.settings.value("base_url", "http://localhost:8000/v1")

    def set_base_url(self, base_url: str):
        """Set base URL setting."""
        self.settings.setValue("base_url", base_url)

    def get_model(self) -> str:
        """Get model name setting."""
        return self.settings.value("model", "autoglm-phone-9b")

    def set_model(self, model: str):
        """Set model name setting."""
        self.settings.setValue("model", model)

    def get_api_key(self) -> str:
        """Get API key setting."""
        return self.settings.value("api_key", "EMPTY")

    def set_api_key(self, api_key: str):
        """Set API key setting."""
        self.settings.setValue("api_key", api_key)

    def get_default_prompt(self) -> str:
        """Get default prompt setting."""
        return self.settings.value("default_prompt", "")

    def set_default_prompt(self, prompt: str):
        """Set default prompt setting."""
        self.settings.setValue("default_prompt", prompt)

    def get_max_steps(self) -> int:
        """Get max steps setting."""
        return int(self.settings.value("max_steps", 100))

    def set_max_steps(self, max_steps: int):
        """Set max steps setting."""
        self.settings.setValue("max_steps", max_steps)

    def get_language(self) -> str:
        """Get language setting."""
        return self.settings.value("language", "cn")

    def set_language(self, language: str):
        """Set language setting."""
        self.settings.setValue("language", language)

    def get_device_type(self) -> str:
        """Get device type setting."""
        return self.settings.value("device_type", "adb")

    def set_device_type(self, device_type: str):
        """Set device type setting."""
        self.settings.setValue("device_type", device_type)

    def get_device_id(self) -> str:
        """Get device ID setting."""
        return self.settings.value("device_id", "")

    def set_device_id(self, device_id: str):
        """Set device ID setting."""
        self.settings.setValue("device_id", device_id)

    def get_wda_url(self) -> str:
        """Get WDA URL setting (iOS)."""
        return self.settings.value("wda_url", "http://localhost:8100")

    def set_wda_url(self, wda_url: str):
        """Set WDA URL setting (iOS)."""
        self.settings.setValue("wda_url", wda_url)

    def get_schedule_enabled(self) -> bool:
        """Get schedule enabled setting."""
        return self.settings.value("schedule_enabled", False, type=bool)

    def set_schedule_enabled(self, enabled: bool):
        """Set schedule enabled setting."""
        self.settings.setValue("schedule_enabled", enabled)

    def get_schedule_interval(self) -> int:
        """Get schedule interval in minutes."""
        return int(self.settings.value("schedule_interval", 60))

    def set_schedule_interval(self, interval: int):
        """Set schedule interval in minutes."""
        self.settings.setValue("schedule_interval", interval)
