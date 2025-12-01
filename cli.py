import argparse
import ipaddress

from scan import scan


def valid_ipv4_address(value):
    try:
        ipaddress.IPv4Address(value)
        return value
    except ipaddress.AddressValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid IPv4 address.")


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer.")

    if not (0 <= port <= 65535):
        raise argparse.ArgumentTypeError(
            f"{port} is not a valid port number (0-65535)."
        )
    return port


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--ip", type=valid_ipv4_address, help="the target ip v4 address"
)
parser.add_argument(
    "-p", "--port", nargs="+", type=valid_port, help="the target port (0-65535)"
)
args = parser.parse_args()

print(f"port = {args.port}, ip = {args.ip}")
for port in args.port:
    scan(args.ip, port)
