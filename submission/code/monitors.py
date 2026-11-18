"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


from .world import ROOT, load_json


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def max_warehouse_processing_cost_upper_bound_vnd(trials):
    """Worst warehouse mean of agent cost plus full-price human reviews.

    Uses no outcome labels. Each recheck is conservatively charged as a full
    review because monitor_view does not expose review_units. Excludes standby
    fees and refund losses: this is a processing-cost signal, not total ROI.
    Unknown warehouses remain visible in their own group. Empty input = 0.
    """
    review_cost = load_json(ROOT / "data" / "world.json")["ops_facts"]["review_cost_per_ticket_vnd"]
    groups = {}
    for trial in trials:
        warehouse = trial.get("warehouse") or "?"
        total, count = groups.get(warehouse, (0, 0))
        human = review_cost if trial.get("review_kind") else 0
        groups[warehouse] = (total + trial.get("cost_vnd", 0) + human, count + 1)
    return max((total / count for total, count in groups.values()), default=0)


def cost_budget_handoff_rate(trials):
    """Share of trials stopped by the cost budget, including prevented overruns."""
    return sum(any(event.get("type") == "business_gate"
                   and event.get("gate") == "cost_budget_per_ticket_vnd"
                   for event in trial.get("events", []))
               for trial in trials) / max(1, len(trials))


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "max_warehouse_processing_cost_upper_bound_vnd": max_warehouse_processing_cost_upper_bound_vnd,
    "cost_budget_handoff_rate": cost_budget_handoff_rate,
}
STARTER_MONITORS = ("escalation_rate",)
