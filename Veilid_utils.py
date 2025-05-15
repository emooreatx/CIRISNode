#!/usr/bin/env python3 """ veilid_node_utils.py

Utility CLI for CIRISNode’s Veilid integration (node-side). Supports:

1. keygen      - generate & store WA keypair


2. recordgen   - create a shared DHT record for WA<->agent chat


3. handshake   - derive shared secret with an agent


4. register    - advertise this WA in the registry



Usage: python veilid_node_utils.py keygen python veilid_node_utils.py recordgen --agent-key AGENT_PUBKEY python veilid_node_utils.py handshake --agent-key AGENT_PUBKEY python veilid_node_utils.py register WA_NAME

Generated files in $HOME: .ciris_node_keys.json      (WA public_key & secret) .ciris_node_record.json    (DHT record key) .ciris_node_secrets.json   (shared secrets per agent) """ import argparse import asyncio import json import base64 import logging from pathlib import Path

import veilid from cirisnode.veilid_provider.registry import advertise_profile, list_profiles, Role

File paths

KEYSTORE       = Path.home() / ".ciris_node_keys.json" RECORDSTORE    = Path.home() / ".ciris_node_record.json" SECRETSTORE    = Path.home() / ".ciris_node_secrets.json" LOG = logging.getLogger("veilid_node_utils") logging.basicConfig(level=logging.INFO)

async def do_keygen(args): """Generate a new WA keypair and save to KEYSTORE.""" conn = await veilid.api_connector(lambda *a, **k: None) crypto = await conn.get_crypto_system(veilid.CryptoKind.CRYPTO_KIND_VLD0) async with crypto: keypair = await crypto.generate_key_pair() await conn.close()

data = {"public_key": keypair.key(), "secret": keypair.secret()}
KEYSTORE.write_text(json.dumps(data))
print(f"WA keypair generated. Public key:\n  {data['public_key']}")
LOG.info("Saved WA keypair to %s", KEYSTORE)

async def do_recordgen(args): """Create a new DHT record for WA<->agent communications, store key.""" # ensure keys exist if not KEYSTORE.exists(): LOG.error("WA keystore missing. Run keygen first.") return ks = json.loads(KEYSTORE.read_text()) wa_pair = veilid.Keypair(ks["public_key"], ks["secret"])

agent_key = args.agent_key
if not agent_key:
    # try first agent in registry
    conn = await veilid.api_connector(lambda *a, **k: None)
    router = await (await conn.new_routing_context()).with_default_safety()
    agents = await list_profiles(router, Role.AGENT)
    await conn.close()
    if not agents:
        LOG.error("No agents found in registry. Provide --agent-key.")
        return
    agent_key = agents[0]["public_key"]
agent_pub = veilid.PublicKey(agent_key)

conn = await veilid.api_connector(lambda *a, **k: None)
router = await (await conn.new_routing_context()).with_default_safety()
# create SMPL record with both WA and agent
members = [
    veilid.DHTSchemaSMPLMember(agent_pub, 1),
    veilid.DHTSchemaSMPLMember(wa_pair.key(), 1)
]
rec = await router.create_dht_record(veilid.DHTSchema.smpl(0, members))
# close then open for WA
await router.close_dht_record(rec.key)
await router.open_dht_record(rec.key, wa_pair)
await conn.close()

RECORDSTORE.write_text(json.dumps({"record_key": rec.key.to_str()}))
print(f"DHT record created: {rec.key}")
LOG.info("Saved record key to %s", RECORDSTORE)

async def do_handshake(args): """Derive shared secret with an agent and store in SECRETSTORE.""" if not KEYSTORE.exists(): LOG.error("WA keystore missing. Run keygen first.") return ks = json.loads(KEYSTORE.read_text()) wa_secret = ks["secret"] wa_priv = wa_secret

agent_key = args.agent_key
if not agent_key:
    # pick first agent from registry
    conn = await veilid.api_connector(lambda *a, **k: None)
    router = await (await conn.new_routing_context()).with_default_safety()
    agents = await list_profiles(router, Role.AGENT)
    await conn.close()
    if not agents:
        LOG.error("No agents found in registry. Provide --agent-key.")
        return
    agent_key = agents[0]["public_key"]
agent_pub = agent_key

conn = await veilid.api_connector(lambda *a, **k: None)
crypto = await conn.get_crypto_system(veilid.CryptoKind.CRYPTO_KIND_VLD0)
secret = await crypto.cached_dh(agent_pub, wa_priv)
await conn.close()

sm = json.loads(SECRETSTORE.read_text()) if SECRETSTORE.exists() else {}
sm[agent_pub] = base64.b64encode(secret.to_bytes()).decode()
SECRETSTORE.write_text(json.dumps(sm))
print(f"Derived secret for agent {agent_pub}")
LOG.info("Saved shared secret to %s", SECRETSTORE)

async def do_register(args): """Advertise WA profile in registry so agents can discover this WA.""" if not KEYSTORE.exists(): LOG.error("WA keystore missing. Run keygen first.") return ks = json.loads(KEYSTORE.read_text()) pub = ks["public_key"]

conn = await veilid.api_connector(lambda *a, **k: None)
router = await (await conn.new_routing_context()).with_default_safety()
profile = {"name": args.name, "public_key": pub}
await advertise_profile(router, Role.WA, profile)
await conn.close()

print(f"WA '{args.name}' registered with public key {pub}")
LOG.info("Published WA profile to registry")

def main(): p = argparse.ArgumentParser(description="CIRISNode Veilid node utilities") sub = p.add_subparsers(dest='cmd', required=True)

k = sub.add_parser('keygen', help='Generate WA keypair')
k.set_defaults(func=lambda args: asyncio.run(do_keygen(args)))

r = sub.add_parser('recordgen', help='Create DHT record for WA<->agent')
r.add_argument('--agent-key', help='Specific agent public key')
r.set_defaults(func=lambda args: asyncio.run(do_recordgen(args)))

h = sub.add_parser('handshake', help='DH handshake with agent')
h.add_argument('--agent-key', help='Specific agent public key')
h.set_defaults(func=lambda args: asyncio.run(do_handshake(args)))

reg = sub.add_parser('register', help='Register this WA in the registry')
reg.add_argument('name', help='Human-readable WA name')
reg.set_defaults(func=lambda args: asyncio.run(do_register(args)))

args = p.parse_args()
args.func(args)

if name == 'main': main()

