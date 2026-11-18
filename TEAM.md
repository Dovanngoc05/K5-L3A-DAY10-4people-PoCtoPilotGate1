# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng):
- Lớp: `L3A` / `L3B`
- Repo của bàn: `K5-<L3A|L3B>-DAY10-<TenNhom>-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8):

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Lê Đoàn Dương | 2A202603372 | Kỹ sư cổng |             |
|   2 |           |      |     |             |
|   3 |           |      |     |             |
|   4 |           |      |     |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## LeDoanDuong-2A202603372

### Phần việc phụ trách

TV2 – Kỹ sư cổng (B7.1–B7.2; phần kỹ thuật C5–C7, C9 và demo). Phụ trách `lab10/guards.py`, `tests/test_guards.py` và tài liệu kỹ thuật TV2 trong `docs/guard-tv2-report.md`.

### Đóng góp cụ thể

- Bổ sung kiểm tra refund, ticket identity, parcel binding, approval expiry, căn cứ carrier fault, giảm thiểu dữ liệu trong carrier notice và lọc PII trong customer reply.
- Bổ sung regression tests cho hard cap 2.000.000 VND/order, parcel không khớp, approval hết hạn/ngày fallback và các luồng hợp lệ.
- Tổng hợp specification, RCA trước/sau sửa, remediation, kịch bản demo và giới hạn tích hợp Agent–Guard trong báo cáo TV2.

### Bằng chứng

- Commit liên quan: `937e234`, `03983b0`, `4ef1272`, `56a7d55`, `58e9fa2`.
- Kiểm tra trên source Guard `58e9fa2` cùng regression tests TV2 hiện tại: `python3 -m unittest discover -s tests -v` — 39 tests PASS; `python3 -m lab10.criteria verify` — `ok: true`; `git diff --check` — PASS.
- Báo cáo kỹ thuật: `docs/guard-tv2-report.md`. Chưa có incident card S1–S8 để ghi run ID hoặc kết quả incident-specific.

### Exit ticket

Tôi học được rằng Guard phải xác minh dữ liệu nguồn tại từng ranh giới ghi, thay vì tin các trường Agent tự gửi. Tôi còn muốn xác nhận luồng chọn parcel của Agent được đồng bộ với parcel canonical của Guard cho đơn có nhiều parcel.

### Sử dụng AI

Có sử dụng AI để rà soát logic, đề xuất và viết regression tests, tổng hợp Git history, cùng soạn tài liệu kỹ thuật. Tôi đã kiểm tra lại thay đổi qua code, test suite và criteria verification; không dùng AI để ký tiêu chí, tạo kết quả evaluation hoặc quyết định pilot.
