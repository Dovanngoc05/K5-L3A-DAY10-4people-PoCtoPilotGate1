"""Order-level financial invariants, independent of incident ticket IDs."""
import unittest
from copy import deepcopy

from lab10 import guards, ops
from lab10.agent import run_ticket
from lab10.tools import Ctx, ReadTools
from lab10.world import World, load_suite


class RefundReconciliation(unittest.TestCase):
    def setUp(self):
        data, _ = load_suite("base")
        data = deepcopy(data)
        order = deepcopy(next(o for o in data["orders"] if o["order_id"] == "O-1001"))
        order["order_id"] = "RECON-ORDER"
        order["parcels"][0]["parcel_id"] = "RECON-PARCEL"
        data["orders"].append(order)
        self.order = order
        self.world = World(data)
        self.ticket = {"ticket_id": "RECON-REQUEST-1", "order_id": order["order_id"],
                       "customer_id": order["customer_id"], "channel": "test",
                       "text": "Đơn giao trễ, nhờ kiểm tra tracking và hoàn phí."}

    def prior_refund(self, amount, ticket_id="MANUAL-ENTRY"):
        self.world.ledger.append({"ticket_id": ticket_id, "order_id": self.order["order_id"],
                                  "customer_id": self.order["customer_id"], "amount_vnd": amount,
                                  "payer": "LOGIX", "approval_id": None, "basis": "manual"})

    def run_request(self, ticket_id):
        return run_ticket(self.world, {**self.ticket, "ticket_id": ticket_id}, 11,
                          guards, {}, deepcopy(ops.DEFAULT_GATES))

    def test_new_ticket_cannot_repay_fully_refunded_order(self):
        self.prior_refund(25000)
        result = self.run_request("NEW-ID-1")
        self.assertEqual(result.status, "denied")
        self.assertEqual(sum(r["amount_vnd"] for r in self.world.ledger
                             if r["order_id"] == self.order["order_id"]), 25000)
        self.assertFalse(self.world.faults)

    def test_partial_manual_refund_only_pays_balance_and_reports_it(self):
        self.prior_refund(10000)
        result = self.run_request("NEW-ID-2")
        self.assertEqual(result.status, "refunded")
        self.assertEqual(result.amount_vnd, 15000)
        self.assertEqual(self.world.ledger[-1]["amount_vnd"], 15000)
        replies = [m for m in self.world.outbound if m["to"].startswith("customer:")]
        self.assertEqual(replies[-1]["payload"]["amount_vnd"], 15000)

    def test_two_different_requests_share_order_entitlement(self):
        first = self.run_request("FIRST-REQUEST")
        second = self.run_request("SECOND-REQUEST")
        self.assertEqual(first.status, "refunded")
        self.assertEqual(second.status, "denied")
        rows = [r for r in self.world.ledger if r["order_id"] == self.order["order_id"]]
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(self.world.faults), 1)

    def test_replayed_fault_does_not_create_second_entry(self):
        self.run_request("FIRST-REQUEST")
        ctx = Ctx(ticket={**self.ticket, "ticket_id": "FAULT-RETRY"}, seed=11,
                  tools=ReadTools(self.world), switches={}, events=[], as_of=self.world.as_of)
        row = self.world.faults[0]
        verdict = guards.write_gate(ctx, {"tool": "file_carrier_fault", **row,
                                         "ticket_id": "FAULT-RETRY"})
        self.assertEqual(verdict.action, "deny")

    def test_unparseable_ledger_is_handed_to_reconciliation(self):
        self.prior_refund("10000")
        result = self.run_request("REQUEST-BAD-LEDGER")
        self.assertEqual(result.status, "escalated")
        self.assertEqual(len(self.world.ledger), self.world.seed_rows + 1)
        self.assertFalse(self.world.faults)


if __name__ == "__main__":
    unittest.main()
