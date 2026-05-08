# Anchor / Causa

Anchor (and its DB layer, Causa) is an execution engine aiming to transform the non-deterministic nature of LLMs into a reliable, deterministic process for OS operations by acting as a Precedent Engine that prioritizes human-approved actions.

- **Manifesto**: [Anchor LLM & Anchor DB (Causa) v1.0](docs/manifesto/anchor-llm-causa-v1.md)
- **Current Status**: Research/Prototype
- **Safety Status**: No autonomous OS execution is implemented yet

## Current Version
- Causa Core v1.0-alpha
- Non-executing
- Storage-agnostic
- InMemoryRepository only
- SQLite local adapter is the next likely persistence step

## Current Capabilities

Causa Core currently supports the following capabilities:
- **Representing a precedent** as an `AnchorRecord`
- **Storing and retrieving** `AnchorRecord` using an `InMemoryCausaRepository`
- **Making replay decisions** using `determine_replay_decision_from_record`
- **Returning machine-readable** `ReplayDecision` outputs
- **Building human-readable** `AuditSummary` explanations
- **Running non-executing** end-to-end simulations

## Architecture Flow

The logical pipeline for assessing a replay decision is:
`AnchorRecord` → `InMemoryCausaRepository` → `determine_replay_decision_from_record` → `ReplayDecision` → `build_audit_summary` → `AuditSummary`

## Storage Direction

- Causa Core is explicitly storage-agnostic.
- `InMemoryCausaRepository` is intended strictly for tests and local simulation.
- A local SQLite adapter is the next likely persistence step.
- PostgreSQL / Supabase may be added later via specific storage adapters.
- The deterministic logic in `decision.py` must remain completely independent from storage implementations.

## Non-goals for v1.0-alpha

The v1.0-alpha scope freeze explicitly excludes any of the following capabilities:
- OS execution
- Autonomous replay
- Accessibility API calls
- Dify integration
- Sudo or privilege escalation
- Network calls
- Destructive operations
- Production database usage
- Supabase integration
- PostgreSQL integration

## Usage Example

```python
from datetime import datetime
from causa_core.storage.memory import InMemoryCausaRepository
from causa_core.decision import determine_replay_decision_from_record
from causa_core.audit import build_audit_summary
from tests.fixtures import build_successful_anchor_record

# 1. Create Repository & Mock Record
repo = InMemoryCausaRepository()
record = build_successful_anchor_record()
repo.save_anchor_record(record)

# 2. Retrieve Record
retrieved_record = repo.get_anchor_record(record.anchor_case.id)

# 3. Determine Replay Decision
decision = determine_replay_decision_from_record(
    current_ui_snapshot=record.ui_snapshot,
    current_risk_level=1,
    current_business_object_id="obj1",
    current_action_payload_hash="pay123",
    historical_record=retrieved_record,
    current_time=datetime(2024, 1, 1, 12, 0, 0),
)

# 4. Build Audit Summary
audit = build_audit_summary(decision, retrieved_record)

print(f"Status: {decision.status}")
print(f"Reason: {decision.reason_code}")
print(f"Summary: {audit.summary}")
```
