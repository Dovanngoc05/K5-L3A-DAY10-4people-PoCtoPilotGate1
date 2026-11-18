"""Focused tests for the TV2 system-level write gates."""
import unittest
from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lab10 import guards, helpers as H, ops  # noqa: E402
from lab10.tools import Ctx, ReadTools  # noqa: E402
from lab10.world import World, load_suite  # noqa: E402


class GuardChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.tickets = load_suite("base")
        cls.by_id = {t["ticket_id"]: t for t in cls.tickets}

    def context(self, ticket_id, data=None):
        world = World(data or self.data)
        ticket = dict(self.by_id[ticket_id])
        events = []
        ctx = Ctx(ticket=ticket, seed=11, tools=ReadTools(world), switches={}, events=events,
                  as_of=world.as_of, gates=ops.load_gates("after"))
        return ctx

    def refund_action(self, ctx, amount=25000, **changes):
        return {"tool": "issue_refund", "ticket_id": ctx.ticket["ticket_id"],
                "order_id": ctx.ticket["order_id"], "amount_vnd": amount,
                "payer": "LOGIX", **changes}

    def test_pre_guard_pins_effective_policy(self):
        v = guards.pre_guard(self.context("T-001"))
        self.assertEqual(v.action, "allow")
        self.assertEqual(v.changes["policy_id"], "REFUND-v3")

    def test_refund_uses_tracking_not_customer_claim(self):
        ctx = self.context("T-002")
        v = guards.write_gate(ctx, self.refund_action(ctx, 20000))
        self.assertEqual(v.action, "deny")

    def test_valid_policy_refund_passes(self):
        ctx = self.context("T-001")
        self.assertEqual(guards.write_gate(ctx, self.refund_action(ctx, 25000)).action, "allow")

    def test_refund_amount_requires_positive_integer(self):
        for amount in (-1, 0, None, "25000", True, 1.5):
            with self.subTest(amount=amount):
                ctx = self.context("T-001")
                self.assertEqual(guards.write_gate(ctx, self.refund_action(ctx, amount)).action, "deny")

    def test_wrong_order_or_payer_is_blocked(self):
        ctx = self.context("T-001")
        self.assertEqual(guards.write_gate(ctx, self.refund_action(ctx, 25000, order_id="O-1002")).action,
                         "escalate")
        ctx = self.context("T-001")
        self.assertEqual(guards.write_gate(ctx, self.refund_action(ctx, 25000, payer="MERCHANT")).action,
                         "deny")

    def test_unverified_approval_cannot_bypass_auto_limits(self):
        ctx = self.context("T-001")
        v = guards.write_gate(ctx, self.refund_action(ctx, 25000, approval_id="A-NOT-VALID"))
        self.assertEqual(v.action, "escalate")

    def test_exact_valid_approval_allows_policy_entitlement(self):
        ctx = self.context("T-008")
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                                    "amount_vnd": 230000, "payer": "LOGIX", "approval_id": "A-0008"})
        self.assertEqual(v.action, "allow")

    def _high_value_approval_data(self, max_vnd):
        data = deepcopy(self.data)
        data["approvals"].append({"approval_id": "A-HIGH", "ticket_id": "T-008", "order_id": "O-1008",
                                  "customer_id": "C-08", "approver_id": "NV-HANH", "max_vnd": max_vnd,
                                  "expires_at": data["as_of"], "status": "valid"})
        return data

    def _p1_on_time_p2_late_data(self):
        data = deepcopy(self.data)
        order = next(o for o in data["orders"] if o["order_id"] == "O-1013")
        p1 = next(p for p in order["parcels"] if p["parcel_id"] == "O-1013-P1")
        p2 = next(p for p in order["parcels"] if p["parcel_id"] == "O-1013-P2")
        p1.update(promised_date="2026-11-14", delivered_date="2026-11-14", delay_cause=None)
        p2.update(promised_date="2026-11-06", delivered_date="2026-11-14", delay_cause="CARRIER")
        return data

    def _approval_context(self, as_of="", tools_as_of="2026-11-16", expires_at="2026-11-20"):
        data = self._high_value_approval_data(230000)
        next(a for a in data["approvals"] if a["approval_id"] == "A-HIGH")["expires_at"] = expires_at
        ctx = self.context("T-008", data)
        ctx.as_of = as_of
        ctx.tools.as_of = tools_as_of
        return ctx

    def _approved_refund(self, ctx):
        return {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                "amount_vnd": 230000, "payer": "LOGIX", "approval_id": "A-HIGH"}

    def test_refund_2000001_is_denied_with_hard_cap_log(self):
        ctx = self.context("T-008", self._high_value_approval_data(2_000_001))
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                                    "amount_vnd": 2_000_001, "payer": "LOGIX", "approval_id": "A-HIGH"})
        self.assertEqual(v.action, "deny")
        self.assertIn("2.000.000", v.reason)
        self.assertTrue(any(e.get("kind") == "refund_hard_cap_exceeded"
                            and e.get("amount_vnd") == 2_000_001 for e in ctx.events))

    def test_refund_2000000_passes_hard_cap_then_normal_checks(self):
        data = self._high_value_approval_data(2_000_000)
        order = next(o for o in data["orders"] if o["order_id"] == "O-1008")
        order["goods_value_vnd"] = 2_000_000
        order["shipping_fee_vnd"] = 0
        policy = next(p for p in data["policies"] if p["policy_id"] == "REFUND-v3")
        policy["late"]["bonus_pct"] = 100
        policy["late"]["bonus_cap_vnd"] = 2_000_000
        ctx = self.context("T-008", data)
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                                    "amount_vnd": 2_000_000, "payer": "LOGIX", "approval_id": "A-HIGH"})
        self.assertEqual(v.action, "allow")
        self.assertFalse(any(e.get("kind") in ("refund_hard_cap_exceeded", "refund_order_hard_cap_exceeded")
                             for e in ctx.events))

    def test_valid_approval_cannot_exceed_hard_cap(self):
        ctx = self.context("T-008", self._high_value_approval_data(2_000_001))
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                                    "amount_vnd": 2_000_001, "payer": "LOGIX", "approval_id": "A-HIGH"})
        self.assertEqual(v.action, "deny")
        self.assertTrue(any(e.get("kind") == "refund_hard_cap_exceeded" for e in ctx.events))

    def test_valid_approval_cannot_push_order_total_over_hard_cap(self):
        data = self._high_value_approval_data(230_000)
        data["ledger_seed"].append({"ticket_id": "T-PRIOR", "order_id": "O-1008", "customer_id": "C-08",
                                    "amount_vnd": 1_900_001, "payer": "LOGIX", "approval_id": "A-PRIOR"})
        ctx = self.context("T-008", data)
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-008", "order_id": "O-1008",
                                    "amount_vnd": 230_000, "payer": "LOGIX", "approval_id": "A-HIGH"})
        self.assertEqual(v.action, "deny")
        self.assertTrue(any(e.get("kind") == "refund_order_hard_cap_exceeded"
                            and e.get("prior_refund_vnd") == 1_900_001 for e in ctx.events))

    def test_refund_denies_action_parcel_different_from_ticket_parcel(self):
        ctx = self.context("T-013", self._p1_on_time_p2_late_data())
        v = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-013", "order_id": "O-1013",
                                    "parcel_id": "O-1013-P2", "amount_vnd": 66000, "payer": "LOGIX"})
        self.assertEqual(v.action, "deny")
        self.assertTrue(any(e.get("kind") == "refund_parcel_mismatch" for e in ctx.events))

    def test_fault_denies_action_parcel_different_from_ticket_parcel(self):
        data = self._p1_on_time_p2_late_data()
        p2 = next(p for p in next(o for o in data["orders"] if o["order_id"] == "O-1013")["parcels"]
                  if p["parcel_id"] == "O-1013-P2")
        ctx = self.context("T-013", data)
        v = guards.write_gate(ctx, {"tool": "file_carrier_fault", "ticket_id": "T-013", "order_id": "O-1013",
                                    "parcel_id": "O-1013-P2", "carrier_id": p2["carrier_id"], "delay_days": 8})
        self.assertEqual(v.action, "deny")
        self.assertTrue(any(e.get("kind") == "fault_parcel_mismatch" for e in ctx.events))

    def test_notice_denies_action_parcel_different_from_ticket_parcel(self):
        data = self._p1_on_time_p2_late_data()
        p2 = next(p for p in next(o for o in data["orders"] if o["order_id"] == "O-1013")["parcels"]
                  if p["parcel_id"] == "O-1013-P2")
        ctx = self.context("T-013", data)
        v = guards.write_gate(ctx, {"tool": "notify_carrier", "ticket_id": "T-013",
                                    "carrier_id": p2["carrier_id"],
                                    "payload": {"parcel_id": "O-1013-P2"}})
        self.assertEqual(v.action, "deny")
        self.assertTrue(any(e.get("kind") == "carrier_notice_parcel_mismatch" for e in ctx.events))

    def test_ticket_parcel_p1_still_allows_valid_refund_fault_and_notice(self):
        ctx = self.context("T-013")
        order = ctx.tools.lookup_order("O-1013")
        parcel = next(p for p in order["parcels"] if p["parcel_id"] == "O-1013-P1")
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        delay = H.db_delay_days(parcel, ctx.as_of)
        amount = H.entitlement_vnd(policy, order, delay, parcel["delay_cause"])

        refund = guards.write_gate(ctx, {"tool": "issue_refund", "ticket_id": "T-013", "order_id": "O-1013",
                                         "parcel_id": "O-1013-P1", "amount_vnd": amount, "payer": "LOGIX"})
        fault = guards.write_gate(ctx, {"tool": "file_carrier_fault", "ticket_id": "T-013", "order_id": "O-1013",
                                        "parcel_id": "O-1013-P1", "carrier_id": parcel["carrier_id"],
                                        "delay_days": delay})
        notice = guards.write_gate(ctx, {"tool": "notify_carrier", "ticket_id": "T-013",
                                         "carrier_id": parcel["carrier_id"],
                                         "payload": {"parcel_id": "O-1013-P1"}})
        self.assertEqual(refund.action, "allow")
        self.assertEqual(fault.action, "allow")
        self.assertEqual(notice.action, "modify")

    def test_expired_approval_uses_tools_date_when_context_date_empty_or_invalid(self):
        for context_date in ("", "not-a-date"):
            with self.subTest(context_date=context_date):
                ctx = self._approval_context(as_of=context_date, expires_at="2026-11-01")
                v = guards.write_gate(ctx, self._approved_refund(ctx))
                self.assertIn(v.action, ("deny", "escalate"))
                self.assertTrue(any(e.get("kind") == "refund_approval_invalid" for e in ctx.events))

    def test_missing_or_invalid_context_and_tools_dates_never_allow_refund(self):
        for context_date, tools_date in (("", ""), ("not-a-date", "also-not-a-date")):
            with self.subTest(context_date=context_date, tools_date=tools_date):
                ctx = self._approval_context(as_of=context_date, tools_as_of=tools_date)
                self.assertNotEqual(guards.write_gate(ctx, self._approved_refund(ctx)).action, "allow")
                self.assertEqual(guards.pre_guard(ctx).action, "escalate")

    def test_unexpired_approval_uses_tools_date_fallback(self):
        ctx = self._approval_context(as_of="", tools_as_of="2026-11-16", expires_at="2026-11-20")
        self.assertEqual(guards.write_gate(ctx, self._approved_refund(ctx)).action, "allow")

    def test_carrier_fault_requires_canonical_delay_and_cause(self):
        ctx = self.context("T-001")
        action = {"tool": "file_carrier_fault", "ticket_id": "T-001", "order_id": "O-1001",
                  "parcel_id": "O-1001-P1", "carrier_id": "GHSH", "delay_days": 99}
        self.assertEqual(guards.write_gate(ctx, action).action, "deny")

    def test_non_refund_writes_reject_mismatched_ticket_id(self):
        ctx = self.context("T-001")
        fault = {"tool": "file_carrier_fault", "ticket_id": "T-OTHER", "order_id": "O-1001",
                 "parcel_id": "O-1001-P1", "carrier_id": "GHSH", "delay_days": 4}
        self.assertEqual(guards.write_gate(ctx, fault).action, "deny")

        ctx = self.context("T-001")
        notice = {"tool": "notify_carrier", "ticket_id": "T-OTHER", "carrier_id": "GHSH",
                  "payload": {"order_id": "O-1001", "parcel_id": "O-1001-P1"}}
        self.assertEqual(guards.write_gate(ctx, notice).action, "deny")

        ctx = self.context("T-001")
        reply = {"tool": "send_reply", "ticket_id": "T-OTHER", "customer_id": "C-01", "text": "Đã nhận yêu cầu"}
        self.assertEqual(guards.write_gate(ctx, reply).action, "deny")

    def test_carrier_notice_is_minimized_from_verified_facts(self):
        ctx = self.context("T-001")
        action = {"tool": "notify_carrier", "ticket_id": "T-001", "carrier_id": "GHSH", "payload": {
            "order_id": "O-1001", "parcel_id": "O-1001-P1", "district": "Cầu Giấy",
            "delay_days": 99, "customer_note": "My phone is 0903110201",
            "recipient_contact": {"phone": "0903110201"}}}
        v = guards.write_gate(ctx, action)
        self.assertEqual(v.action, "modify")
        self.assertEqual(set(v.changes["payload"]), {"order_id", "parcel_id", "district", "delay_days"})
        self.assertNotIn("customer_note", v.changes["payload"])
        self.assertEqual(v.changes["payload"]["delay_days"], 4)

    def test_reply_redacts_contact_details_and_rejects_wrong_recipient(self):
        ctx = self.context("T-001")
        v = guards.write_gate(ctx, {"tool": "send_reply", "ticket_id": "T-001", "customer_id": "C-01",
                                    "text": "Gọi 0903110201 hoặc a@example.com, Nguyễn Minh Anh"})
        self.assertEqual(v.action, "modify")
        self.assertNotIn("0903110201", v.changes["text"])
        self.assertNotIn("a@example.com", v.changes["text"])
        self.assertNotIn("Nguyễn Minh Anh", v.changes["text"])
        ctx = self.context("T-001")
        self.assertEqual(guards.write_gate(ctx, {"tool": "send_reply", "ticket_id": "T-001", "customer_id": "C-02",
                                                  "text": "Xin chào"}).action, "deny")


if __name__ == "__main__":
    unittest.main()
