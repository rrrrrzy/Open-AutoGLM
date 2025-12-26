"""Main window for Phone Agent UI."""

import sys
import io
import os
from typing import Callable, Optional

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .scheduler import TaskScheduler
from .settings import SettingsManager


class OutputRedirector(io.TextIOBase):
    """Redirect stdout/stderr to signal for UI display."""

    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self._buffer = ""
        self._last_emit_time = 0

    def write(self, text):
        if not text:
            return 0
        
        import time
        current_time = time.time()
        
        # Add text to buffer
        self._buffer += text
        
        # Emit if:
        # 1. Buffer ends with newline
        # 2. Buffer is long enough (>100 chars)
        # 3. Time since last emit > 0.5 seconds
        should_emit = (
            self._buffer.endswith('\n') or 
            len(self._buffer) > 100 or
            (current_time - self._last_emit_time) > 0.5
        )
        
        if should_emit and self._buffer.strip():
            self.signal.emit(self._buffer)
            self._buffer = ""
            self._last_emit_time = current_time
        
        return len(text)

    def flush(self):
        # Emit any remaining buffered content
        if self._buffer.strip():
            self.signal.emit(self._buffer)
            self._buffer = ""


class TaskExecutionThread(QThread):
    """Thread for executing tasks without blocking UI."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    status = pyqtSignal(str)
    input_requested = pyqtSignal(str)  # Signal when input() is called

    def __init__(self, execute_func: Callable, task: str, config: dict):
        """
        Initialize task execution thread.

        Args:
            execute_func: Function to execute the task
            task: Task description
            config: Configuration dictionary
        """
        super().__init__()
        self.execute_func = execute_func
        self.task = task
        self.config = config
        self._stop_requested = False
        self._input_response = None
        self._waiting_for_input = False

    def request_stop(self):
        """Request the thread to stop execution."""
        self._stop_requested = True

    def provide_input(self, response: str):
        """Provide input response from UI."""
        self._input_response = response
        self._waiting_for_input = False

    def run(self):
        """Execute the task."""
        # Redirect stdout and stderr to capture all output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_input = __builtins__.input if hasattr(__builtins__, 'input') else input
        
        def custom_input(prompt=""):
            """Custom input function that signals UI."""
            if prompt:
                self.log.emit(prompt)
            self.input_requested.emit(prompt)
            self._waiting_for_input = True
            
            # Wait for input response
            import time
            timeout = 300  # 5 minutes timeout
            elapsed = 0
            while self._waiting_for_input and not self._stop_requested:
                time.sleep(0.1)
                elapsed += 0.1
                if elapsed > timeout:
                    raise TimeoutError("Input timeout after 5 minutes")
            
            if self._stop_requested:
                raise KeyboardInterrupt("Task terminated by user")
            
            response = self._input_response or ""
            self._input_response = None
            return response
        
        try:
            # Create output redirectors
            stdout_redirector = OutputRedirector(self.log)
            stderr_redirector = OutputRedirector(self.log)
            
            sys.stdout = stdout_redirector
            sys.stderr = stderr_redirector
            
            # Replace built-in input function
            import builtins
            builtins.input = custom_input
            
            self.status.emit("执行中 (Running)")
            self.log.emit(f"开始任务 (Starting task): {self.task}\n")
            self.log.emit("=" * 50 + "\n")
            
            result = self.execute_func(self.task, self.config)
            
            # Flush any remaining output
            stdout_redirector.flush()
            stderr_redirector.flush()
            
            if self._stop_requested:
                self.status.emit("已终止 (Terminated)")
                self.error.emit("任务被用户终止 (Task terminated by user)")
            else:
                self.status.emit("已完成 (Completed)")
                self.finished.emit(result)
                
        except Exception as e:
            self.status.emit("出错 (Error)")
            self.error.emit(str(e))
        finally:
            # Restore original stdout/stderr/input
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            builtins.input = old_input


class MainWindow(QMainWindow):
    """Main window for Phone Agent."""

    def __init__(self, execute_func: Optional[Callable] = None):
        """
        Initialize main window.

        Args:
            execute_func: Function to execute tasks, signature: (task: str, config: dict) -> str
        """
        super().__init__()
        self.execute_func = execute_func
        self.settings = SettingsManager()
        self.scheduler = TaskScheduler()
        self.execution_thread = None
        self._waiting_for_input = False

        # Connect scheduler signal
        self.scheduler.task_triggered.connect(self.on_scheduled_task)

        self.init_ui()
        self.load_settings()
        self.init_tray_icon()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Phone Agent - AI手机自动化")
        self.setMinimumSize(800, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Settings group
        settings_group = QGroupBox("设置 (Settings)")
        settings_layout = QFormLayout()

        # Model settings
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("http://localhost:8000/v1")
        settings_layout.addRow("Base URL:", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("autoglm-phone-9b")
        settings_layout.addRow("Model:", self.model_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("EMPTY")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        settings_layout.addRow("API Key:", self.api_key_input)

        # Agent settings
        self.max_steps_input = QSpinBox()
        self.max_steps_input.setRange(1, 1000)
        self.max_steps_input.setValue(100)
        settings_layout.addRow("Max Steps:", self.max_steps_input)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["cn", "en"])
        settings_layout.addRow("Language:", self.language_combo)

        # Device settings
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItems(["adb", "hdc", "ios"])
        self.device_type_combo.currentTextChanged.connect(self.on_device_type_changed)
        settings_layout.addRow("Device Type:", self.device_type_combo)

        self.device_id_input = QLineEdit()
        self.device_id_input.setPlaceholderText("留空自动检测 (Auto-detect)")
        settings_layout.addRow("Device ID:", self.device_id_input)

        self.wda_url_input = QLineEdit()
        self.wda_url_input.setPlaceholderText("http://localhost:8100")
        settings_layout.addRow("WDA URL (iOS):", self.wda_url_input)

        # Save settings button
        save_settings_btn = QPushButton("保存设置 (Save Settings)")
        save_settings_btn.clicked.connect(self.save_settings)
        settings_layout.addRow("", save_settings_btn)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Task group
        task_group = QGroupBox("任务 (Task)")
        task_layout = QVBoxLayout()

        # Default prompt
        task_layout.addWidget(QLabel("默认提示词 (Default Prompt):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("输入默认任务描述... (Enter default task description...)")
        self.prompt_input.setMaximumHeight(100)
        task_layout.addWidget(self.prompt_input)

        # Task input
        task_layout.addWidget(QLabel("当前任务 (Current Task):"))
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("输入要执行的任务... (Enter task to execute...)")
        self.task_input.setMaximumHeight(100)
        task_layout.addWidget(self.task_input)

        # Task status and control buttons
        control_layout = QHBoxLayout()
        
        # Task status label
        control_layout.addWidget(QLabel("任务状态 (Status):"))
        self.status_label = QLabel("就绪 (Ready)")
        self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        # Execute button
        self.execute_btn = QPushButton("执行任务 (Execute Task)")
        self.execute_btn.clicked.connect(self.execute_task)
        self.execute_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 8px; background-color: #4CAF50; color: white; }")
        control_layout.addWidget(self.execute_btn)
        
        # Terminate button
        self.terminate_btn = QPushButton("终止任务 (Terminate)")
        self.terminate_btn.clicked.connect(self.terminate_task)
        self.terminate_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 8px; background-color: #f44336; color: white; }")
        self.terminate_btn.setEnabled(False)
        control_layout.addWidget(self.terminate_btn)
        
        # Send Enter button
        self.send_enter_btn = QPushButton("发送回车 (Send Enter)")
        self.send_enter_btn.clicked.connect(self.send_enter)
        self.send_enter_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 8px; background-color: #FF9800; color: white; }")
        self.send_enter_btn.setEnabled(False)
        control_layout.addWidget(self.send_enter_btn)
        
        task_layout.addLayout(control_layout)

        task_group.setLayout(task_layout)
        main_layout.addWidget(task_group)

        # Scheduler group
        scheduler_group = QGroupBox("定时执行 (Scheduled Execution)")
        scheduler_layout = QHBoxLayout()

        self.schedule_enabled_checkbox = QCheckBox("启用定时执行 (Enable)")
        self.schedule_enabled_checkbox.stateChanged.connect(self.on_schedule_toggled)
        scheduler_layout.addWidget(self.schedule_enabled_checkbox)

        scheduler_layout.addWidget(QLabel("间隔 (Interval):"))
        self.schedule_interval_input = QSpinBox()
        self.schedule_interval_input.setRange(1, 1440)  # 1 minute to 24 hours
        self.schedule_interval_input.setValue(60)
        self.schedule_interval_input.setSuffix(" 分钟 (min)")
        self.schedule_interval_input.valueChanged.connect(self.on_interval_changed)
        scheduler_layout.addWidget(self.schedule_interval_input)

        scheduler_layout.addStretch()

        scheduler_group.setLayout(scheduler_layout)
        main_layout.addWidget(scheduler_group)

        # Output group
        output_group = QGroupBox("输出 (Output)")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("任务输出将显示在这里... (Task output will appear here...)")
        output_layout.addWidget(self.output_text)

        # Clear output button
        clear_btn = QPushButton("清空输出 (Clear Output)")
        clear_btn.clicked.connect(self.output_text.clear)
        output_layout.addWidget(clear_btn)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Initial device type UI update
        self.on_device_type_changed(self.device_type_combo.currentText())

    def on_device_type_changed(self, device_type: str):
        """Handle device type change."""
        # Show/hide WDA URL based on device type
        is_ios = device_type == "ios"
        self.wda_url_input.setEnabled(is_ios)

    def load_settings(self):
        """Load settings from storage."""
        self.base_url_input.setText(self.settings.get_base_url())
        self.model_input.setText(self.settings.get_model())
        self.api_key_input.setText(self.settings.get_api_key())
        self.prompt_input.setPlainText(self.settings.get_default_prompt())
        self.max_steps_input.setValue(self.settings.get_max_steps())
        self.language_combo.setCurrentText(self.settings.get_language())
        self.device_type_combo.setCurrentText(self.settings.get_device_type())
        self.device_id_input.setText(self.settings.get_device_id())
        self.wda_url_input.setText(self.settings.get_wda_url())
        self.schedule_interval_input.setValue(self.settings.get_schedule_interval())
        self.schedule_enabled_checkbox.setChecked(self.settings.get_schedule_enabled())

    def save_settings(self):
        """Save settings to storage."""
        self.settings.set_base_url(self.base_url_input.text())
        self.settings.set_model(self.model_input.text())
        self.settings.set_api_key(self.api_key_input.text())
        self.settings.set_default_prompt(self.prompt_input.toPlainText())
        self.settings.set_max_steps(self.max_steps_input.value())
        self.settings.set_language(self.language_combo.currentText())
        self.settings.set_device_type(self.device_type_combo.currentText())
        self.settings.set_device_id(self.device_id_input.text())
        self.settings.set_wda_url(self.wda_url_input.text())
        self.settings.set_schedule_interval(self.schedule_interval_input.value())
        self.settings.set_schedule_enabled(self.schedule_enabled_checkbox.isChecked())

        self.log_output("✓ 设置已保存 (Settings saved)\n")

    def get_config(self) -> dict:
        """Get current configuration as dictionary."""
        return {
            "base_url": self.base_url_input.text() or "http://localhost:8000/v1",
            "model": self.model_input.text() or "autoglm-phone-9b",
            "api_key": self.api_key_input.text() or "EMPTY",
            "max_steps": self.max_steps_input.value(),
            "language": self.language_combo.currentText(),
            "device_type": self.device_type_combo.currentText(),
            "device_id": self.device_id_input.text(),
            "wda_url": self.wda_url_input.text() or "http://localhost:8100",
        }

    def execute_task(self):
        """Execute the current task."""
        # Get task from input or use default prompt
        task = self.task_input.toPlainText().strip()
        if not task:
            task = self.prompt_input.toPlainText().strip()

        if not task:
            QMessageBox.warning(
                self, "警告 (Warning)", "请输入任务描述 (Please enter a task description)"
            )
            return

        if not self.execute_func:
            QMessageBox.critical(
                self,
                "错误 (Error)",
                "执行函数未设置 (Execute function not set)\n请使用 --ui 模式启动 (Please start with --ui mode)",
            )
            return

        # Update UI state for execution
        self.execute_btn.setEnabled(False)
        self.terminate_btn.setEnabled(True)
        self.send_enter_btn.setEnabled(False)
        self.update_status("准备中 (Preparing)", "orange")

        # Create and start execution thread
        config = self.get_config()
        self.execution_thread = TaskExecutionThread(self.execute_func, task, config)
        self.execution_thread.finished.connect(self.on_task_finished)
        self.execution_thread.error.connect(self.on_task_error)
        self.execution_thread.log.connect(self.log_output)
        self.execution_thread.status.connect(self.on_status_update)
        self.execution_thread.input_requested.connect(self.on_input_requested)
        self.execution_thread.start()

    def send_enter(self):
        """Send Enter key to continue execution."""
        if self.execution_thread and self.execution_thread.isRunning() and self._waiting_for_input:
            self.log_output("\n✓ 已发送回车 (Enter sent)\n")
            self.execution_thread.provide_input("")
            self.send_enter_btn.setEnabled(False)
            self._waiting_for_input = False

    def on_input_requested(self, prompt: str):
        """Handle input request from execution thread."""
        self._waiting_for_input = True
        self.send_enter_btn.setEnabled(True)
        self.log_output("\n⌨️  等待用户输入... (Waiting for input...)\n")
        if "Press Enter" in prompt or "按回车" in prompt:
            self.log_output('💡 提示：点击"发送回车"按钮继续 (Hint: Click \'Send Enter\' button to continue)\n')

    def terminate_task(self):
        """Terminate the running task."""
        if self.execution_thread and self.execution_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "确认终止 (Confirm Termination)",
                "确定要终止当前任务吗？\n(Are you sure you want to terminate the current task?)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.log_output("\n⚠️ 正在终止任务... (Terminating task...)\n")
                self.execution_thread.request_stop()
                self.execution_thread.terminate()
                self.execution_thread.wait()
                self.update_status("已终止 (Terminated)", "red")
                self.reset_ui_state()

    def update_status(self, status: str, color: str = "green"):
        """Update the status label."""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"QLabel {{ color: {color}; font-weight: bold; }}")

    def reset_ui_state(self):
        """Reset UI to ready state."""
        self.execute_btn.setEnabled(True)
        self.terminate_btn.setEnabled(False)
        self.send_enter_btn.setEnabled(False)
        self._waiting_for_input = False

    def on_status_update(self, status: str):
        """Handle status update from execution thread."""
        color_map = {
            "执行中": "blue",
            "Running": "blue",
            "已完成": "green",
            "Completed": "green",
            "出错": "red",
            "Error": "red",
            "已终止": "red",
            "Terminated": "red",
        }
        color = "blue"
        for key, value in color_map.items():
            if key in status:
                color = value
                break
        self.update_status(status, color)

    def on_task_finished(self, result: str):
        """Handle task completion."""
        self.log_output("\n" + "=" * 50 + "\n")
        self.log_output(f"✅ 结果 (Result): {result}\n")
        self.log_output("=" * 50 + "\n")
        self.reset_ui_state()

    def on_task_error(self, error: str):
        """Handle task error."""
        self.log_output("\n" + "=" * 50 + "\n")
        self.log_output(f"❌ 错误 (Error): {error}\n")
        self.log_output("=" * 50 + "\n")
        QMessageBox.critical(self, "执行错误 (Execution Error)", error)
        self.reset_ui_state()

    def log_output(self, text: str):
        """Append text to output area."""
        self.output_text.append(text)
        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def on_schedule_toggled(self, state: int):
        """Handle schedule checkbox toggle."""
        enabled = state == Qt.CheckState.Checked.value
        if enabled:
            # Save settings and start scheduler
            self.save_settings()
            self.scheduler.set_interval(self.schedule_interval_input.value())
            self.scheduler.start()
            self.log_output(
                f"✓ 定时执行已启动，间隔 {self.schedule_interval_input.value()} 分钟\n"
                f"  (Scheduled execution started, interval: {self.schedule_interval_input.value()} minutes)\n"
            )
        else:
            # Stop scheduler
            self.scheduler.stop()
            self.log_output("✓ 定时执行已停止 (Scheduled execution stopped)\n")

    def on_interval_changed(self, value: int):
        """Handle interval change."""
        if self.scheduler.is_running():
            self.scheduler.set_interval(value)
            self.log_output(f"✓ 定时间隔已更新为 {value} 分钟 (Interval updated to {value} minutes)\n")

    def on_scheduled_task(self):
        """Handle scheduled task trigger."""
        self.log_output("\n" + "=" * 50 + "\n")
        self.log_output("⏰ 定时任务触发 (Scheduled task triggered)\n")
        self.log_output("=" * 50 + "\n")
        self.execute_task()

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop scheduler if running
        if self.scheduler.is_running():
            self.scheduler.stop()

        # Wait for execution thread to finish
        if self.execution_thread and self.execution_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出 (Confirm Exit)",
                "任务正在执行，确定要退出吗？\n任务将被终止。\n(Task is running, are you sure you want to exit?\nThe task will be terminated.)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.execution_thread.request_stop()
                self.execution_thread.terminate()
                self.execution_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def init_tray_icon(self):
        """Initialize system tray icon."""
        # Load icon from image.png in project root
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "image.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Fallback to default icon if image.png not found
            icon = QIcon()

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(icon, self)

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        hide_action = QAction("隐藏窗口", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Double-click tray icon to restore window
        self.tray_icon.activated.connect(self.on_tray_activated)

        # Show tray icon
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        """Show window from system tray."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()

    def changeEvent(self, event):
        """Handle window state changes."""
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                # Hide to tray when minimized
                event.ignore()
                self.hide()
                return
        super().changeEvent(event)


def main():
    """Main entry point for UI testing."""
    app = QApplication(sys.argv)

    # Example execute function
    def example_execute(task: str, config: dict) -> str:
        import time

        time.sleep(2)  # Simulate work
        return f"Task '{task}' completed with config: {config}"

    window = MainWindow(execute_func=example_execute)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
