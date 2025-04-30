# CIRISNode

> Alignment & governance back-plane for the CIRIS ecosystem  
> Status: **CONCEPTUAL — no code or containers yet**

---

## 1  Overview

CIRISNode (née “EthicsEngine Enterprise”) is the remote utility that CIRISAgent clients will call for:

- **Alignment benchmarking** (Annex J HE-300 suite)  
- **Secure communications** via a Matrix homeserver integration  
- **Governance workflows** (WA ticketing, audit anchoring)  
- **SSI/DID support** through a Hyperledger Aries side-car

---

## 2  Core Responsibilities

1. **Alignment API**  
   Runs HE-300 scenarios, enforces pass/fail gates, returns signed benchmark reports.

2. **WA API**  
   Receives Wisdom-Based Deferral packages, relays to Wise Authorities, streams replies.

3. **SSI/DID API**  
   Issues and verifies W3C DIDs and verifiable credentials for audit roots and reports.

4. **Audit Anchoring**  
   Publishes daily SHA-256 roots of logs and benchmark results into a Matrix “transparency” room and mints them as `CIRIS-AuditRoot` credentials.

---

## 3  Proposed API Endpoints

- **GET** /api/v1/health  
- **POST** /api/v1/did/issue → `{ did, verkey, token }`  
- **POST** /api/v1/did/verify → verification result  
- **POST** /api/v1/matrix/token → Matrix access token  
- **POST** /api/v1/benchmarks/run → start HE-300  
- **GET** /api/v1/benchmarks/status/{run_id}  
- **GET** /api/v1/benchmarks/results/{run_id} → signed report + VC  
- **POST** /api/v1/wa/ticket → submit deferral package  
- **GET** /api/v1/wa/status/{ticket_id}

*All responses are JSON-Web-Signed; clients verify via the Aries agent.*

---

## 4  SSI / DID Integration

- Aries side-car issues Verifiable Credentials for:
  - Benchmark reports (`CIRIS-BenchReport`)  
  - Daily audit roots (`CIRIS-AuditRoot`)  

- Agents authenticate using short-lived, DID-scoped tokens.  
- Matrix access is granted via Aries-issued tokens bound to each DID.

---

## 5  Naming & Migration Plan

- References to “EthicsEngine Enterprise” will be renamed to **CIRISNode** once Matrix & SSI flows stabilize.  
- Documentation will use “CIRISNode (née EthicsEngine Enterprise)” until final branding is confirmed.  
- **TBD**: exact Matrix room IDs, Aries agent configuration parameters, governance charter hooks.

---

## 6  Next Steps

- Draft OpenAPI specification for `/api/v1/*` endpoints.  
- Design architecture and data-flow diagrams.  
- Prototype Aries integration and Matrix provisioning scripts.  
- Migrate existing EEE documentation into this new spec as code is developed.

---

## 7  License

This README is licensed under Apache 2.0 © 2025 CIRIS AI Project

