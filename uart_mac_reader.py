#!/usr/bin/env python3
"""
USB UART MAC Address Reader

Monitors USB UART connections, reads logs, and extracts MAC addresses.
"""

import re
import sys
import time
import serial
from uart_util import UARTBase


class MACReader(UARTBase):
    """Monitor UART and extract MAC addresses from logs."""

    # MAC address pattern for wifi:mode format
    MAC_PATTERN = r'wifi:mode\s*:\s*sta\s*\(\s*([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\s*\)'

    def __init__(self, baudrate=115200, timeout=1):
        """
        Initialize the MAC reader.

        Args:
            baudrate: Serial baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1)
        """
        super().__init__(baudrate, timeout)

    def parse_mac(self, line):
        """
        Extract MAC address from a log line.

        Args:
            line: Log line to parse

        Returns:
            MAC address found in wifi:mode format, or None
        """
        match = re.search(self.MAC_PATTERN, line)
        if match:
            return match.group(1).upper()
        return None

    def read_logs(self):
        """
        Read and print logs from the UART connection.

        Extracts and displays MAC addresses when found.
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("[✗] No active connection")
            return

        print("[*] Monitoring for MAC addresses (Ctrl+C to stop)...")

        buffer = ""

        try:
            while True:
                try:
                    # Read available data
                    if self.serial_conn.in_waiting > 0:
                        data = self.serial_conn.read(self.serial_conn.in_waiting)
                        buffer += data.decode('utf-8', errors='ignore')

                    # Process complete lines
                    while '\n' in buffer or '\r' in buffer:
                        # Split by newline or carriage return
                        if '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        else:
                            line, buffer = buffer.split('\r', 1)

                        line = line.strip()

                        if line:
                            # Skip lines containing "Found AP"
                            if "Found AP" in line:
                                continue

                            # Extract and print MAC address with the log line
                            mac = self.parse_mac(line)
                            if mac:
                                print(f"\n[!] MAC ADDRESS FOUND: {mac}")
                                print(f"    Log: {line}\n")

                    time.sleep(0.01)

                except (serial.SerialException, OSError):
                    print("\n[*] Device disconnected")
                    raise

        except KeyboardInterrupt:
            print("\n[*] Stopping log reader...")

    def run(self, port=None, continuous=True):
        """
        Main run loop.

        Args:
            port: Device path (if None, waits for connection)
            continuous: If True, reconnects on disconnect (default: True)
        """
        try:
            while True:
                if self.connect(port):
                    try:
                        self.read_logs()
                    except (serial.SerialException, OSError):
                        # Device disconnected, continue to reconnect
                        pass
                    finally:
                        self.close()

                if not continuous:
                    break

                print("[*] Waiting for reconnection...")
                port = None  # Wait for new connection

        except KeyboardInterrupt:
            print("\n[*] Exiting...")
        finally:
            self.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor USB UART and extract MAC addresses from logs'
    )
    parser.add_argument(
        '-p', '--port',
        help='Serial port device (e.g., /dev/ttyUSB0, COM3). If not specified, waits for connection.'
    )
    parser.add_argument(
        '-b', '--baudrate',
        type=int,
        default=115200,
        help='Serial baud rate (default: 115200)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (do not reconnect on disconnect)'
    )

    args = parser.parse_args()

    # Create and run the reader
    reader = MACReader(baudrate=args.baudrate)
    reader.run(port=args.port, continuous=not args.once)


if __name__ == '__main__':
    main()
