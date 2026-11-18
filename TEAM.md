# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): `4people`
- Lớp: `L3A`
- Repo của bàn: `K5-L3A-DAY10-4people-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8):

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

Gốc tích hợp TV1: `23b6213`; commit ký: `d355eb9`. Lần đo: `R-base-before-20261118-160903-aca5cb`; report và trace sao lưu ở `docs/tv3-evidence/`. Phiếu A A2, Phiếu B B0–B2/B7.3; kế hoạch bàn giao ở `docs/tv3-preparation.md`. B7.3 chưa chạy, prepared và monitor chờ các mốc tương ứng.

### Exit ticket

Chưa điền — Đoàn Nhật Anh tự ghi điều học được và điều còn chưa chắc trước khi nộp.
