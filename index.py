"""
Analytic-AI entry point.

Usage:
    python index.py app          # Streamlit UI (default)
    python index.py mcp          # MCP server (stdio)
"""

import subprocess
import sys


def run_app() -> int:
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", "app.py", *sys.argv[2:]]
    )


def run_mcp() -> int:
    return subprocess.call([sys.executable, "server.py", *sys.argv[2:]])


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "app"
    runners = {"app": run_app, "mcp": run_mcp}

    if command not in runners:
        print(f"Unknown command: {command}")
        print("Usage: python index.py [app|mcp]")
        return 1

    return runners[command]()


if __name__ == "__main__":
    raise SystemExit(main())
