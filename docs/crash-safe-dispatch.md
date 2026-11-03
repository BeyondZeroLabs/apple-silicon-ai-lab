# Crash-safe worker dispatch

Proposed fail-closed recovery contract for a local worker after a supervisor crash. This document does not implement a supervisor, a worker, a barrier, or a test, and it does not launch a worker.

A committed claim and process creation are separate operations. A crash between them can leave an ambiguous outcome: a durable claim with no verified process, a live process with no verified identity, or released work with no receipt. Recovery does not guess which of those happened.

## Inspected repository guidance

Existing recovery notes were inspected and left unchanged. They use proposed language for leases, goal states, checkpoints, quarantine, and receipts. That documentation and its terminology are **UNVERIFIED** as a runtime dispatch or recovery contract. This document does not treat those notes as proof that a claim, spawn, release, or cleanup is crash-safe.

## Contract

After a supervisor crash, an unresolved job fails closed.

### Durable single-use claim

Before a worker is created, the supervisor records one claim for one job. The claim names the job, a single owner, and a launch-generation id chosen for that attempt. A second owner must not adopt the same claim. Recording the claim does not create the process. Creating the process does not release the job.

The claim is single-use. Closing it requires a verified terminal record for that same generation. A missing process listing is not a terminal record.

**UNVERIFIED**: the assumption that a persistence primitive already described in this repository, such as exclusive create, rename, directory sync, or a lease field, makes this claim durable across crash or power loss.

### Uncertain-launch quarantine

If a claim is durable and the launch outcome is not both a verified identity and a later receipt, the job is quarantined. Quarantine forbids a second worker for that claim, forbids release, and forbids treating the job as complete or as never started.

### Identity verification

A process is the claimed worker only when an observation carries the launch-generation id stored in the claim. A mismatch leaves the job quarantined. Recovery does not release the job and does not start a replacement.

**UNVERIFIED**: the assumption that a command line, working directory, start time, or process id is a sufficient substitute for that launch-generation id.

### Refusal to replay an unresolved job

An unresolved job is not replayed. A later attempt needs a new claim and a new launch-generation id, and only after the prior claim has a verified terminal record. Restarting the supervisor does not create that record.

**UNVERIFIED**: the assumption that a restart may safely re-dispatch a job whose launch, release, or receipt was never resolved.

## Worker-start barrier

A worker-start barrier is a candidate ordering, not a proven guarantee:

1. Durably commit the single-use claim.
2. Spawn the worker.
3. Verify identity against the launch-generation id.
4. Release the job to that verified worker.
5. Accept a receipt only from that same generation.

**UNVERIFIED**: the assumption that a barrier, lock, or start gate makes the claim and process creation atomic, or that it removes the crash windows below.

### Crash before spawn

The claim write and the spawn have not both finished. If a durable claim is visible and spawn was not followed by a verified identity, quarantine that claim and do not spawn. If no claim record is visible, do not treat that gap as proof the write never reached stable storage, and do not spawn on the strength of the missing record.

**UNVERIFIED**: the assumption that a missing claim record proves the write never reached stable storage. A missing record is not proof that a claim is absent.

### Crash after spawn

The process may exist while its identity is still unverified. Quarantine the claim. Do not spawn another worker. Do not mark the job complete. Do not replay it.

### Crash before release

A process may be alive, and it may match the claim, while the barrier has not released the job. Recovery does not release the job. An identity match is required before any later release, and a match alone does not finish the job. Leave the claim quarantined until that generation has both a durable release record and a receipt, or until a verified terminal record closes it. Do not replay.

### Crash after release but before receipt

The worker may still be running, may have finished, or may already have had effects, and no receipt is stored. A missing receipt is neither success nor proof that the job did not run. Quarantine the claim and refuse replay.

**UNVERIFIED**: the assumption that work after release is idempotent and therefore safe to repeat when the receipt is missing.

## What does not prove process absence

The following results do not prove that the worker process is absent:

- Process id alone. Identifiers are reused. A recorded id can name an unrelated live process, and a dead id does not say which program exited.
- Missing observations. No log line, heartbeat, receipt, or process-table row in the observer's view can mean the worker is running outside that view.
- Denied access. A permission error, an unreadable process table, a sandbox boundary, or a failed query means the check did not succeed.

**UNVERIFIED**: any recovery rule that treats a process-id check, a missing observation, or denied access as proof that the worker exited or that a new spawn is safe.

## Future tests

These tests are specified only. They are not implemented by this change, and this document does not claim that they pass.

1. Competing owners. Two supervisors attempt the same job. One claim is kept. The other does not spawn. If the winner crashes, the loser does not adopt the unresolved claim.
2. Crash boundaries. A crash is injected before spawn, after spawn, before release, and after release but before a receipt. Each path fails closed and does not start a second worker for that claim.
3. Identity mismatch. The observed generation id differs from the claim. Recovery does not release the job and does not replay it.
4. Failed persistence. A claim write, an identity write, or a receipt write fails or stops mid-write. A partial record is not treated as success, and the job is not replayed because of it.
5. Late cleanup. Quarantine is cleared only after a verified terminal record. Delayed cleanup does not delete the only evidence of an uncertain launch and then start a duplicate.

## Assumptions marked UNVERIFIED

1. **UNVERIFIED**: Existing recovery documentation and terminology already define or implement this crash-safe dispatch contract.
2. **UNVERIFIED**: A persistence primitive already described in this repository makes a single-use claim durable across crash or power loss.
3. **UNVERIFIED**: A missing claim record proves the claim write never reached stable storage.
4. **UNVERIFIED**: A command line, working directory, start time, or process id can replace a recorded launch-generation id.
5. **UNVERIFIED**: A supervisor restart may safely re-dispatch a job whose launch outcome is unresolved.
6. **UNVERIFIED**: A worker-start barrier makes claim and process creation atomic, or removes the crash windows.
7. **UNVERIFIED**: Work released before a receipt is idempotent and therefore safe to repeat.
8. **UNVERIFIED**: A process id alone, a missing observation, or denied access proves process absence.
9. **UNVERIFIED**: Late or automatic cleanup of an unresolved claim is safe.

No test listed above is claimed to pass.
