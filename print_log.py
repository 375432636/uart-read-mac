#!/usr/bin/env python3
"""
Simple UART Log Printer

Monitors USB UART connections and prints logs.
"""

import sys
import time
import serial
from uart_util import UARTBase


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

    def read_logs(self):
        """Read and print logs from the UART connection."""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("[✗] No active connection")
            return

        print("\n[*] Reading logs (Ctrl+C to stop)...\n")

        try:
            while True:
                if self.serial_conn.in_waiting > 0:
                    try:
                        # Read a line
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        print(line)
                    except UnicodeDecodeError:
                        # Skip lines that can't be decoded
                        pass
                else:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n[*] Stopping log reader...")
        except (serial.SerialException, OSError):
            print("\n[*] Device disconnected")
            raise  # Re-raise to let the run() method handle it

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
                    self.read_logs()
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
