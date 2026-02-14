#!/usr/bin/env python3
"""
Simple UART Log Printer

Monitors USB UART connections and prints logs.
"""

import sys
import time
import os
import serial
from datetime import datetime
from uart_util import UARTBase


# Static directory for log files
STATIC_DIR = "static"


class UARTLogPrinter(UARTBase):
    """Monitor UART and print logs."""

    def __init__(self, baudrate=115200, timeout=1):
        """
        Initialize the log printer.

        Args:
            baudrate: Serial baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1)
        """
        super().__init__(baudrate, timeout)
        self.log_file = None

    def start_session(self):
        """Start a new logging session with a new log file."""
        # Create static directory if it doesn't exist
        if not os.path.exists(STATIC_DIR):
            os.makedirs(STATIC_DIR)

        # Generate filename with timestamp: %Y%m%d-%H%M%S.log
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(STATIC_DIR, f"{timestamp}.log")

        # Open log file for writing
        self.log_file = open(filename, 'w', encoding='utf-8')
        self.log_file.write(f"Session started: {datetime.now().isoformat()}\n")
        self.log_file.write(f"{'=' * 60}\n")
        self.log_file.flush()
        print(f"[*] Logging to: {filename}")

    def end_session(self):
        """End the current logging session and close the log file."""
        if self.log_file:
            self.log_file.write(f"{'=' * 60}\n")
            self.log_file.write(f"Session ended: {datetime.now().isoformat()}\n")
            self.log_file.close()
            self.log_file = None

    def read_logs(self):
        """Read and print logs from the UART connection."""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("[✗] No active connection")
            return

        print("\n[*] Reading logs (Ctrl+C to stop)...\n")

        try:
            while True:
                try:
                    if self.serial_conn.in_waiting > 0:
                        try:
                            # Read a line
                            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                            if line:  # Only process non-empty lines
                                # Print to console (original line)
                                print(line)
                                # Write to log file with timestamp
                                if self.log_file:
                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Milliseconds
                                    log_line = f"[{timestamp}] {line}"
                                    self.log_file.write(log_line + '\n')
                                    self.log_file.flush()
                        except UnicodeDecodeError:
                            # Skip lines that can't be decoded
                            pass
                    else:
                        time.sleep(0.01)
                except (serial.SerialException, OSError):
                    # Device disconnected during operation
                    print("\n[*] Device disconnected")
                    return  # Return normally to let run() handle reconnection

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
                    # Start a new session for this connection
                    self.start_session()
                    try:
                        self.read_logs()
                    finally:
                        # End session when connection closes
                        self.end_session()
                        self.close()

                if not continuous:
                    break

                print("[*] Waiting for reconnection...")
                port = None  # Wait for new connection

        except KeyboardInterrupt:
            print("\n[*] Exiting...")
        finally:
            self.close()
            self.end_session()  # Ensure log file is closed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor USB UART and print logs'
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

    # Create and run the printer
    printer = UARTLogPrinter(baudrate=args.baudrate)
    printer.run(port=args.port, continuous=not args.once)


if __name__ == '__main__':
    main()
