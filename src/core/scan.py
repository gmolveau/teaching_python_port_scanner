import socket

# NOTE: listen on port 1337 with netcat: nc -l 1337


def get_ssh_banner(host: str, port: int = 22, timeout: float = 2.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            banner = s.recv(1024).decode().strip()
            return banner if banner else None
    except (TimeoutError, ConnectionRefusedError, UnicodeDecodeError):
        return None


def get_http_server(host: str, port: int = 80, timeout: float = 2.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            # Send a minimal HTTP HEAD request
            s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
            response = s.recv(4096).decode()
            # Look for the 'Server:' header in the response
            for line in response.split("\r\n"):
                if line.lower().startswith("server:"):
                    return line.split(":", 1)[1].strip()
            return None
    except (TimeoutError, ConnectionRefusedError, UnicodeDecodeError):
        return None


def scan(ip_target, port_target):
    if port_target == 22:
        # test with 172.65.251.78:22
        data = get_ssh_banner(ip_target, port_target, 3.0)
        if data:
            print(data)
            return data

    if port_target in (80, 443, 8080):
        # example with 104.21.5.178:80
        data = get_http_server(ip_target, port_target, 3.0)
        if data:
            print(data)
            return data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(3)
            s.connect((ip_target, port_target))
            print("OK")
            return "OK"
        except (TimeoutError, ConnectionRefusedError) as e:
            print(e)
