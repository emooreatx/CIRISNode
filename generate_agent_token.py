#!/usr/bin/env python3
"""
Script to generate a valid agent JWT token using the server's JWT_SECRET and print it to stdout.
Run this on the server where the backend is deployed.
"""
import os
import sys
import jwt
import datetime

# Load secret from environment or fallback to config
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    # Try to load from cirisnode/config.py
    try:
        from cirisnode import config
        JWT_SECRET = getattr(config, "settings", None)
        if JWT_SECRET:
            JWT_SECRET = JWT_SECRET.JWT_SECRET
    except Exception:
        pass
if not JWT_SECRET:
    print("Error: JWT_SECRET not found in environment or cirisnode/config.py", file=sys.stderr)
    sys.exit(1)

# Agent identity (customize as needed)
sub = sys.argv[1] if len(sys.argv) > 1 else "test-agent"
role = sys.argv[2] if len(sys.argv) > 2 else "agent"

now = datetime.datetime.now(datetime.timezone.utc)
payload = {
    "sub": sub,
    "role": role,
    "iat": int(now.timestamp()),
    "exp": int((now + datetime.timedelta(days=7)).timestamp()),
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(token)
