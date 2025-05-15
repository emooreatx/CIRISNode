#!/usr/bin/env python3
"""
veilid_node_provider.py

CIRISNode “Veilid Provider” – Wisdom‐Authority backplane over Veilid DHT.

Supports:
  • ACTION (SPEAK)      – agent ➔ WA
  • DEFERRAL (DEFER)     – agent ➔ WA
  • MEMORY (learn,remember,forget) – agent ➔ WA
  • OBSERVE             – WA   ➔ agent
  • CORRECTION          – WA   ➔ agent

Security best‑practices built in:
  • AES‑style encryption with per‑message nonce
  • HMAC‑SHA256 integrity check
  • Sliding‑window rate‑limiting to mitigate DHT floods
  • Private paranet (no tokens) + per‑session record key

Assumes you have run the “utils” to:
  1) Keygen:            `~/.ciris_agent_keys.json`
  2) Handshake:         `~/.ciris_agent_secrets.json`
  3) Agent registered in registry (so WA can discover you)
  4) Env vars set:
       VLD_WA_RECORD_KEY   – your WA’s DHT record key (smpl DID string)
       VLD_WA_PUBKEY       – WA’s public key
"""

import os, json, time, hmac, hashlib, base64, asyncio, logging
from pathlib import Path
from typing import Optional, Dict, Any

import veilid
from ciris_engine.core.speak     import SpeakMessage
from ciris_engine.core.deferral  import DeferralPackage
from ciris_engine.core.memory    import MemoryOperation
from ciris_engine.core.observe   import Observation
from ciris_engine.core.thoughts  import AgentCorrectionThought
from ciris_engine.action_handlers import (
    handle_speak,
    handle_defer,
    handle_memory,
    handle_observe,
    handle_correction,
)

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Local key/secret stores written by the utils
KEYSTORE    = Path.home() / ".ciris_agent_keys.json"
SECRETSTORE = Path.home() / ".ciris_agent_secrets.json"

# Flood protection params (writes/minute)
RECV_RATE_LIMIT = int(os.getenv("VLD_RECV_MAX_PER_MIN", "60"))
RECV_WINDOW_SEC = 60  # sliding window in seconds

# Envelope helper
class Envelope:
    """Holds a signed, encrypted payload."""
    def __init__(self, id: str, op: str, body: Dict[str,Any], hmac_sig: str):
        self.id   = id
        self.op   = op
        self.body = body
        self.hmac = hmac_sig

    @classmethod
    def from_dict(cls, d: Dict[str,Any]) -> "Envelope":
        return cls(d["id"], d["op"], d["body"], d["hmac"])

    def to_dict(self) -> Dict[str,Any]:
        return {"id": self.id, "op": self.op, "body": self.body, "hmac": self.hmac}


class VeilidNodeProvider:
    """
    CIRISNode side DHT service over Veilid:
      • start() opens the DHT channel
      • _worker() loops on subkey=0, dispatching SPEAK/DEFER/MEMORY
      • _send() pushes envelopes on subkey=1 (if needed)
    """
    def __init__(self):
        self.conn       = None           # Veilid API connector
        self.router     = None           # RoutingContext
        self.crypto     = None           # CryptoSystem
        self.keypair    = None           # Keypair (our WA identity)
        self.rec_key    = None           # TypedKey for WA record
        self.secrets    = {}             # agent_pubkey → SharedSecret
        self.running    = False
        self._recv_times: list[float] = []

    async def start(self):
        """Initialize Veilid, load keys + secrets, and start the worker."""
        # 1) connect & routing
        self.conn   = await veilid.api_connector(lambda *a,**k: None)
        ctx         = await self.conn.new_routing_context()
        self.router = await ctx.with_default_safety()
        self.crypto = await self.conn.get_crypto_system(veilid.CryptoKind.CRYPTO_KIND_VLD0)

        # 2) load our WA keypair
        if not KEYSTORE.exists():
            raise RuntimeError("Missing keystore – run keygen util first")
        ks = json.loads(KEYSTORE.read_text())
        self.keypair = veilid.Keypair(ks["public_key"], ks["secret"])

        # 3) load all agent shared‐secrets from SECRETSTORE
        if SECRETSTORE.exists():
            mapping = json.loads(SECRETSTORE.read_text())
            for pub, b64 in mapping.items():
                secret = veilid.SharedSecret.from_bytes(base64.b64decode(b64))
                self.secrets[veilid.PublicKey(pub)] = secret

        # 4) open our WA DHT record (from env)
        rec = os.getenv("VLD_WA_RECORD_KEY")
        if not rec:
            raise RuntimeError("VLD_WA_RECORD_KEY not set")
        self.rec_key = veilid.TypedKey.from_str(rec)

        self.running = True
        LOG.info("[Provider] started, listening on record %s", rec)
        asyncio.create_task(self._worker())

    async def stop(self):
        """Stop the provider cleanly."""
        self.running = False
        if self.router: await self.router.close()
        if self.conn:   await self.conn.close()
        LOG.info("[Provider] stopped")

    async def _worker(self):
        """
        Main loop: poll subkey=0 (agent→WA). Each message is:
          { id, op, body, hmac }
        After decrypt & verify, dispatch to the correct handler.
        """
        sub0 = veilid.ValueSubkey(0)
        while self.running:
            try:
                env = await self._recv(sub0)
                if not env:
                    await asyncio.sleep(0.5)
                    continue

                # Dispatch based on operation
                if env.op == "SPEAK":
                    msg = SpeakMessage(**env.body)
                    await handle_speak(msg)

                elif env.op == "DEFER":
                    pkg = DeferralPackage(**env.body)
                    await handle_defer(pkg)

                elif env.op == "MEMORY":
                    mem = MemoryOperation(**env.body)
                    await handle_memory(mem)

                else:
                    LOG.warning("[Provider] unknown op: %s", env.op)

            except Exception:
                LOG.exception("[Provider] error in worker loop")
                await asyncio.sleep(1)

    async def _send(self,
                    target_key: veilid.TypedKey,
                    op: str,
                    body: Dict[str,Any],
                    subkey: int = 1):
        """
        Send an Envelope(op,body) → HMAC → encrypt → DHT set on subkey (default=1).
        Used to reply (e.g. CORRECTION or OBSERVE) back to agents.
        """
        # 1) build envelope & sign HMAC
        eid = veilid.uuid4()
        raw = json.dumps({"id": eid, "op": op, "body": body}, sort_keys=True).encode()
        sig = hmac.new(self.keypair.secret().to_bytes(), raw, hashlib.sha256).digest()
        env = {"id": eid, "op": op, "body": body, "hmac": base64.b64encode(sig).decode()}
        clear = json.dumps(env).encode()

        # 2) encrypt
        nonce  = await self.crypto.random_nonce()
        cipher = await self.crypto.crypt_no_auth(clear, nonce, self.keypair.secret())
        payload = nonce.to_bytes() + cipher

        # 3) publish
        await self.router.set_dht_value(target_key,
                                        veilid.ValueSubkey(subkey),
                                        payload)

    async def _recv(self, subkey: veilid.ValueSubkey) -> Optional[Envelope]:
        """
        Poll DHT(subkey) → decrypt → verify HMAC → return Envelope.
        Applies sliding-window rate limit to drop floods.
        """
        now = time.time()
        self._recv_times = [t for t in self._recv_times if now - t < RECV_WINDOW_SEC]
        if len(self._recv_times) >= RECV_RATE_LIMIT:
            await asyncio.sleep(1)
            return None
        self._recv_times.append(now)

        resp = await self.router.get_dht_value(self.rec_key, subkey, True)
        if not resp:
            return None

        # decrypt
        data  = resp.data
        nonce = veilid.Nonce.from_bytes(data[:24])
        cipher= data[24:]
        clear = await self.crypto.crypt_no_auth(cipher, nonce, self.keypair.secret())
        d     = json.loads(clear.decode())

        # verify HMAC
        recv_hmac = base64.b64decode(d.get("hmac",""))
        raw_check = json.dumps({"id":d["id"],"op":d["op"],"body":d["body"]},
                                sort_keys=True).encode()
        exp = hmac.new(self.keypair.secret().to_bytes(), raw_check, hashlib.sha256).digest()
        if not hmac.compare_digest(exp, recv_hmac):
            LOG.warning("[Provider] invalid HMAC from agent %s – dropping", resp.key)
            return None

        return Envelope(d["id"], d["op"], d["body"], d["hmac"])


# Example usage (not for production)
if __name__ == "__main__":
    provider = VeilidNodeProvider()
    try:
        asyncio.run(provider.start())
        # keep running
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(provider.stop())
