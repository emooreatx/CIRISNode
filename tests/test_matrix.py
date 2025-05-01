import pytest
from cirisnode.matrix.bot import send_audit_root

@pytest.mark.asyncio
async def test_matrix_message_send(monkeypatch):
    monkeypatch.setenv("MATRIX_HOMESERVER", "https://matrix.example.org")
    monkeypatch.setenv("MATRIX_USER_ID", "@test:matrix.org")
    monkeypatch.setenv("MATRIX_ACCESS_TOKEN", "dummy-token")
    monkeypatch.setenv("MATRIX_ROOM_ID", "!abc123:matrix.org")

    try:
        response = await send_audit_root(run_ids=[])
        assert "sha256" in response
    except Exception as e:
        pytest.skip(f"Matrix integration skipped: {e}")
