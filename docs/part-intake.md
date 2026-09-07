# Prototype part intake and revision lock

This procedure runs **before T909 physical measurement capture**. Its purpose is to prove which exact hardware revision was received so later CAD-driving measurements cannot silently inherit the identity of a different SKU, PCB revision, or substitute part.

## Files

- Frozen candidate BOM: `bom/prototype-v1.md`
- Blank receipt manifest: `measurements/prototype-v1.intake.template.json`
- Intake validator: `measurements/validate_intake.py`
- T909 measurement template: `measurements/prototype-v1.template.json`
- Physical measurement procedure: `docs/measurement-capture.md`

The intake manifest records identity and receipt evidence only. **Do not copy planning/vendor dimensions into the intake manifest or into measured CAD-driving values.**

## Receipt workflow

For each physical item, work through the matching `component_id` entry before taking CAD-driving measurements.

1. Confirm the package/component is actually present and set `receipt_state` to `received` only after inspection.
2. Record the manufacturer, ordered SKU and received SKU where available. Record the visible PCB/revision marking, serial/lot, supplier, or other durable identity discriminator supplied by the item.
3. Capture evidence-photo paths or immutable references showing labels, revision markings, connector side/orientation, and any visible substitution. Photos are evidence references; do not embed private purchase-account details in the public repository.
4. Record included cables/fasteners/accessories, shipping or component damage, and obvious anomalies.
5. Verify connector orientation and inspect whether the delivered item matches the frozen BOM selection. Set `bom_match` to `match` or `substitution`; a substitution requires a written `substitution_reason` and must be reviewed as a new mechanical identity.
6. Record any measurement blockers. Examples: missing mating plug, damaged mounting boss, absent fastener, inaccessible revision mark, or a substituted part that has not been accepted.
7. Set `measurement_ready` only when the received identity is resolved, blockers are empty, and the exact item is ready to be measured.
8. Generate the expected identity fingerprint with:

   ```bash
   python3 measurements/validate_intake.py measurements/prototype-v1.intake.json --fingerprints
   ```

   Copy the matching `sha256:...` value into that item's `identity_lock`, then validate again.
9. Before handing the dataset to T909, run:

   ```bash
   python3 measurements/validate_intake.py measurements/prototype-v1.intake.json --require-ready
   ```

A changed received SKU, revision/PCB marking, serial/lot, supplier identity, or component mapping changes the fingerprint. That prevents a previous identity lock from validating against a silently substituted revision.

## Mapping to T909

The intake `component_id` is the stable handoff key. T909 should capture measurements only against the actual received item represented by that intake entry and record the relevant received serial/lot or revision in the measurement record where supported.

If an item is replaced after measurements begin:

1. return the intake entry to a non-ready state;
2. record the new received identity and evidence;
3. recompute the identity lock;
4. invalidate/re-capture CAD-driving measurements affected by the replacement;
5. do not treat dimensions from the earlier identity as measurements of the replacement.

The intake fingerprint proves identity continuity; it does **not** prove dimensional correctness or physical fit. T909 still requires real caliper/fit-coupon measurements, and T910 remains blocked until those measured records are complete.

## Template semantics

The checked-in `.template.json` intentionally uses `pending`, `unverified`, `measurement_ready: false`, and `identity_lock: null`. It is safe for CI and is not evidence that any part has arrived.

A real intake file may remain outside version control while it contains purchase/serial information. If committed publicly, redact account/order identifiers that are not needed to identify the physical revision, while retaining enough manufacturer/SKU/revision evidence for the T909 mechanical handoff.
