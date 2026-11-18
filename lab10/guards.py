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
MAX_REFUND_PER_ORDER_VND = 2_000_000


def _as_of_date(ctx):
    """Return the first valid ISO date from the context or trusted tools."""
    for value in (getattr(ctx, "as_of", None), getattr(ctx.tools, "as_of", None)):
        try:
            return H.d(value).isoformat()
        except (TypeError, ValueError):
            continue
    return None


def _effective_policy(ctx):
    as_of = _as_of_date(ctx)
    if as_of is None:
        return None
    try:
        return H.effective_policy(ctx.tools.lookup_policies(), as_of)
    except (KeyError, TypeError, ValueError):
        return None


def _order(ctx, order_id):
    try:
        return ctx.tools.lookup_order(order_id)
    except (KeyError, TypeError, ValueError):
        return None


def _ticket_parcel(order, ctx):
    """Resolve the parcel named by the ticket, or the tracked worst-delay parcel."""
    if not isinstance(order, dict):
        return None
    parcels = order.get("parcels")
    if not isinstance(parcels, list) or not parcels:
        return None
    ticket_parcel_id = ctx.ticket.get("parcel_id")
    if ticket_parcel_id is not None:
        if not isinstance(ticket_parcel_id, str) or not ticket_parcel_id:
            return None
        return next((p for p in parcels if p.get("parcel_id") == ticket_parcel_id), None)
    as_of = _as_of_date(ctx)
    if as_of is None:
        return None
    try:
        parcel = H.ticket_parcel(order, ctx.ticket, as_of)
        return parcel if isinstance(parcel, dict) and parcel.get("parcel_id") else None
    except (KeyError, TypeError, ValueError):
        return None


def _parcel(order, action_parcel_id, ctx):
    """Return the ticket's canonical parcel and whether the action named another parcel."""
    parcel = _ticket_parcel(order, ctx)
    if parcel is None:
        return None, False
    if action_parcel_id is not None and action_parcel_id != parcel["parcel_id"]:
        return parcel, True
    return parcel, False


def _entitlement(ctx, order, parcel, policy):
    """Compute policy entitlement from official tracking only; None means unverifiable."""
    try:
        as_of = _as_of_date(ctx)
        if as_of is None:
            return None, None
        if not parcel.get("promised_date"):
            return None, None
        delay = H.db_delay_days(parcel, as_of)
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
    if amount > MAX_REFUND_PER_ORDER_VND:
        ctx.log("refund_hard_cap_exceeded", amount_vnd=amount,
                cap_vnd=MAX_REFUND_PER_ORDER_VND, scope="per_order")
        return Verdict.deny("số tiền hoàn vượt hard cap 2.000.000 VND mỗi đơn hàng")

    ticket_id = action.get("ticket_id")
    order_id = action.get("order_id")
    if ticket_id != ctx.ticket.get("ticket_id") or order_id != ctx.ticket.get("order_id"):
        ctx.log("refund_context_mismatch")
        return Verdict.escalate("đơn hoặc phiếu không khớp yêu cầu ban đầu")

    order = _order(ctx, order_id)
    policy = _effective_policy(ctx)
    parcel, parcel_mismatch = _parcel(order, action.get("parcel_id"), ctx)
    if parcel_mismatch:
        ctx.log("refund_parcel_mismatch", supplied_parcel_id=action.get("parcel_id"),
                expected_parcel_id=parcel.get("parcel_id"))
        return Verdict.deny("kiện hàng trong lệnh hoàn không khớp kiện của ticket")
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
        as_of = _as_of_date(ctx)
        if as_of is None:
            ctx.log("approval_date_unverifiable")
            return Verdict.escalate("không xác minh được ngày để kiểm tra hạn phê duyệt")
        try:
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id) if approval_id else []
        except (KeyError, TypeError, ValueError):
            approvals = []
        for approval in approvals:
            try:
                expiry = H.d(approval.get("expires_at"))
            except (AttributeError, TypeError, ValueError):
                continue
            if (approval.get("ticket_id") == ticket_id and approval.get("order_id") == order_id
                    and approval.get("customer_id") == order.get("customer_id")
                    and approval.get("status") == "valid" and expiry >= H.d(as_of)
                    and isinstance(approval.get("max_vnd"), int)
                    and not isinstance(approval.get("max_vnd"), bool)
                    and approval["max_vnd"] >= amount):
                approval_valid = True
                break
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
    order_total = sum(r.get("amount_vnd", 0) for r in today_rows if r.get("order_id") == order_id)
    if order_total + amount > MAX_REFUND_PER_ORDER_VND:
        ctx.log("refund_order_hard_cap_exceeded", order_id=order_id, prior_refund_vnd=order_total,
                amount_vnd=amount, cap_vnd=MAX_REFUND_PER_ORDER_VND)
        return Verdict.deny("tổng tiền hoàn cho đơn hàng sẽ vượt hard cap 2.000.000 VND")
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
    parcel, parcel_mismatch = _parcel(order, action.get("parcel_id"), ctx)
    if parcel_mismatch:
        ctx.log("fault_parcel_mismatch", supplied_parcel_id=action.get("parcel_id"),
                expected_parcel_id=parcel.get("parcel_id"))
        return Verdict.deny("kiện hàng trong lỗi hãng không khớp kiện của ticket")
    if (action.get("ticket_id") != ctx.ticket.get("ticket_id") or
            not order or order_id != ctx.ticket.get("order_id") or not policy or not parcel or
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
    source = action.get("payload")
    if not isinstance(source, dict):
        ctx.log("carrier_notice_payload_invalid")
        return Verdict.deny("nội dung thông báo hãng không hợp lệ")
    parcel, parcel_mismatch = _parcel(order, source.get("parcel_id"), ctx)
    if parcel_mismatch:
        ctx.log("carrier_notice_parcel_mismatch", supplied_parcel_id=source.get("parcel_id"),
                expected_parcel_id=parcel.get("parcel_id"))
        return Verdict.deny("kiện hàng trong thông báo không khớp kiện của ticket")
    if (action.get("ticket_id") != ctx.ticket.get("ticket_id") or
            not order or not policy or not parcel or
            order.get("customer_id") != ctx.ticket.get("customer_id") or
            action.get("carrier_id") != parcel.get("carrier_id")):
        ctx.log("carrier_notice_recipient_invalid")
        return Verdict.deny("người nhận hoặc kiện hàng không khớp dữ liệu đã xác minh")

    allowed = set(policy.get("carrier_notice_fields", ()))
    # Rebuild from canonical facts. Never forward ticket text or recipient details.
    as_of = _as_of_date(ctx)
    if as_of is None:
        ctx.log("carrier_notice_date_unverifiable")
        return Verdict.deny("không xác minh được ngày tracking cho thông báo hãng")
    delay = H.db_delay_days(parcel, as_of)
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
    if (action.get("ticket_id") != ctx.ticket.get("ticket_id") or
            not order or order.get("customer_id") != ctx.ticket.get("customer_id") or
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
