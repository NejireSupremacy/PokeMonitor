import socket

from src.memory import BRIDGE_HOST, BRIDGE_PORT


def recv_line(conn: socket.socket) -> str:
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = conn.recv(64)
        if not chunk:
            raise RuntimeError("Connection closed while reading line")
        buf += chunk

    return buf.decode("ascii").strip()


def send_bridge_command(command: str) -> str:
    with socket.create_connection((BRIDGE_HOST, BRIDGE_PORT), timeout=2) as conn:
        conn.sendall(f"{command}\n".encode("ascii"))
        response = recv_line(conn)

    if response.startswith("ERR "):
        raise RuntimeError(response)

    return response


def read32(address: int) -> int:
    response = send_bridge_command(f"read32 {address:#x}")
    return int(response, 16)


def read_bytes(address: int, length: int) -> bytes:
    response = send_bridge_command(f"readbytes {address:#x} {length}")
    return bytes.fromhex(response)
