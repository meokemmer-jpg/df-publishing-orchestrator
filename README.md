# df-publishing-orchestrator [CRUX-MK]

**Welle:** 44 | **Type:** Foundation-DF | **Funktion:** Cross-Book-Coordinator

## Konzept

Orchestriert die 4 Buecher-Trilogie-Foundation-DFs (Symbiotic Minds + AI Leadership +
Mathematik der Macht + Souveraene Maschine). Koppelt mit Graphity-Verlag (VG-Wort-Royalties +
METIS-Reform-Compliance).

## Module

- `graphity_verlag_connector.py`: Verlag-Coupling-Stub (kein Real-API in Skeleton)
- `vg_wort_tracker.py`: Royalty-Tracking-Stub (METIS-Reform 2026+ ready)
- `metis_reform_compliance.py`: METIS-Reform-Compliance-Checker
- `publishing_orchestrator.py`: 4-Books-Coordination
- `audit_logger.py`: HMAC-SHA256-Hash-Chain

## Strict-Conditions

- KEIN Auto-Push to Verlag-Plattformen
- KEIN Echtgeld-Workflow (VG-Wort-Buchungen sind Tracking-only)
- KEIN Real-API ohne ENV `DF_PUBLISHING_REAL_ENABLED=true` + PHRONESIS_TICKET
- Mock-Default: Verlag-Connector + VG-Wort-Tracker geben Mock-Responses

## CRUX-Bindung

- **K_0:** indirekt (Royalty-Income, kein Capital-Risk)
- **Q_0:** nicht direkt
- **W_0:** Architekt-Bandbreite via Mock-Default geschuetzt
- **rho:** geschaetzt +€20-100k/Jahr (4 Buecher Royalties + Brand-Building)

## Beziehung zu anderen DFs

- **df-symbiotic-minds-writer:** Producer
- **df-ai-leadership-writer:** Producer
- **df-mathematik-der-macht-writer:** Producer
- **df-souveraene-maschine-writer:** Producer
- **_df_common:** atomic_io + audit_log

[CRUX-MK]
