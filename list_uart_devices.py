#!/usr/bin/env python3
"""
List all currently connected UART/Serial devices.
"""

from uart_mac_reader_pkg.uart_util import list_uart_ports_detailed, format_port_info, get_platform


def list_uart_devices():
    """List all available UART/serial ports with detailed information."""
    ports = list_uart_ports_detailed()

    if not ports:
        print("No UART devices found.")
        return

    # Show platform information
    plat = get_platform()
    print(f"Platform: {plat}")
    print(f"Found {len(ports)} UART device(s):\n")

    for i, port in enumerate(ports, 1):
        print(f"Device {i}:{format_port_info(port)}")


if __name__ == '__main__':
    list_uart_devices()
