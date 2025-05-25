#!/usr/bin/env python3
"""
Script to register an agent event with the CIRISNode server using a JWT token.
Usage: python3 register_agent_event.py <JWT_TOKEN> [API_URL]
- JWT_TOKEN: The agent JWT token (required)
- API_URL: The base URL of the CIRISNode API (default: http://localhost:8000)
"""
import sys
import requests
import json

if len(sys.argv) < 2:
    print("Usage: python3 register_agent_event.py <JWT_TOKEN> [API_URL]", file=sys.stderr)
    sys.exit(1)

JWT_TOKEN = sys.argv[1]
API_URL = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"

# event must be a dict, not a string
payload = {
    "agent_uid": "happy",  # required
    "event": {
        "event_type": "agent_registered",
        "agent_id": "happy",
        "timestamp": "2025-05-24T12:00:00Z",
        "details": {"info": "Agent registered via script."}
    }
}

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

resp = requests.post(f"{API_URL}/api/v1/agent/events", headers=headers, json=payload)

print(f"Status: {resp.status_code}")
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print(resp.text)
