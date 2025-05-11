### Veilid side‑car integration — contributor task brief

You’re wiring every Agent, Node, and WA process to talk over a local Veilid server instead of raw HTTP.
All message schemas stay the same; only transport changes.

---

#### 1. Local setup

* `brew install veilid` (mac) / `curl -sL https://veilid.net/install.sh | sudo bash` (Linux).
* Run once: `veilid-server --bootstrap /dnsaddr/bootstrap.veilid.net`

  * Confirms `~/.veilid/keys/node.key` (ed25519) created.
* Clone repo, create a `.env` file:

  ```
  VEILID_API=ws://127.0.0.1:5959
  ```

---

#### 2. Add Veilid wrapper

Create `cirisnode/transport/veilid_peer.py`

```python
from veilid import Peer
import json, os, asyncio

API = os.getenv("VEILID_API", "ws://127.0.0.1:5959")

class VeilidPeer:
    def __init__(self, key_path):
        self.peer = Peer(url=API, key_path=key_path)

    async def start(self):
        await self.peer.start()

    async def publish(self, topic, data):
        await self.peer.publish(topic, json.dumps(data).encode())

    async def subscribe(self, topic, handler):
        await self.peer.subscribe(topic, lambda raw, *_: asyncio.create_task(
            handler(json.loads(raw))))
```

---

#### 3. Replace HTTP calls

Search for `httpx.AsyncClient` or `requests`:

```bash
rg -n "(httpx|requests).*post" src/
```

For each:

```python
# BEFORE
await client.post("http://localhost:8010/api/v1/wa/run", json=thought)

# AFTER
await vp.publish("wa.deferral", thought)
```

Add `vp = VeilidPeer("keys/agent.key"); await vp.start()` at the top of each service.

---

#### 4. Listeners

Example for Node:

```python
vp = VeilidPeer("keys/node.key")
await vp.start()

@vp.subscribe("node.cmd")
async def handle_cmd(thought):
    result = run_pdma(thought)          # existing fn
    await vp.publish("agent.reply", result)
```

Do parallel handlers for `control.abort` (kill‑switch) and `wa.ruling`.

---

#### 5. Docker / Compose

Add a side‑car service:

```yaml
veilid:
  image: ghcr.io/veilid/veilid:latest
  command: veilid-server --listen 0.0.0.0:5150
  volumes: [veilid-data:/data]
  expose: ["5150","5959"]
```

Set `VEILID_API=ws://veilid:5959` in the main container.

---

#### 6. Health & tests

* Extend `GET /health` to ping `ws://127.0.0.1:5959/status`.
* `pytest tests/test_transport.py`

  * publish dummy message ➜ expect echo handler fired.
* Run `scripts/test_abort_latency.py` and verify safe‑state ≤ 200 ms.

---

#### 7. Key rotation

Document (`docs/ops/veilid.md`):

```
veilid-server rotate            # generates new key
publish_new_pubkey.sh           # pushes to OriginTrail
```

---

#### 8. Done criteria

* All `agent ↔ node`, `node ↔ node`, and `agent/node ↔ WA` calls use Veilid.
* Kill‑switch frame reaches agent and triggers safe‑state in CI test.
* HE‑300 benchmark still passes (transport‑agnostic).
* Daily Merkle anchor script succeeds with Veilid logs included.

Ping @Eric when branch `feature/veilid-transport` is ready for PR.
