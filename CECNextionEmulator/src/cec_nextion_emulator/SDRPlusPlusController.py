import socket
import json
import os
from datetime import datetime
from typing import List, Dict, Union


class SDRPlusPlusController:
    """
    An advanced object-oriented controller to interface with SDR++ using
    the Hamlib RigCTL network protocol wrapper driven natively by Tkinter's .after() loop.
    Part 1: Dynamic Short-Label Channel Manager, Logging Framework, and JSON Storage.
    """

    HAM_BANDS = {
        '80m': (3500000, 'LSB', 2700),
        '40m': (7074000, 'USB', 3000),
        '20m': (14200000, 'USB', 2400),
        '15m': (21074000, 'USB', 3000),
        '10m': (28400000, 'USB', 2400),
        '2m': (145000000, 'FM', 12500)
    }

    DEFAULT_FILTER_FALLBACKS = {
        'USB': 2400, 'LSB': 2400, 'CW': 500, 'CW_L': 500, 'CW_U': 500,
        'AM': 6000, 'NFM': 12500, 'FM': 12500, 'WFM': 180000
    }

    # Absolute JSON file path tracking location mapping profile
    JSON_FILE = "sdr_scan_channels.json"

    def __init__(self, root, host: str = '127.0.0.1', port: int = 4532):
        self.root = root
        self.host = host
        self.port = port
        self.sock = None
        self.is_connected = False

        # State tracking cache variables
        self.current_frequency = 0
        self.current_mode = "UNKNOWN"
        self.current_filter_width = 2400

        # MANAGED SHORT-LABEL SCAN LIST
        self.scan_channels: List[Dict[str, Union[int, str]]] = []
        self._load_channels_from_json()  # Load saved list immediately on startup []

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

    def connect(self) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.15)
            self.sock.connect((self.host, self.port))
            self.is_connected = True
            self._tkinter_tick_loop()
            return True
        except Exception:
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_scan()
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

    # =========================================================================
    #  JSON STORAGE DISK ROUTINES
    # =========================================================================
    def _load_channels_from_json(self):
        """Attempts to read and decode custom entries from local storage on startup []."""
        if os.path.exists(self.JSON_FILE):
            try:
                with open(self.JSON_FILE, 'r', encoding='utf-8') as f:
                    self.scan_channels = json.load(f)
                print(f"[✔ Storage] Successfully loaded {len(self.scan_channels)} channels from disk.")
            except Exception as e:
                print(f"[-] Storage Exception: Failed to decode channels backup -> {e}")
                self.scan_channels = []

    def _save_channels_to_json(self):
        """Saves current memory registry arrays directly out to a clean JSON file []."""
        try:
            with open(self.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.scan_channels, f, indent=4)
            print("[✔ Storage] Scan channels saved to disk database cleanly.")
        except Exception as e:
            print(f"[-] Storage Exception: Failed to write database backup -> {e}")

    # =========================================================================
    #  LABEL-BASED CHANNEL LIST MANAGEMENT METHODS
    # =========================================================================
    def add_channel(self, label: str, freq_hz: int, mode: str, filter_hz: int, name: str) -> bool:
        clean_label = label.strip().upper()
        if not clean_label: return False

        for ch in self.scan_channels:
            if ch["label"] == clean_label: return False

        new_channel = {
            "label": clean_label,
            "freq_hz": int(freq_hz),
            "mode": mode.upper().strip(),
            "filter_hz": int(filter_hz),
            "name": name.strip() if name else f"Station {clean_label}"
        }
        self.scan_channels.append(new_channel)
        self._save_channels_to_json()  # Commit changes to disk immediately []
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
            self._save_channels_to_json()  # Commit changes to disk immediately []
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

    def log_current_state(self, description: str = "Manual Log Entry") -> Dict[str, Union[str, int, float]]:
        hz_key = self.current_frequency
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mhz": hz_key / 1_000_000,
            "mode": self.current_mode,
            "filter_hz": self.current_filter_width,
            "description": description if description else "Manual Log Entry"
        }
        self.logged_signals[hz_key] = log_entry
        return log_entry

    def query_logs(self, freq_hz: int) -> Union[Dict[str, Union[str, int, float]], None]:
        return self.logged_signals.get(int(freq_hz), None)

    def clear_logs(self):
        self.logged_signals.clear()

    def get_all_logs(self) -> Dict[int, Dict[str, Union[str, int, float]]]:
        return self.logged_signals

    # =========================================================================
    #  Part 2: Core Tuning Commands, Memory Scanning, and Telemetry Loop Threads
    # =========================================================================

    def set_frequency_hz(self, hz: int) -> bool:
        if not self.is_connected: return False
        try:
            cmd = f"F {int(hz)}\n".encode('ascii')
            self.sock.sendall(cmd)
            self.sock.recv(1024)
            return True
        except socket.error:
            self._handle_unexpected_disconnect()
            return False

    def set_frequency_mhz(self, mhz: float) -> bool:
        return self.set_frequency_hz(int(mhz * 1_000_000))

    def set_mode(self, mode: str, passband_hz: int = 0) -> bool:
        if not self.is_connected: return False
        input_mode = mode.upper().strip()

        if input_mode in ["CW", "CW_L", "CW_U"]:
            self.current_mode = "CW"
        else:
            self.current_mode = input_mode

        if passband_hz == 0:
            passband_hz = self.DEFAULT_FILTER_FALLBACKS.get(input_mode, 2400)

        network_mode = "CW" if "CW" in input_mode else input_mode
        self.current_filter_width = passband_hz

        try:
            cmd = f"M {network_mode} {int(passband_hz)}\n".encode('ascii')
            self.sock.sendall(cmd)
            self.sock.recv(1024)
            return True
        except socket.error:
            self._handle_unexpected_disconnect()
            return False

    def set_filter_width_hz(self, passband_hz: int) -> bool:
        if not self.is_connected or self.current_mode == "UNKNOWN":
            return False

        target_width = max(50, passband_hz)
        target_mode = self.current_mode

        if "CW" in self.current_mode or self.current_mode == "USB":
            if target_width > 500:
                target_mode = "USB"
            else:
                target_mode = "CW"

        return self.set_mode(target_mode, target_width)

    def get_filter_width_hz(self) -> int:
        """Exposes the public method required by main_app.py to fix the AttributeError."""
        self._sync_mode_only()
        return self.current_filter_width

    def widen(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width + active_step)

    def narrow(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width - active_step)

    def change_band(self, band_name: str) -> bool:
        self.stop_scan()
        band = band_name.lower().strip()
        if band in self.HAM_BANDS:
            hz, mode, default_width = self.HAM_BANDS[band]
            self.set_frequency_hz(hz)
            self.set_mode(mode, default_width)
            return True
        return False

    def start_memory_scan(self, delay_ms: int = 2500):
        if not self.is_connected or not self.scan_channels: return
        self.scan_delay_ms = delay_ms
        self.scan_idx = 0
        self.is_scanning = True
        self._tkinter_scan_tick()

    def stop_scan(self):
        self.is_scanning = False

    def _tkinter_scan_tick(self):
        if not self.is_scanning or not self.is_connected: return
        if self.scan_idx >= len(self.scan_channels): self.scan_idx = 0
        if not self.scan_channels:
            self.is_scanning = False
            return

        current_ch = self.scan_channels[self.scan_idx]
        self.set_frequency_hz(current_ch["freq_hz"])
        self.set_mode(current_ch["mode"], current_ch.get("filter_hz", 0))
        if self.on_scan_step: self.on_scan_step(current_ch)

        self.scan_idx = (self.scan_idx + 1) % len(self.scan_channels)
        self.root.after(self.scan_delay_ms, self._tkinter_scan_tick)

    def _sync_mode_only(self):
        if not self.is_connected: return
        try:
            self.sock.sendall(b'm\n')
            mode_resp = self.sock.recv(1024).decode('utf-8').strip()
            clean_lines = mode_resp.replace('\r', '').replace('RPRT 0', '').strip().split('\n')

            if clean_lines and len(clean_lines) >= 1:
                first_line = clean_lines[0].strip().upper()
                if first_line and first_line != self.current_mode:
                    if not ("CW" in first_line and self.current_mode == "CW"):
                        self.current_mode = first_line
                        self.current_filter_width = self.DEFAULT_FILTER_FALLBACKS.get(first_line, 2400)
                        if self.on_mode_change: self.on_mode_change(first_line)
        except socket.error:
            self._handle_unexpected_disconnect()

    def _tkinter_tick_loop(self):
        if not self.is_connected: return
        try:
            if not self.is_scanning:
                self.sock.sendall(b'f\n')
                freq_resp = self.sock.recv(1024).decode('utf-8').strip()
                clean_freq = freq_resp.replace('\r', '').replace('RPRT 0', '').strip()
                if clean_freq.isdigit():
                    freq_val = int(clean_freq)
                    if freq_val != self.current_frequency:
                        self.current_frequency = freq_val
                        if self.on_frequency_change: self.on_frequency_change(freq_val)

                self.sock.sendall(b'm\n')
                mode_resp = self.sock.recv(1024).decode('utf-8').strip()
                clean_lines = mode_resp.replace('\r', '').replace('RPRT 0', '').strip().split('\n')

                if clean_lines and len(clean_lines) >= 1:
                    first_line = clean_lines[0].strip().upper()
                    if first_line and first_line != self.current_mode:
                        if not ("CW" in first_line and self.current_mode == "CW"):
                            self.current_mode = first_line
                            if self.on_mode_change: self.on_mode_change(first_line)

                if clean_lines and len(clean_lines) >= 2:
                    second_line = clean_lines[1].strip()
                    if second_line.isdigit():
                        width_val = int(second_line)
                        if width_val != self.current_filter_width:
                            self.current_filter_width = width_val
                            if self.on_filter_change: self.on_filter_change(width_val)

        except socket.timeout:
            pass
        except socket.error:
            self._handle_unexpected_disconnect()
            return

        self.root.after(200, self._tkinter_tick_loop)
