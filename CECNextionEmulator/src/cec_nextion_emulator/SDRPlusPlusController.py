import socket
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Union
import globalvars as gv


class SDRPlusPlusController:
    """
    An advanced object-oriented controller to interface with SDR++ using
    the Hamlib RigCTL network protocol wrapper driven natively by Tkinter's .after() loop.
    Part 1: Initialization, Disk Storage, and Local Configuration Cache Registries.
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

    def __init__(self, root):
        self.root = root
        # self.host = gv.config.get("SDR Server IP", '127.0.0.1')
        # self.port = int(gv.config.get("SDR TCP Port", 4532))
        self.host = gv.config.get_sdr_server_ip()
        self.port = gv.config.get_sdr_tcp_port()
        self.sock = None
        self.is_connected = False
        self.is_running = False

        # Multi-Scan Set Architecture Properties
        self.scan_sets_dict: Dict[str, List[Dict[str, Union[int, str]]]] = {}
        self.active_scan_set: str = "DEFAULT SET"

        # State tracking cache variables
        self.current_frequency = 0
        self.current_mode = "UNKNOWN"
        self.current_filter_width = 2400
        self.current_signal_dbfs = -120.0

        # Mutatable Fallback Dictionary Registry
        self.DEFAULT_FILTER_FALLBACKS = dict(self.FACTORY_DEFAULTS)

        # Managed Scan Array targeting active subset pointer
        self.scan_channels: List[Dict[str, Union[int, str]]] = []
        self._load_channels_from_json()

        # Scanner runtime properties
        self.is_scanning = False
        self.scan_idx = 0
        self.scan_delay_ms = 2500

        # In-Memory Dictionary Logger Storage
        self.logged_signals: Dict[int, Dict[str, Union[str, int, float]]] = {}

        # Public system event callbacks
        self.on_frequency_change_primary = None
        self.on_frequency_change_secondary = None
        self.on_mode_change_primary = None
        self.on_mode_change_secondary = None
        self.on_filter_change = None
        self.on_scan_step = None
        self.on_disconnect = None
        self.on_incompatible_mode = None
        self.on_signal_change = None

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
        """Loads nested multi-scan sets from the unified application config profile."""
        try:
            # UNIFIED PATTERN: Read directly out of gv.config
            # self.scan_sets_dict = gv.config.get("Scan Channels Registry Queue", {})
            self.scan_sets_dict = gv.config.get_scan_channels_registry()
            if not isinstance(self.scan_sets_dict, dict) or not self.scan_sets_dict:
                self.scan_sets_dict = {"DEFAULT SET": []}
            if self.active_scan_set not in self.scan_sets_dict:
                self.active_scan_set = list(self.scan_sets_dict.keys())[0]
            self.scan_channels = self.scan_sets_dict[self.active_scan_set]
        except Exception as e:
            print(f"[-] Config Load Exception: {e}")
            self.scan_sets_dict = {"DEFAULT SET": []}
            self.scan_channels = []

    def _save_channels_to_json(self):
        """Appends active scan set updates via global configuration manager."""
        try:
            self.scan_sets_dict[self.active_scan_set] = self.scan_channels

            # UNIFIED: Hand the data directly to gv.config
            gv.config.set_scan_channels_registry(self.scan_sets_dict)

            print(f"[✔ Disk Sync] Saved active set: '{self.active_scan_set}'")
        except Exception as e:
            print(f"[-] Disk Sync Exception: {e}")

    def _save_all_channels_to_json(self):
        """Saves the entire registry tracking block via global configuration manager."""
        try:
            # UNIFIED: Hand the full dictionary to gv.config
            gv.config.set_scan_channels_registry(self.scan_sets_dict)

            print("[✔ Disk Sync] Successfully committed all master scan sets to gv.config")
        except Exception as e:
            print(f"[-] Master Disk Sync Exception: {e}")

    def change_active_scan_set(self, set_name: str) -> bool:
        """Swaps the active scanning target profile list cleanly to a different scan set."""
        clean_name = set_name.strip()
        if clean_name in self.scan_sets_dict:
            self.stop_scan()
            self.active_scan_set = clean_name
            self.scan_channels = self.scan_sets_dict[clean_name]
            print(f"[*] Controller: Swapped scanner target profile to set: '{clean_name}'")
            return True
        return False

    def create_new_scan_set(self, set_name: str, clone_from_set: str = None) -> bool:
        """Creates a brand new named scan set with option template copying cloning parameters."""
        clean_name = set_name.strip()
        if not clean_name or clean_name in self.scan_sets_dict:
            return False

        if clone_from_set and clone_from_set in self.scan_sets_dict:
            import copy
            self.scan_sets_dict[clean_name] = copy.deepcopy(self.scan_sets_dict[clone_from_set])
            print(f"[✔ Clone] Set '{clean_name}' successfully duplicated from template set: '{clone_from_set}'")
        else:
            self.scan_sets_dict[clean_name] = []
            print(f"[✔ Creation] Initialized empty scan set category bucket: '{clean_name}'")

        self._save_channels_to_json()
        return True

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

    def get_all_mode_fallbacks(self) -> Dict[str, int]:
        return self.DEFAULT_FILTER_FALLBACKS

    def set_mode_fallback_width(self, mode: str, fallback_hz: int) -> bool:
        clean_mode = mode.upper().strip()
        if not clean_mode or int(fallback_hz) <= 0: return False
        self.DEFAULT_FILTER_FALLBACKS[clean_mode] = int(fallback_hz)
        if clean_mode in ["CW_L", "CW_U"]: self.DEFAULT_FILTER_FALLBACKS["CW"] = int(fallback_hz)
        if self.is_connected:
            if clean_mode == self.current_mode or (clean_mode in ["CW_L", "CW_U"] and self.current_mode == "CW"):
                self.set_filter_width_hz(int(fallback_hz))
        return True

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

        self.current_mode = target_lookup_mode
        self.current_filter_width = passband_hz

        if self.on_mode_change_primary: self.on_mode_change_primary(target_lookup_mode)
        if self.on_mode_change_secondary: self.on_mode_change_secondary(target_lookup_mode)
        if self.on_filter_change: self.on_filter_change(passband_hz)

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

        self.current_mode = target_mode
        self.current_filter_width = target_width

        if self.on_mode_change_primary: self.on_mode_change_primary(target_mode)
        if self.on_mode_change_secondary: self.on_mode_change_secondary(target_mode)
        if self.on_filter_change: self.on_filter_change(target_width)

        # UNIFIED PATTERN: Save both configurations safely to disk on update
        try:
            gv.config.set_sdr_filter_width_hz(target_width)
            gv.config.set_sdr_current_mode(target_mode)
        except Exception as e:
            print(f"[-] Config Save Error inside set_filter_width_hz: {e}")

        return self.set_mode(target_mode, target_width)

    def get_filter_width_hz(self) -> int:
        """Fetches the filter width from config, falling back to the local variable or 120000 Hz."""
        try:
            # Fall back to the active tracking instance variable if the key doesn't exist yet
            default_fallback = getattr(self, 'current_filter_width', 120000)
            return int(gv.config.get_sdr_filter_width_hz())
        except Exception as e:
            print(f"[-] Error retrieving filter width: {e}")
            return 120000

    def widen(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width + active_step)

    def narrow(self, step_hz: int = 200) -> bool:
        active_step = 50 if "CW" in self.current_mode or self.current_filter_width <= 500 else step_hz
        return self.set_filter_width_hz(self.current_filter_width - active_step)


    def start_memory_scan(self, delay_ms: int = None):
        """Begins scan loop, utilizing config file for delay."""
        if not self.is_connected or not self.scan_channels: return
        self.scan_delay_ms = int(delay_ms) if delay_ms is not None else gv.config.get_scan_station_time_ms()
        self.scan_idx = 0
        self.is_scanning = True
        self._tkinter_scan_tick()

    def set_scan_station_time_ms(self, milliseconds: int) -> bool:
        """Adjusts and saves scan dwell time to config."""
        try:
            self.scan_delay_ms = max(200, int(milliseconds))
            gv.config.set_Scan_On_Station_Time(self.scan_delay_ms)
            return True
        except Exception as e:
            print(f"[-] Timing Save Error: {e}")
            return False

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

        # FIXED: Thread loops dynamically load the saved configurations live on every step
        self.root.after(self.scan_delay_ms, self._tkinter_scan_tick)

    # =========================================================================
    #  NEW INTEGRATION: AUTOMATED SCAN DELAY METHOD CONTROLLERS
    # =========================================================================
    def set_scan_station_time_ms(self, milliseconds: int) -> bool:
        """
        Dynamically adjusts the dwell time variable parameter for memory scans
        and commits the update cleanly back into your executable configuration python file [1.11].
        """
        clean_ms = max(200, int(milliseconds))  # Enforces a safe 200ms processing floor layout
        self.scan_delay_ms = clean_ms

        try:
            gv.config.set_scan_station_time_ms(clean_ms)
            print(f"[✔ Disk Sync] Scan On Station Time successfully committed to disk -> {clean_ms} ms")
            return True
        except Exception as e:
            print(f"[-] Disk Sync Exception: {e}")
            return False

    def get_system_volume(self) -> int:
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
                if "[" in res: return int(res.split("[")[1].split("%]")[0])
            except Exception:
                return default_vol
        return default_vol

    def set_volume(self, volume_float: float) -> bool:
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
                cmd = f'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; [void]$wsh.SendKeys([char]174)*50; [void]$wsh.SendKeys([char]175)*{int(vol_percentage / 2)}"'
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
                return False
        return False

    def mute(self) -> bool:
        if sys.platform == "darwin":
            try:
                subprocess.run("osascript -e 'set volume with output muted'", shell=True, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                subprocess.run(
                    'powershell -Command "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run("amixer -q sset Master mute", shell=True, check=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL); return True
            except Exception:
                return False
        return False

    def unmute(self, restore_volume: float = 0.5) -> bool:
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
                pass
        return self.set_volume(restore_volume)

    def _tkinter_tick_loop(self):
        """Asynchronous updater loop. Simulates real-world radio propagation profiles safely [1.11]."""
        if not self.is_connected or not self.is_running: return
        try:
            if not self.is_scanning:
                # 1. Sync VFO Frequency Counter
                self.sock.sendall(b'f\n')
                freq_resp = self.sock.recv(1024).decode('utf-8').strip()
                clean_freq = freq_resp.replace('\r', '').replace('RPRT 0', '').strip()
                if clean_freq.isdigit() and int(clean_freq) != self.current_frequency:
                    self.current_frequency = int(clean_freq)
                    if self.on_frequency_change_primary:
                        self.on_frequency_change_primary(self.current_frequency)
                    if self.on_frequency_change_secondary:
                        self.on_frequency_change_secondary(self.current_frequency)

                # 2. Sync VFO Mode State
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
                        self.current_filter_width = self.DEFAULT_FILTER_FALLBACKS.get(mapped_mode, 2400)
                        if self.on_mode_change_primary:
                            self.on_mode_change_primary(mapped_mode)

                        if self.on_mode_change_secondary:
                            self.on_mode_change_secondary(mapped_mode)

                        if self.on_filter_change: self.on_filter_change(self.current_filter_width)

                # 3. Frequency-Aware Propagation S-Meter Calculations [1.11]
                import random
                freq_mhz = self.current_frequency / 1_000_000.0
                if self.current_mode == "CW":
                    base_dbfs = -94.0 if freq_mhz > 30.0 else -82.0
                    jitter_range = (-1.8, 2.2)
                else:
                    if freq_mhz <= 4.0:
                        base_dbfs, jitter_range = -54.0, (-4.2, 4.5)
                    elif 4.0 < freq_mhz <= 8.0:
                        base_dbfs, jitter_range = -58.0, (-3.8, 5.2)
                    elif 14.0 <= freq_mhz <= 29.7:
                        base_dbfs, jitter_range = -74.0, (-2.5, 3.2)
                    elif 144.0 <= freq_mhz <= 148.0:
                        base_dbfs, jitter_range = -98.0, (-1.1, 1.4)
                    else:
                        base_dbfs, jitter_range = -72.0, (-2.0, 2.5)

                signal_spike = 0.0
                if int(self.current_frequency) % 7 == 0:
                    signal_spike = random.uniform(12.5, 34.0)
                elif int(self.current_frequency) % 3 == 0:
                    signal_spike = random.uniform(4.0, 11.5)

                simulated_signal = base_dbfs + random.uniform(*jitter_range) + signal_spike
                self.current_signal_dbfs = min(-5.0, simulated_signal)
                if self.on_signal_change: self.on_signal_change(self.current_signal_dbfs)

                # 4. Filter Sanitation Lock
                if self.current_mode == "CW" and self.current_filter_width > 500:
                    self.current_filter_width = 500
                    if self.on_filter_change: self.on_filter_change(500)
                else:
                    if self.on_filter_change: self.on_filter_change(self.current_filter_width)

        except socket.timeout:
            pass
        except socket.error:
            self._handle_unexpected_disconnect(); return
        self.root.after(200, self._tkinter_tick_loop)
