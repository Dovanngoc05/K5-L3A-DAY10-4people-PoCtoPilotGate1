"""System-level safety gates for the refund agent.

The agent's proposal and the customer's message are untrusted. Decisions here use
the order, parcel tracking, effective policy, approvals, and operating limits read
through ``ctx.tools``. Keep these checks before the corresponding write: refunds
are recorded before carrier faults and notifications are attempted.
"""
from __future__ import annotations

import re

from . import helpers as H
from .tools import Verdict


_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){8,}\d(?!\w)")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")


def _effective_policy(ctx):
    try:
        return H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of or ctx.tools.as_of)
    except (KeyError, TypeError, ValueError):
        return None


def _order(ctx, order_id):
    try:
        return ctx.tools.lookup_order(order_id)
    except (KeyError, TypeError, ValueError):
        return None


def _parcel(order, parcel_id, ctx):
    parcels = order.get("parcels")
    if not isinstance(parcels, list) or not parcels:
        return None
    if parcel_id:
        return next((p for p in parcels if p.get("parcel_id") == parcel_id), None)
    try:
        return H.ticket_parcel(order, ctx.ticket, ctx.as_of or ctx.tools.as_of)
    except (KeyError, TypeError, ValueError):
        return None


def _entitlement(ctx, order, parcel, policy):
    """Compute policy entitlement from official tracking only; None means unverifiable."""
    try:
        if not parcel.get("promised_date"):
            return None, None
        delay = H.db_delay_days(parcel, ctx.as_of or ctx.tools.as_of)
        cause = parcel.get("delay_cause")
        if delay > 0 and not cause:
            return None, delay
        return H.entitlement_vnd(policy, order, delay, cause), delay
    except (KeyError, TypeError, ValueError):
        return None, None


def pre_guard(ctx):
    """Pin the policy effective today before the agent reads untrusted text."""
    policy = _effective_policy(ctx)
    if policy is None:
        ctx.log("policy_unavailable")
        return Verdict.escalate("không xác minh được chính sách có hiệu lực; cần người duyệt")
    return Verdict.allow(policy_id=policy["policy_id"])


def _refund_gate(ctx, action):
    amount = action.get("amount_vnd")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        ctx.log("refund_amount_invalid")
        return Verdict.deny("số tiền hoàn không phải số nguyên dương hợp lệ")

    ticket_id = action.get("ticket_id")
    order_id = action.get("order_id")
    if ticket_id != ctx.ticket.get("ticket_id") or order_id != ctx.ticket.get("order_id"):
        ctx.log("refund_context_mismatch")
        return Verdict.escalate("đơn hoặc phiếu không khớp yêu cầu ban đầu")

    order = _order(ctx, order_id)
    policy = _effective_policy(ctx)
    parcel = _parcel(order, action.get("parcel_id"), ctx) if order else None
    if (not order or not policy or not parcel or
            order.get("customer_id") != ctx.ticket.get("customer_id")):
        ctx.log("refund_facts_unverifiable")
        return Verdict.escalate("không xác minh đủ chủ đơn, tracking hoặc chính sách")

    entitled, delay = _entitlement(ctx, order, parcel, policy)
    if entitled is None:
        ctx.log("refund_evidence_unverifiable")
        return Verdict.escalate("tracking thiếu hoặc không hợp lệ; cần người xác minh")
    if amount > entitled:
        ctx.log("refund_over_entitlement", amount_vnd=amount, entitled_vnd=entitled)
        return Verdict.deny("số tiền yêu cầu vượt quyền lợi tính từ tracking và chính sách")
    if entitled <= 0:
        ctx.log("refund_without_entitlement")
        return Verdict.deny("tracking và chính sách không xác nhận quyền được hoàn")

    payer = action.get("payer")
    if payer != "LOGIX":
        ctx.log("refund_payer_unapproved")
        return Verdict.deny("bên trả tiền không được chính sách ủy quyền")

    approval_id = action.get("approval_id")
    approval_valid = False
    if approval_id or amount > policy["auto_limit_vnd"]:
        try:
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id) if approval_id else []
        except (KeyError, TypeError, ValueError):
            approvals = []
        approval_valid = any(a.get("ticket_id") == ticket_id and a.get("order_id") == order_id
                             and a.get("customer_id") == order.get("customer_id")
                             and a.get("status") == "valid" and a.get("expires_at", "") >= ctx.as_of
                             and isinstance(a.get("max_vnd"), int) and not isinstance(a.get("max_vnd"), bool)
                             and a["max_vnd"] >= amount
                             for a in approvals)
        if not approval_valid:
            ctx.log("refund_approval_invalid")
            return Verdict.escalate("khoản hoàn vượt hạn mức tự động hoặc thiếu phê duyệt hợp lệ")

    # Apply the finance ceilings from the source-of-truth limits, not request data.
    try:
        limits = ctx.tools.ops_limits()
        customer_rows = ctx.tools.ledger_rows(customer_id=order["customer_id"])
        today_rows = ctx.tools.ledger_rows()
    except (KeyError, TypeError, ValueError):
        ctx.log("refund_limits_unavailable")
        return Verdict.escalate("không xác minh được hạn mức vận hành")
    if not approval_valid:
        customer_cap = limits.get("max_auto_refund_per_customer_per_day_vnd")
        customer_total = sum(r.get("amount_vnd", 0) for r in customer_rows
                             if not r.get("approval_id"))
        daily_cap = limits.get("daily_auto_refund_budget_vnd")
        daily_total = ctx.tools.auto_refund_today_vnd()
        if ((isinstance(customer_cap, int) and customer_total + amount > customer_cap) or
                (isinstance(daily_cap, int) and daily_total + amount > daily_cap)):
            ctx.log("refund_operating_limit", amount_vnd=amount)
            return Verdict.escalate("vượt hạn mức hoàn tự động; chuyển người duyệt")

    # Do not replay a successful write after an uncertain model confirmation.
    if any(r.get("ticket_id") == ticket_id for r in today_rows):
        ctx.log("refund_duplicate_write")
        return Verdict.deny("phiếu này đã có khoản hoàn trong sổ cái")
    return Verdict.allow()


def _fault_gate(ctx, action):
    order_id = action.get("order_id")
    order = _order(ctx, order_id)
    policy = _effective_policy(ctx)
    parcel = _parcel(order, action.get("parcel_id"), ctx) if order else None
    if (not order or order_id != ctx.ticket.get("order_id") or not policy or not parcel or
            order.get("customer_id") != ctx.ticket.get("customer_id")):
        ctx.log("fault_facts_unverifiable")
        return Verdict.deny("không đủ dữ liệu tracking để ghi lỗi hãng")
    _, actual_delay = _entitlement(ctx, order, parcel, policy)
    cause = parcel.get("delay_cause")
    if (actual_delay is None or actual_delay < policy["late"]["min_days_fee"] or
            cause not in policy["fault_causes"] or
            action.get("carrier_id") != parcel.get("carrier_id") or
            action.get("delay_days") != actual_delay):
        ctx.log("fault_evidence_insufficient")
        return Verdict.deny("tracking không đủ căn cứ xác nhận lỗi hãng hoặc tham số không khớp")
    return Verdict.allow()


def _carrier_notice(ctx, action):
    order = _order(ctx, ctx.ticket.get("order_id"))
    policy = _effective_policy(ctx)
    parcel = _parcel(order, action.get("payload", {}).get("parcel_id"), ctx) if order else None
    if (not order or not policy or not parcel or
            order.get("customer_id") != ctx.ticket.get("customer_id") or
            action.get("carrier_id") != parcel.get("carrier_id")):
        ctx.log("carrier_notice_recipient_invalid")
        return Verdict.deny("người nhận hoặc kiện hàng không khớp dữ liệu đã xác minh")

    allowed = set(policy.get("carrier_notice_fields", ()))
    source = action.get("payload")
    if not isinstance(source, dict):
        return Verdict.deny("nội dung thông báo hãng không hợp lệ")
    # Rebuild from canonical facts. Never forward ticket text or recipient details.
    delay = H.db_delay_days(parcel, ctx.as_of or ctx.tools.as_of)
    canonical = {"order_id": order["order_id"], "parcel_id": parcel["parcel_id"],
                 "district": order.get("recipient", {}).get("district"), "delay_days": delay}
    minimized = {k: v for k, v in canonical.items() if k in allowed and v is not None}
    if not minimized:
        ctx.log("carrier_notice_no_allowed_fields")
        return Verdict.deny("chính sách không cho phép trường thông báo cần thiết")
    ctx.log("carrier_notice_minimized", removed_fields=sorted(set(source) - set(minimized)))
    return Verdict.modify("chỉ gửi dữ liệu vận hành tối thiểu đã xác minh", payload=minimized)


def _customer_reply(ctx, action):
    order = _order(ctx, ctx.ticket.get("order_id"))
    if (not order or order.get("customer_id") != ctx.ticket.get("customer_id") or
            action.get("customer_id") != order.get("customer_id")):
        ctx.log("reply_recipient_invalid")
        return Verdict.deny("người nhận trả lời không khớp chủ đơn")
    text = action.get("text")
    if not isinstance(text, str):
        return Verdict.deny("nội dung trả lời không hợp lệ")
    safe = _EMAIL.sub("[đã ẩn]", _PHONE.sub("[đã ẩn]", text))
    try:
        customer = ctx.tools.lookup_customer(order["customer_id"]) or {}
    except (KeyError, TypeError, ValueError):
        customer = {}
    pii_values = {customer.get(k) for k in ("name", "phone", "street")}
    pii_values.update({(order.get("recipient") or {}).get(k) for k in ("name", "phone", "street")})
    for value in sorted((v for v in pii_values if isinstance(v, str) and len(v.strip()) >= 4),
                        key=len, reverse=True):
        safe = re.sub(re.escape(value), "[đã ẩn]", safe, flags=re.IGNORECASE)
    if safe != text:
        ctx.log("reply_pii_redacted")
        return Verdict.modify("đã ẩn thông tin liên hệ không cần thiết", text=safe)
    return Verdict.allow()


def write_gate(ctx, action):
    """Validate each write before it reaches the mutable tools."""
    try:
        tool = action.get("tool")
        if tool == "issue_refund":
            return _refund_gate(ctx, action)
        if tool == "file_carrier_fault":
            return _fault_gate(ctx, action)
        if tool == "notify_carrier":
            return _carrier_notice(ctx, action)
        if tool == "send_reply":
            return _customer_reply(ctx, action)
        ctx.log("unknown_write_tool")
        return Verdict.deny("thao tác ghi không được nhận diện")
    except Exception as exc:
        # A broken guard check must never turn a risky write into an allow.
        ctx.log("guard_check_failed", tool=action.get("tool"), error_type=type(exc).__name__)
        return Verdict.escalate("lỗi khi xác minh điều kiện an toàn; cần người duyệt")
