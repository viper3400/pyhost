import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PyHost ASGI plugin host")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--forwarded-allow-ips",
        default=os.getenv("PYHOST_FORWARDED_ALLOW_IPS", "127.0.0.1"),
        help=(
            "Comma-separated proxy IPs/networks allowed to set forwarded headers "
            "(default: PYHOST_FORWARDED_ALLOW_IPS or 127.0.0.1)"
        ),
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Load environment variables from this file (default: .env)",
    )
    args = parser.parse_args()
    uvicorn.run(
        "tool_host.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        env_file=args.env_file,
        forwarded_allow_ips=args.forwarded_allow_ips,
    )
