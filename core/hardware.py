"""
Hardware interface for ESP32 and air quality gas sensor over Serial / USB.
Includes COM port auto-discovery, baud rate selection, and seamless fallback to synthetic mock data generator.
"""

import json
import math
import random
import time
from typing import Dict, List, Optional, Tuple

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class HardwareManager:
    """Manages physical ESP32 serial communication and simulated IoT data generation per tenant."""

    def __init__(self, baseline_ppm: float = 380.0):
        self.serial_conn: Optional["serial.Serial"] = None
        self.connected_port: Optional[str] = None
        self.baud_rate: int = 115200
        self.is_connected: bool = False
        self.last_error: Optional[str] = None
        
        # Simulation engine state
        self.sim_ppm_baseline: float = baseline_ppm
        self.sim_current_ppm: float = baseline_ppm
        self.sim_spike_active: bool = False
        self.sim_spike_target: float = 0.0
        self.sim_spike_steps_remaining: int = 0
        self.sim_cycle_count: int = random.randint(0, 100)

    @staticmethod
    def get_available_ports() -> List[Dict[str, str]]:
        """Scan system for active COM/Serial ports."""
        ports_list = []
        if not SERIAL_AVAILABLE:
            return ports_list

        try:
            detected = serial.tools.list_ports.comports()
            for p in detected:
                desc = p.description or "Serial Device"
                ports_list.append({
                    "device": p.device,
                    "description": f"{p.device} ({desc})",
                    "hwid": p.hwid or ""
                })
        except Exception:
            pass
        return ports_list

    def connect(self, port: str, baud_rate: int = 115200, timeout: float = 1.0) -> Tuple[bool, str]:
        """Connect to physical ESP32 device via USB Serial."""
        if not SERIAL_AVAILABLE:
            self.last_error = "PySerial is not installed."
            return False, self.last_error

        self.disconnect()

        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.1)
            self.connected_port = port
            self.baud_rate = baud_rate
            self.is_connected = True
            self.last_error = None
            return True, f"Successfully connected to {port} @ {baud_rate} baud."
        except Exception as e:
            self.serial_conn = None
            self.is_connected = False
            self.last_error = str(e)
            return False, f"Connection failed: {e}"

    def disconnect(self):
        """Safely close active serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.serial_conn = None
        self.connected_port = None
        self.is_connected = False

    def read_physical_sensor(self) -> Optional[Dict]:
        """
        Read and parse incoming line from physical ESP32.
        Supports JSON format: {"ppm": 412.5, "temp": 24.5}
        and raw string values: "412.5" or "PPM: 412.5"
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return None

        try:
            if self.serial_conn.in_waiting > 0:
                raw_line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if not raw_line:
                    return None

                # Attempt JSON parsing first
                if raw_line.startswith('{') and raw_line.endswith('}'):
                    try:
                        data = json.loads(raw_line)
                        ppm = float(data.get("ppm", data.get("PPM", 0.0)))
                        return {
                            "ppm": round(ppm, 2),
                            "raw": raw_line,
                            "source": f"Physical ESP32 ({self.connected_port})",
                            "temp": round(float(data.get("temp", 24.5)), 1),
                            "humidity": round(float(data.get("humidity", 51.0)), 1),
                            "timestamp": time.time()
                        }
                    except json.JSONDecodeError:
                        pass

                # Try key-value parsing: "PPM: 382.4" or "382.4"
                cleaned = raw_line.upper().replace("PPM:", "").replace("PPM=", "").strip()
                try:
                    ppm_val = float(cleaned)
                    return {
                        "ppm": round(ppm_val, 2),
                        "raw": raw_line,
                        "source": f"Physical ESP32 ({self.connected_port})",
                        "temp": 24.5,
                        "humidity": 51.0,
                        "timestamp": time.time()
                    }
                except ValueError:
                    return {
                        "ppm": None,
                        "raw": raw_line,
                        "source": f"Physical ESP32 ({self.connected_port})",
                        "timestamp": time.time()
                    }
        except Exception as e:
            self.last_error = f"Serial read error: {e}"
            self.disconnect()
            return None

        return None

    def trigger_high_emission_spike(self, spike_ppm: float = 580.0, steps: int = 8):
        """Simulate an industrial emission leak or high pollutant event exceeding safe limits."""
        self.sim_spike_active = True
        self.sim_spike_target = spike_ppm
        self.sim_spike_steps_remaining = steps

    def read_simulated_sensor(self) -> Dict:
        """
        Generates realistic synthetic air quality readings.
        Includes smooth Brownian walk around tenant baseline and handles emission spikes.
        """
        self.sim_cycle_count += 1

        if self.sim_spike_active and self.sim_spike_steps_remaining > 0:
            step_progress = 1.0 - (self.sim_spike_steps_remaining / 8.0)
            self.sim_current_ppm = self.sim_spike_target * (0.90 + 0.10 * math.sin(step_progress * math.pi)) + random.uniform(-10.0, 15.0)
            self.sim_spike_steps_remaining -= 1
            if self.sim_spike_steps_remaining <= 0:
                self.sim_spike_active = False
        else:
            # Natural drift back towards tenant baseline with stochastic noise
            drift = (self.sim_ppm_baseline - self.sim_current_ppm) * 0.14
            noise = random.uniform(-5.0, 5.5)
            wave = 8.0 * math.sin(self.sim_cycle_count * 0.25)
            self.sim_current_ppm = max(260.0, self.sim_current_ppm + drift + noise + (wave * 0.05))

        temp = round(23.5 + 1.8 * math.sin(self.sim_cycle_count * 0.08) + random.uniform(-0.2, 0.2), 1)
        humidity = round(52.0 + 3.5 * math.cos(self.sim_cycle_count * 0.08) + random.uniform(-0.5, 0.5), 1)

        return {
            "ppm": round(self.sim_current_ppm, 2),
            "raw": f'{{"ppm": {round(self.sim_current_ppm, 2)}, "temp": {temp}, "humidity": {humidity}, "sensor": "GAS-SIM-ORACLE"}}',
            "source": "Simulated Mock Stream",
            "temp": temp,
            "humidity": humidity,
            "timestamp": time.time()
        }

    def get_reading(self, use_hardware: bool) -> Dict:
        """
        Primary interface: Returns reading from physical device if connected & enabled,
        or seamlessly falls back to realistic simulation.
        """
        if use_hardware and self.is_connected:
            reading = self.read_physical_sensor()
            if reading and reading.get("ppm") is not None:
                return reading
        
        return self.read_simulated_sensor()
