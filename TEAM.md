# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): `4people`
- Lớp: `L3A`
- Repo của bàn: `K5-L3A-DAY10-4people-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): `S5`

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 |Đỗ Văn Ngọc|2A202603391|Sản phẩm và kinh doanh|Trưởng nhóm|
|   2 |Đoàn Nhật Anh|2A202603408|Kỹ sư cổng — đánh giá và giám sát||
|   3 |Nguyễn Hữu Đức|2A202603429|Vận hành và pháp lý| |
|   4 |Lê Đoàn Dương|2A202603372|Kỹ sư cổng — xây dựng cổng bảo vệ||

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## HoVaTen-MSSV

### Phần việc phụ trách

Vai trong bàn; câu nào của đề, mục nào của phiếu A/B/C, file nào (`lab10/guards.py`, `config/operating_gates.json`, …).

### Đóng góp cụ thể

...

### Bằng chứng

Mã commit, mã lần chạy (`runs/<mã>`), dòng trong phiếu.

### Exit ticket

Một điều học được, một điều còn chưa chắc.

## DoanNhatAnh-2A202603408

### Phần việc phụ trách

TV3 — Kỹ sư cổng, đánh giá và giám sát: xác nhận metric offline A2 câu 1.3; baseline và trace B0–B2; tình huống thử B7.3; sau khi nhóm chốt mới đo prepared, sau khi có thẻ mới làm C0–C2 và C8.

### Đóng góp cụ thể

Đối chiếu metric TV1 với trường dữ liệu thật; đo lại baseline sau commit ký đã lên origin/main; phân tích hai tác hại hoàn sai và ghi lỗi hãng oan trong T-002@55. Soạn hai ticket thử cùng trạng thái đầu vào để kiểm tra tính bất biến khi khách phóng đại số ngày giao trễ. Dùng Codex hỗ trợ đọc code, soạn tài liệu, chạy lệnh và phân tích trace; thành viên cần kiểm tra và giải thích kết quả khi demo.

### Bằng chứng

Gốc tích hợp TV1: `23b6213`; commit ký: `d355eb9`. Baseline: `R-base-before-20261118-160903-aca5cb`; sau tích hợp cổng TV2 `58e9fa2`: `R-base-after-20261118-172000-182fc8` (65 trial, coverage 59,09%). B7.3 đã chạy hai ticket, không hoàn sai/ghi lỗi oan; 35/35 test đạt. Report, gate, journal và trace sao lưu ở `docs/tv3-evidence/`. Phiếu A A2, Phiếu B B0–B2/B7.3; kế hoạch bàn giao ở `docs/tv3-preparation.md`. Prepared và monitor chờ các mốc tương ứng.

### Exit ticket

Chưa điền — Đoàn Nhật Anh tự ghi điều học được và điều còn chưa chắc trước khi nộp.

### Cập nhật S5

Cập nhật sau yêu cầu sửa nghiệp vụ: đã bổ sung đối soát ledger theo order, hoàn phần quyền lợi còn lại và chống ghi lỗi hãng lặp; 40 test đạt. Grade `R-S5-grade-20261118-173308-883400` đạt visible/criteria/regression/monitor; S5 50/50, hoàn sai/lỗi hãng oan về 0, ROI +0,52, coverage vẫn 33,33%. Chẩn đoán đủ 150 trial ngoài phạm vi chỉ để kiểm logic cũng đạt. Integrity còn thiếu 28 file thẻ khác; chưa tự sửa grader hoặc lấy thẻ ngoài phân công. Chi tiết mới nhất ở `docs/s5-fix-report.md`; đoạn bên dưới ghi lại trạng thái trước bản sửa này.

Đã chạy grade đầu trước thay đổi theo thẻ, phân tích ba nguồn tác hại và điền C0–C2/C8. Thêm `max_warehouse_processing_cost_upper_bound_vnd` và `cost_budget_handoff_rate` trong monitors.py, không dùng nhãn chấm. Grade `R-S5-grade-20261118-172739-a2b82f` xác nhận monitor/regression đạt, 35 test đạt; còn 350.000đ hoàn sai, 15 lỗi hãng oan và ROI -0,55, chưa tuyên bố sự cố đã sửa. Chi tiết và công việc bàn giao ở `docs/tv3-s5-handover.md`. Integrity còn thiếu 28 file thẻ khác sau khi khôi phục đúng LF của 23 file hiện có; chờ hướng dẫn Coach. Chưa commit/push phần tích hợp và S5 do lần cấp quyền commit merge trước bị từ chối.

Cập nhật TV3 sau tích hợp TV4: config `a065538` đã kết hợp với cổng TV2, 35 test đạt. Prepared `R-base-prepared-20261118-172442-6b6da8`: 65/65 đạt, coverage 59,09%, 5.550đ/ticket, ROI 0,80, 0 ùn, không vi phạm an toàn. Checkpoint `300f9086` đã tạo và verify đạt; chờ nhóm chốt v1 và commit/push mốc vòng 1 trước khi đo S5. Chưa hoàn tất commit merge do yêu cầu cấp quyền bị từ chối.
