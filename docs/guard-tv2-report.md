> Cập nhật cuối hồ sơ: đã bổ sung đủ file thẻ theo yêu cầu người dùng; grade R-S5-grade-20261118-184018-883400 đạt PASS-VISIBLE và integrity. Các trạng thái thiếu file/chưa ký/chưa tích hợp bên dưới là ghi chép lịch sử. Xem submission/REPORT.md và submission/docs/ để đọc hồ sơ cuối.

# TV2 Guard Analysis and Handover

## Scope and current state

This analysis follows the TV2 work request in `MyToDo.md`. The repository currently has no `AGENTS.md` instructions and no incident pack under `incidents/S1`–`S8`; `incidents/README.md` says those files arrive after the team receives its incident card. No incident was inferred or selected.

The team-owned acceptance criteria are still blank and unsigned. The current operating gates also have blank business and legal settings. Both remain unchanged. The Round 1 checkpoint files are absent, so this work has not created or replaced a `guards_round1.py`, `operating_gates.round1.json`, or `round1.lock` snapshot.

## Architecture verified from code

`lab10.agent.run_ticket()` calls `pre_guard(ctx)` before sending ticket text to the model. It later obtains the order and tracking, computes a proposal, then calls `write_gate(ctx, action)` through `WriteTools` before every write. The relevant write order is:

1. `issue_refund` writes the ledger.
2. `file_carrier_fault` records a carrier strike.
3. `notify_carrier` sends a message to the carrier.
4. `send_reply` sends a message to the customer.

`Verdict.allow` permits, `deny` skips one write while the agent continues, `escalate` queues the ticket, and `modify` replaces write arguments. A later denial cannot reverse an earlier ledger write.

The trusted read interface includes order/customer/tracking, policies, approvals, ledger/fault rows, current date, and agreed operating limits. Ticket text and model proposals are untrusted. The active policy-index flag is not guaranteed to match the effective date, so policy selection needs date validation.

## Findings before the change

- `pre_guard` and `write_gate` were unconditional allows.
- The agent can replace tracking delay with the customer's claimed number.
- If policy evaluation hits its rate limit twice, the agent's fallback proposes a refund without the normal policy calculation.
- For missing tracking cause, the agent assumes `CARRIER` when deciding blame.
- Large-refund approval lookup may fall back from order-scoped approvals to customer-scoped approvals; the write guard therefore needs to validate approval identity and scope itself.
- The carrier notice can include the original customer message and, for gifts, the recipient's name and phone.
- Existing host checks cap a refund at total paid for the order and enforce configured business gates, but they do not validate policy entitlement or correct payer.
- Since the refund is written before a carrier fault, checking evidence only at the carrier-fault step would leave the customer refund in place.

## Guards added

### 1. Policy pin and refund validation

`pre_guard` pins the policy effective on `ctx.as_of`. If no valid policy can be established, it escalates. Before `issue_refund`, the guard checks a positive integer amount, original ticket/order identity, order ownership, canonical parcel tracking, recorded delay cause when delayed, effective policy entitlement, and `LOGIX` as payer. Refunds above policy's automatic limit require an approval matching the exact ticket, order, customer, amount, status, and expiry. Automatic refund customer/day and finance/day caps use `ops_limits()` and escalate when exceeded. A duplicate write for the ticket is denied.

The entitlement is computed from tracking dates and recorded cause, never from the model's claimed delay. Missing tracking or policy facts fail closed to a human. An amount above entitlement is denied before the ledger write. Any supplied approval is verified even when the refund is below the automatic limit, so an invalid approval cannot be used to bypass operating caps.

### 2. Carrier evidence validation

`file_carrier_fault` is allowed only when the order belongs to the ticket customer, the parcel and carrier match source data, delay is at least the policy threshold, delay days equal the tracking calculation, and the recorded cause is in the effective policy's fault causes. Missing or conflicting evidence denies the strike.

### 3. Privacy and recipient validation

Carrier notifications are rebuilt from canonical order/tracking facts and restricted to the effective policy's `carrier_notice_fields`. Customer message text and recipient contact details are never forwarded. Replies must target the order owner; detected email, phone, customer name, and known address details are redacted before sending.

Guard logs record decision kinds and field names only; they do not log message contents or sensitive values. Unexpected validation errors escalate rather than allow a write.

## Actions allowed, denied, or escalated

- **Allowed:** policy-consistent refunds for the ticket's verified order/customer, with the correct payer and valid approval if above the automatic limit; carrier strikes supported by matching official tracking; minimized notices with policy-allowed operational fields; replies addressed to the order owner.
- **Denied:** invalid/nonpositive refund amounts, amounts above policy entitlement, unauthorized payer, duplicate refunds, unsupported carrier strikes, and notices/replies with invalid recipients.
- **Escalated:** missing/invalid effective policy, unverifiable order/customer/tracking, missing approval for an above-limit refund, unavailable operating caps, and unexpected guard errors.
- **Modified:** carrier notices are reduced to canonical allowed fields; replies have detected unnecessary personal details redacted.

No config threshold was hardcoded. Thresholds come from the effective policy, `ops_limits()`, or the team's operating gates already enforced by the write tools.

## Verification

Ran `python3 -m unittest discover -s tests`: **23 tests passed**. This includes the existing public regression test that confirms every previously passing base ticket remains passing, as well as focused guard cases for policy pinning, forged delay claims, amount types and bounds, payer/order mismatch, approval validity, carrier evidence, notice minimization, reply redaction, and recipient validation.

The full evaluation command was not run because the repository's rules require acceptance criteria to be signed before viewing evaluation results. The criteria file is intentionally still blank and unsigned. No incident-grade run is possible until the team's assigned incident pack and recorded card number are available. Passing tests do not establish production safety.

## Incident work (C5/C6/C7/C9)

Not applicable yet: the repository has no incident card and no assigned S1–S8 number. Do not write a hypothetical incident specification or fault tree. Once the assigned card arrives, run the prepared baseline as required, identify the first bad trace step, and document C5/C6/C7/C9 for that card only. Round 1 snapshot and incident grading remain team workflow steps.

## Demo notes

- **Guard:** an independent system check at the boundary before a write; the model cannot override its result.
- **Agent:** proposes and performs the workflow. It can make mistakes because it consumes customer text and model output.
- **Why guards run at write time:** the final amount and recipient are then visible, and the refund can be stopped before it enters the ledger.
- **Verdicts:** allow preserves a verified action; deny skips a single write; escalate stops the flow and queues a human; modify removes or corrects unsafe fields.
- **Missing evidence:** fail closed. Refund facts go to a human; unsupported carrier blame is not filed.
- **False positives:** conservative checks can send a valid case to review. The base regression test checks that currently passing tickets remain passing, but incident and hidden tests are still required.
- **Effectiveness evidence:** compare before/prepared/after traces and metrics, test both unsafe and valid cases, inspect ledger/fault/outbound state, and check for regressions. A passing unit suite alone is insufficient.

## Changed files

- `lab10/guards.py` — system-level policy, refund, evidence, and privacy checks.
- `tests/test_guards.py` — focused guard tests.
- `docs/guard-tv2-report.md` — this analysis and handover.

## Remaining work

- Team must finish and sign the criteria before running evaluation.
- `ReadTools.ledger_rows()` does not expose a date filter for customer-level totals. The per-customer daily ceiling therefore counts all visible unapproved rows conservatively, including any seeded historical rows; this can send an otherwise valid refund for human review. The finance-wide daily total uses the dedicated `auto_refund_today_vnd()` method.
- Team must complete its Round 1 checkpoint at the appropriate lab milestone; the protected snapshot files were left untouched.
- TV3-owned `lab10/monitors.py` was not changed. Add a monitor only through the team's assigned owner and lab process.
- After the incident card is issued and the team records its draw, complete C5/C6/C7/C9, incident tests, monitor, and after-fix grade.
- A further review should check hidden incident cases, including valid approvals, conflicting parcel evidence, duplicate attempts, and privacy patterns beyond known database values and simple email/phone formats. Reply redaction is a deterministic backstop for detectable identifiers; it is not a general-purpose named-entity detector.
