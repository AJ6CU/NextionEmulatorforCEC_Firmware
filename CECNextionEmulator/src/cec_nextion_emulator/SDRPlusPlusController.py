import socket
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Union


class SDRPlusPlusController:
    """
    An advanced object-oriented controller to interface with SDR++ using
    the Hamlib RigCTL network protocol wrapper driven natively by Tkinter's .after() loop.
    Part 1: Initialization, Disk Storage, and Labeled Channel Memory Registries.
    """

    HAM_BANDS = {
        '80m': (3500000, 'LSB', 2700),
        '40m': (7074000, 'USB', 3000),
        '20m': (14200000, 'USB', 2400),
        '15m': (21074000, 'USB', 3000),
        '10m': (28400000, 'USB', 2400),
        '2m': (145000000, 'FM', 12500)
    }

    FACTORY_DEFAULTS = {
        'USB': 2400, 'LSB': 2400, 'CW': 500, 'CW_L': 500, 'CW_U': 500,
        'AM': 6000, 'NFM': 12500, 'FM': 12500, 'WFM': 180000
    }

    JSON_FILE = "sdr_scan_channels.json"

    def __init__(self, root, host: str = '127.0.0.1', port: int = 4532):
        self.root = root
        self.host = host
        self.port = port
        self.sock = None
        self.is_connected = False
        self.is_running = False

        # State tracking cache variables
        self.current_frequency = 0
        self.current_mode = "UNKNOWN"
        self.current_filter_width = 2400

        # Mutatable Fallback Dictionary Registry
        self.DEFAULT_FILTER_FALLBACKS = dict(self.FACTORY_DEFAULTS)

        # Managed Scan Array
        self.scan_channels: List[Dict[str, Union[int, str]]] = []
        self._load_channels_from_json()

        # Scanner runtime properties
        self.is_scanning = False
        self.scan_idx = 0
        self.scan_delay_ms = 2500

        # In-Memory Dictionary Logger Storage
        self.logged_signals: Dict[int, Dict[str, Union[str, int, float]]] = {}

        # Public system event callbacks
        self.on_frequency_change = None
        self.on_mode_change = None
        self.on_filter_change = None
        self.on_scan_step = None
        self.on_disconnect = None
        self.on_incompatible_mode = None

    def connect(self) -> bool:
        if self.sock:
            try:
                self.sock.close()
            except socket.error:
                pass

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(0.15)
            self.sock.connect((self.host, self.port))
            self.is_connected = True

            if not self.is_running:
                self.is_running = True
                self.root.after(300, self._tkinter_tick_loop)
            return True
        except Exception:
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_scan()
        self.is_running = False
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except socket.error:
                pass

    def _handle_unexpected_disconnect(self):
        if self.is_connected:
            self.is_connected = False
            self.stop_scan()
            if self.on_disconnect: self.on_disconnect()

    def _load_channels_from_json(self):
        if os.path.exists(self.JSON_FILE):
            try:
                with open(self.JSON_FILE, 'r', encoding='utf-8') as f:
                    self.scan_channels = json.load(f)
            except Exception:
                self.scan_channels = []

    def _save_channels_to_json(self):
        try:
            with open(self.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.scan_channels, f, indent=4)
        except Exception:
            pass

    def add_channel(self, label: str, freq_hz: int, mode: str, filter_hz: int, name: str) -> bool:
        clean_label = label.strip().upper()
        if not clean_label: return False
        for ch in self.scan_channels:
            if ch["label"] == clean_label: return False

        new_channel = {
            "label": clean_label, "freq_hz": int(freq_hz), "mode": mode.upper().strip(),
            "filter_hz": int(filter_hz), "name": name.strip() if name else f"Station {clean_label}"
        }
        self.scan_channels.append(new_channel)
        self._save_channels_to_json()
        return True

    def delete_channel(self, label: str) -> bool:
        clean_label = label.strip().upper()
        target_idx = -1
        for i, ch in enumerate(self.scan_channels):
            if ch["label"] == clean_label:
                target_idx = i
                break
        if target_idx != -1:
            was_scanning = self.is_scanning
            self.stop_scan()
            self.scan_channels.pop(target_idx)
            self._save_channels_to_json()
            if was_scanning and self.scan_channels:
                self.scan_idx = 0
                self.is_scanning = True
                self._tkinter_scan_tick()
            return True
        return False

    def list_all_channels(self) -> Dict[str, Dict[str, Union[int, str]]]:
        channels_dict = {}
        for ch in self.scan_channels:
            channels_dict[ch["label"]] = {
                "freq_hz": ch["freq_hz"], "mode": ch["mode"], "filter_hz": ch["filter_hz"], "name": ch["name"]
            }
        return channels_dict

    # =========================================================================
    #  CROSS-PLATFORM NATIVE HARDWARE SYSTEM VOLUME UTILITIES
    # =========================================================================
    def get_system_volume(self) -> int:
        """Queries the OS audio subsystem directly to determine the initialization volume level."""
        default_vol = 50
        if sys.platform == "darwin":
            try:
                cmd = "osascript -e 'output volume of (get volume settings)'"
                res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                if res.isdigit(): return int(res)
            except Exception:
                return default_vol
        elif sys.platform == "win32":
            return default_vol
        elif sys.platform.startswith("linux"):
            try:
                res = subprocess.check_output("amixer sget Master", shell=True).decode('utf-8')
                if "[" in res:
                    return int(res.split("[")[1].split("%]")[0])
            except Exception:
                return default_vol
        return default_vol

    def get_all_mode_fallbacks(self) -> Dict[str, int]:
        """
        Public method to expose the active fallback lookup dictionary map.
        Resolves the AttributeError during startup configuration sync passes.
        """
        return self.DEFAULT_FILTER_FALLBACKS


    def set_volume(self, volume_float: float) -> bool:
        """Pipes slider metrics natively into macOS, Windows, or Linux sound systems."""
        vol_float = max(0.0, min(1.0, float(volume_float)))
        vol_percentage = int(vol_float * 100)

        if sys.platform == "darwin":
            try:
                subprocess.run(f"osascript -e 'set volume output volume {vol_percentage}'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                cmd = f'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; if ({vol_percentage} -eq 0) {{ [void]$wsh.SendKeys([char]173) }} else {{ [void]$wsh.SendKeys([char]174)*50; [void]$wsh.SendKeys([char]175)*{int(vol_percentage / 2)}) }}"'
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run(f"amixer -q sset Master {vol_percentage}%", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                try:
                    subprocess.run(f"pactl set-sink-volume @DEFAULT_SINK@ {vol_percentage}%", shell=True, check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception:
                    return False
        return False

    def mute(self) -> bool:
        """Forces hardware mixer speaker channels to an absolute muted state."""
        if sys.platform == "darwin":
            try:
                subprocess.run("osascript -e 'set volume with output muted'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                subprocess.run(
                    'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run("amixer -q sset Master mute", shell=True, check=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True
            except Exception:
                try:
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 1", shell=True, check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception:
                    return False
        return False

    def unmute(self, restore_volume: float = 0.5) -> bool:
        """Releases the hardware attenuation lock and re-establishes volume parameters."""
        if sys.platform == "darwin":
            try:
                subprocess.run("osascript -e 'set volume without output muted'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                subprocess.run(
                    'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run("amixer -q sset Master unmute", shell=True, check=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except Exception:
                try:
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ 0", shell=True, check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
        return self.set_volume(restore_volume)

    def set_mode_fallback_width(self, mode: str, fallback_hz: int) -> bool:
        clean_mode = mode.upper().strip()
        if not clean_mode or int(fallback_hz) <= 0: return False
        self.DEFAULT_FILTER_FALLBACKS[clean_mode] = int(fallback_hz)
        if clean_mode in ["CW_L", "CW_U"]: self.DEFAULT_FILTER_FALLBACKS["CW"] = int(fallback_hz)
        if self.is_connected:
            if clean_mode == self.current_mode or (clean_mode in ["CW_L", "CW_U"] and self.current_mode == "CW"):
                self.set_filter_width_hz(int(fallback_hz))
        return True

    def log_current_state(self, description: str = "Manual Log Entry") -> Dict[str, Union[str, int, float]]:
        hz_key = self.current_frequency
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mhz": hz_key / 1_000_000, "mode": self.current_mode, "filter_hz": self.current_filter_width,
            "description": description if description else "Manual Log Entry"
        }
        self.logged_signals[hz_key] = log_entry
        return log_entry

    def get_all_logs(self) -> Dict[int, Dict[str, Union[str, int, float]]]:
        return self.logged_signals

    def clear_logs(self):
        self.logged_signals.clear()

    def set_frequency_hz(self, hz: int) -> bool:
        if not self.is_connected: return False
        try:
            self.sock.sendall(f"F {int(hz)}\n".encode('ascii'))
            self.sock.recv(1024)
            return True
        except socket.error:
            self._handle_unexpected_disconnect()
            return False

    def set_mode(self, mode: str, passband_hz: int = 0) -> bool:
        if not self.is_connected: return False
        input_mode = mode.upper().strip()
        if input_mode in ["CW", "CW_L", "CW_U"]:
            target_lookup_mode, network_mode = "CW", "CW"
        else:
            target_lookup_mode, network_mode = input_mode, input_mode

        if passband_hz == 0:
            passband_hz = self.DEFAULT_FILTER_FALLBACKS.get(target_lookup_mode, 2400)
        self.current_mode, self.current_filter_width = target_lookup_mode, passband_hz
        try:
            self.sock.sendall(f"M {network_mode} {int(passband_hz)}\n".encode('ascii'))
            self.sock.recv(1024)
            return True
        except socket.error:
            self._handle_unexpected_disconnect()
            return False

    def set_filter_width_hz(self, passband_hz: int) -> bool:
        if not self.is_connected or self.current_mode == "UNKNOWN": return False
        target_width = max(50, passband_hz)
        target_mode = self.current_mode
        if "CW" in self.current_mode or self.current_mode == "USB":
            target_mode = "USB" if target_width > 500 else "CW"
        return self.set_mode(target_mode, target_width)

    def get_filter_width_hz(self) -> int:
        self._sync_mode_only()
        return self.current_filter_width

    def widen(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width + active_step)

    def narrow(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width - active_step)

    def start_memory_scan(self, delay_ms: int = 2500):
        if not self.is_connected or not self.scan_channels: return
        self.scan_delay_ms, self.scan_idx, self.is_scanning = delay_ms, 0, True
        self._tkinter_scan_tick()

    def stop_scan(self):
        self.is_scanning = False

    def _tkinter_scan_tick(self):
        if not self.is_scanning or not self.is_connected: return
        if self.scan_idx >= len(self.scan_channels): self.scan_idx = 0
        current_ch = self.scan_channels[self.scan_idx]
        self.set_frequency_hz(current_ch["freq_hz"])
        self.set_mode(current_ch["mode"], current_ch.get("filter_hz", 0))
        if self.on_scan_step: self.on_scan_step(current_ch)
        self.scan_idx = (self.scan_idx + 1) % len(self.scan_channels)
        self.root.after(self.scan_delay_ms, self._tkinter_scan_tick)

    def _sync_mode_only(self):
        if not self.is_connected or not self.is_running: return
        try:
            self.sock.sendall(b'm\n')
            mode_resp = self.sock.recv(1024).decode('utf-8').strip()
            clean_lines = mode_resp.replace('\r', '').replace('RPRT 0', '').strip().split('\n')
            if clean_lines and len(clean_lines) >= 1:
                raw_mode = clean_lines[0].strip().upper()
                is_compatible = "CW" in raw_mode or raw_mode in ["LSB", "USB"]
                mapped_mode = "CW" if "CW" in raw_mode else ("LSB" if raw_mode == "LSB" else "USB")
                if not is_compatible:
                    if self.on_incompatible_mode: self.on_incompatible_mode(raw_mode, mapped_mode)
                    self.set_mode(mapped_mode, passband_hz=0)
                    return
                if mapped_mode != self.current_mode:
                    self.current_mode = mapped_mode
                    self.current_filter_width = self.DEFAULT_FILTER_FALLBACKS.get(raw_mode, 2400)
                    if self.on_mode_change: self.on_mode_change(mapped_mode)
        except socket.error:
            self._handle_unexpected_disconnect()

    def _tkinter_tick_loop(self):
        if not self.is_connected or not self.is_running: return
        try:
            if not self.is_scanning:
                self.sock.sendall(b'f\n')
                freq_resp = self.sock.recv(1024).decode('utf-8').strip()
                clean_freq = freq_resp.replace('\r', '').replace('RPRT 0', '').strip()
                if clean_freq.isdigit() and int(clean_freq) != self.current_frequency:
                    self.current_frequency = int(clean_freq)
                    if self.on_frequency_change: self.on_frequency_change(self.current_frequency)

                self.sock.sendall(b'm\n')
                mode_resp = self.sock.recv(1024).decode('utf-8').strip()
                clean_lines = mode_resp.replace('\r', '').replace('RPRT 0', '').strip().split('\n')
                if clean_lines and len(clean_lines) >= 1:
                    raw_mode = clean_lines[0].strip().upper()
                    is_compatible = "CW" in raw_mode or raw_mode in ["LSB", "USB"]
                    mapped_mode = "CW" if "CW" in raw_mode else ("LSB" if raw_mode == "LSB" else "USB")
                    if not is_compatible:
                        if self.on_incompatible_mode: self.on_incompatible_mode(raw_mode, mapped_mode)
                        self.set_mode(mapped_mode, passband_hz=0)
                        self.root.after(200, self._tkinter_tick_loop)
                        return
                    if mapped_mode != self.current_mode:
                        self.current_mode = mapped_mode
                        if self.on_mode_change: self.on_mode_change(mapped_mode)
                if clean_lines and len(clean_lines) >= 2 and clean_lines[1].strip().isdigit():
                    width_val = int(clean_lines[1].strip())
                    if width_val != self.current_filter_width:
                        self.current_filter_width = width_val
                        if self.on_filter_change: self.on_filter_change(width_val)
        except socket.timeout:
            pass
        except socket.error:
            self._handle_unexpected_disconnect()
            return
        self.root.after(200, self._tkinter_tick_loop)
