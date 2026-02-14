#!/usr/bin/env python3
"""
Cross-platform UART/Serial utilities.

Common utilities for working with UART/serial ports on Windows, macOS, and Linux.
"""

import sys
import time
import platform
import serial
import serial.tools.list_ports
from serial.tools import list_ports


def get_platform():
    """
    Get the current platform.

    Returns:
        'windows', 'darwin', or 'linux'
    """
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'


def get_uart_port_prefixes():
    """
    Get common UART port prefixes for the current platform.

    Returns:
        List of port prefixes (e.g., ['COM'] for Windows, ['/dev/tty'] for Unix)
    """
    plat = get_platform()
    if plat == 'windows':
        return ['COM']
    elif plat in ('darwin', 'linux'):
        return ['/dev/tty', '/dev/cu']
    return []


def format_port_info(port):
    """
    Format port information as a string.

    Args:
        port: serial.tools.list_ports.ListPortInfo object

    Returns:
        Formatted string with port information
    """
    info = [
        f"Port:       {port.device}",
        f"Name:       {port.name}",
    ]

    if port.description:
        info.append(f"Description: {port.description}")
    if port.manufacturer:
        info.append(f"Maker:      {port.manufacturer}")
    if port.product:
        info.append(f"Product:    {port.product}")
    if port.serial_number:
        info.append(f"Serial:     {port.serial_number}")
    if port.vid:
        info.append(f"Vendor ID:  {port.vid:04X}")
    if port.pid:
        info.append(f"Product ID: {port.pid:04X}")

    return '\n  '.join([''] + info)  # Add leading newline and indent


def list_uart_ports():
    """
    List all available UART/serial ports.

    Returns:
        List of port device paths
    """
    ports = list_ports.comports()
    return [port.device for port in ports]


def list_uart_ports_detailed():
    """
    List all available UART/serial ports with detailed information.

    Returns:
        List of serial.tools.list_ports.ListPortInfo objects
    """
    return list_ports.comports()


class UARTBase:
    """Base class for UART operations with cross-platform support."""

    def __init__(self, baudrate=115200, timeout=1):
        """
        Initialize the UART base class.

        Args:
            baudrate: Serial baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1)
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.known_ports = set()

    def list_uart_ports(self):
        """List all available UART/serial ports."""
        return list_uart_ports()

    def wait_for_connection(self, check_interval=1):
        """
        Wait for a new USB UART device to be connected.

        Args:
            check_interval: Seconds between checks (default: 1)

        Returns:
            The device path of the newly connected port, or None if interrupted
        """
        print("Waiting for USB UART connection...")
        print("Press Ctrl+C to exit")

        # Get initial list of ports
        self.known_ports = set(self.list_uart_ports())

        try:
            while True:
                current_ports = set(self.list_uart_ports())
                new_ports = current_ports - self.known_ports

                if new_ports:
                    # Return the first new port found
                    new_port = list(new_ports)[0]
                    print(f"\n[*] Device connected: {new_port}")
                    self.known_ports = current_ports
                    return new_port

                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            sys.exit(0)

    def connect(self, port=None):
        """
        Connect to a UART port.

        Args:
            port: Device path (if None, waits for connection)

        Returns:
            True if connected successfully, False otherwise
        """
        if port is None:
            port = self.wait_for_connection()

        try:
            print(f"[*] Connecting to {port} at {self.baudrate} baud...")
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            print(f"[✓] Connected successfully!")
            return True
        except serial.SerialException as e:
            print(f"[✗] Failed to connect: {e}")
            return False

    def close(self):
        """Close the serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("[*] Connection closed")
