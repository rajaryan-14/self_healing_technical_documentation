"""Tiny demo service used to exercise the documentation checker."""


def start_server(host: str = "127.0.0.1", port: int = 8000) -> str:
    """Return the address where the demo server would listen."""
    return f"http://{host}:{port}"

