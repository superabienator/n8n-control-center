"""
Autostart Manager for n8n Control Center Pro.
Manages system autostart across Windows, Linux, and macOS.
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Optional


class AutostartManager:
    """Handles enabling, disabling, and checking operating system autostart."""

    APP_NAME = "n8nControlCenter"
    APP_DISPLAY_NAME = "n8n Control Center Pro"

    def __init__(self, target_executable: Optional[str] = None):
        self.system = platform.system()
        self.target_path = target_executable or self._resolve_target_executable()

    def _resolve_target_executable(self) -> str:
        """
        Resolves the preferred launch command:
        1. If running as a frozen PyInstaller binary, return sys.executable.
        2. If dist/n8n-control-center.exe exists, return that.
        3. Fallback to current python + main.py.
        """
        if getattr(sys, "frozen", False):
            return str(Path(sys.executable).resolve())

        base_dir = Path(__file__).parent.resolve()

        # Check compiled binary in dist/
        if self.system == "Windows":
            candidate = base_dir / "dist" / "n8n-control-center.exe"
            if candidate.exists():
                return str(candidate.resolve())
            bat_launcher = base_dir / "iniciar_windows.bat"
            if bat_launcher.exists():
                return str(bat_launcher.resolve())
        else:
            candidate = base_dir / "dist" / "n8n-control-center"
            if candidate.exists():
                return str(candidate.resolve())
            sh_launcher = base_dir / "iniciar_mac_linux.sh"
            if sh_launcher.exists():
                return str(sh_launcher.resolve())

        # Fallback to python executable with main.py
        py_exec = sys.executable
        main_py = base_dir / "main.py"
        return f'"{py_exec}" "{main_py}"'

    # =========================================================================
    # Windows Implementation (winreg)
    # =========================================================================
    def _is_windows_enabled(self) -> bool:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            try:
                winreg.QueryValueEx(key, self.APP_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception:
            return False

    def _enable_windows(self) -> bool:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            # Ensure path is properly quoted if it has spaces and isn't already quoted
            cmd = self.target_path.strip()
            if not cmd.startswith('"') and " " in cmd and not cmd.endswith('"'):
                cmd = f'"{cmd}"'

            winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"[AutostartManager] Error enabling Windows autostart: {e}")
            return False

    def _disable_windows(self) -> bool:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            try:
                winreg.DeleteValue(key, self.APP_NAME)
            except FileNotFoundError:
                pass
            finally:
                winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"[AutostartManager] Error disabling Windows autostart: {e}")
            return False

    # =========================================================================
    # Linux Implementation (~/.config/autostart/*.desktop)
    # =========================================================================
    def _get_linux_desktop_path(self) -> Path:
        return Path.home() / ".config" / "autostart" / f"{self.APP_NAME.lower()}.desktop"

    def _is_linux_enabled(self) -> bool:
        return self._get_linux_desktop_path().exists()

    def _enable_linux(self) -> bool:
        try:
            p = self._get_linux_desktop_path()
            p.parent.mkdir(parents=True, exist_ok=True)
            cmd = self.target_path.strip()
            content = f"""[Desktop Entry]
Type=Application
Exec={cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={self.APP_DISPLAY_NAME}
Comment=Iniciar n8n Control Center Pro al iniciar sesión
"""
            p.write_text(content, encoding="utf-8")
            os.chmod(p, 0o755)
            return True
        except Exception as e:
            print(f"[AutostartManager] Error enabling Linux autostart: {e}")
            return False

    def _disable_linux(self) -> bool:
        try:
            p = self._get_linux_desktop_path()
            if p.exists():
                p.unlink()
            return True
        except Exception as e:
            print(f"[AutostartManager] Error disabling Linux autostart: {e}")
            return False

    # =========================================================================
    # macOS Implementation (~/Library/LaunchAgents/*.plist)
    # =========================================================================
    def _get_mac_plist_path(self) -> Path:
        return Path.home() / "Library" / "LaunchAgents" / "com.n8ncontrol.plist"

    def _is_mac_enabled(self) -> bool:
        return self._get_mac_plist_path().exists()

    def _enable_mac(self) -> bool:
        try:
            p = self._get_mac_plist_path()
            p.parent.mkdir(parents=True, exist_ok=True)
            cmd = self.target_path.strip()
            content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.n8ncontrol</string>
    <key>ProgramArguments</key>
    <array>
        <string>{cmd}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
            p.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[AutostartManager] Error enabling macOS autostart: {e}")
            return False

    def _disable_mac(self) -> bool:
        try:
            p = self._get_mac_plist_path()
            if p.exists():
                p.unlink()
            return True
        except Exception as e:
            print(f"[AutostartManager] Error disabling macOS autostart: {e}")
            return False

    # =========================================================================
    # Public Unified API
    # =========================================================================
    def is_autostart_enabled(self) -> bool:
        """Returns True if autostart is currently configured for this OS."""
        if self.system == "Windows":
            return self._is_windows_enabled()
        elif self.system == "Linux":
            return self._is_linux_enabled()
        elif self.system == "Darwin":
            return self._is_mac_enabled()
        return False

    def enable_autostart(self) -> bool:
        """Registers the application to launch automatically on user login."""
        if self.system == "Windows":
            return self._enable_windows()
        elif self.system == "Linux":
            return self._enable_linux()
        elif self.system == "Darwin":
            return self._enable_mac()
        return False

    def disable_autostart(self) -> bool:
        """Unregisters the application from system autostart."""
        if self.system == "Windows":
            return self._disable_windows()
        elif self.system == "Linux":
            return self._disable_linux()
        elif self.system == "Darwin":
            return self._disable_mac()
        return False
