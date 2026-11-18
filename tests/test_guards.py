"""Focused tests for the TV2 system-level write gates."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lab10 import guards, ops  # noqa: E402
from lab10.tools import Ctx, ReadTools  # noqa: E402
from lab10.world import World, load_suite  # noqa: E402


class GuardChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.tickets = load_suite("base")
        cls.by_id = {t["ticket_id"]: t for t in cls.tickets}

    def context(self, ticket_id):
        world = World(self.data)
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

    def test_carrier_fault_requires_canonical_delay_and_cause(self):
        ctx = self.context("T-001")
        action = {"tool": "file_carrier_fault", "ticket_id": "T-001", "order_id": "O-1001",
                  "parcel_id": "O-1001-P1", "carrier_id": "GHSH", "delay_days": 99}
        self.assertEqual(guards.write_gate(ctx, action).action, "deny")

    def test_carrier_notice_is_minimized_from_verified_facts(self):
        ctx = self.context("T-001")
        action = {"tool": "notify_carrier", "carrier_id": "GHSH", "payload": {
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
        v = guards.write_gate(ctx, {"tool": "send_reply", "customer_id": "C-01",
                                    "text": "Gọi 0903110201 hoặc a@example.com, Nguyễn Minh Anh"})
        self.assertEqual(v.action, "modify")
        self.assertNotIn("0903110201", v.changes["text"])
        self.assertNotIn("a@example.com", v.changes["text"])
        self.assertNotIn("Nguyễn Minh Anh", v.changes["text"])
        ctx = self.context("T-001")
        self.assertEqual(guards.write_gate(ctx, {"tool": "send_reply", "customer_id": "C-02",
                                                  "text": "Xin chào"}).action, "deny")


if __name__ == "__main__":
    unittest.main()
