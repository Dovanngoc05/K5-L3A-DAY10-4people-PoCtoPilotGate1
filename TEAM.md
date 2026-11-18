# Team — 4people

- Nhóm: `4people`; lớp: `L3A`.
- Repo: `K5-L3A-DAY10-4people-PoCtoPilotGate1`.
- Thẻ được giao và phân tích: **S5**. Các gói còn lại chỉ được bổ sung để kiểm hash/đóng gói theo yêu cầu của người dùng, không phân tích để làm bài.

## Thành viên

| Họ tên | MSSV | Vai | Trưởng nhóm |
|---|---|---|---|
| Đỗ Văn Ngọc | 2A202603391 | Trưởng nhóm · Sản phẩm và kinh doanh | Có |
| Đoàn Nhật Anh | 2A202603408 | Kỹ sư cổng · Đánh giá và giám sát |  |
| Nguyễn Hữu Đức | 2A202603429 | Vận hành và pháp lý |  |
| Lê Đoàn Dương | 2A202603372 | Kỹ sư cổng · Xây dựng cổng bảo vệ |  |

## Trạng thái hồ sơ chung

Tiêu chí ký tại d355eb9, hash ce7ab3b6; checkpoint 300f9086 giữ nguyên. Grade cuối `R-S5-grade-20261118-184018-883400`: PASS-VISIBLE, integrity/criteria/visible/regression/monitor đạt, chưa có test ẩn. S5 trong phạm vi HN/HCM: 50/50, coverage 33,33%, không hoàn sai/lỗi oan/PII, chi phí 6.564đ/ticket, ROI +0,52. 40 test đạt.

**Tính xác thực:** checkpoint được tạo sau khi tải gói S5 nhưng trước khi đọc/phân tích; B6/v1 chưa có bản hoàn chỉnh được lưu trước sự cố, nên ghi rõ tổng hợp hồi cứu. Không tạo chữ ký hoặc đổi lịch sử. Các đoạn tự nhận xét bên dưới là gợi ý tổng kết từ bằng chứng, cần từng thành viên đọc, sửa và xác nhận trước khi nộp LMS; không phải lời xác nhận cá nhân đã được thu thập.

**Dùng AI:** Codex được dùng để đọc code, chuẩn bị/chỉnh tài liệu, chạy công cụ, tích hợp nhánh, viết monitor, sửa nghiệp vụ S5 và gom bài. Mỗi thành viên cần xác nhận phạm vi dùng AI của mình; tên vai và nhánh là bằng chứng phân công, không chứng minh ai tự gõ toàn bộ code khi Git dùng danh tính chung.

## DoVanNgoc-2A202603391

### Phần việc phụ trách

Phiếu A, bản tiêu chí, business config, quyết định và tích hợp repo.

### Đóng góp cụ thể

Theo nhánh TV1 và hồ sơ ký: điền tiêu chí và cấu hình kinh doanh; ủy quyền tiếp nhận các nhánh và hoàn thiện hồ sơ. Không suy từ danh tính Git chung ra ai tự gõ từng dòng.

### Bằng chứng

d355eb9; 752a903; 23b6213; config/acceptance_criteria.json và Phiếu A.

### Exit ticket

Đề xuất tự nhận xét: chi phí/ticket thấp hơn làm tay chưa đủ chứng minh ROI dương khi còn tiền mất; cần xác minh số liệu và quyền mở pilot thật.

## DoanNhatAnh-2A202603408

### Phần việc phụ trách

Metric A2, B0–B2/B7.3, C0–C2/C8, monitor, report và tích hợp kiểm thử.

### Đóng góp cụ thể

Chạy baseline/trace, soạn behavioral test, tích hợp TV2/TV4; dùng Codex bổ sung monitor, sửa đối soát ledger và lỗi hãng lặp theo yêu cầu, kiểm hash và gom hồ sơ.

### Bằng chứng

24a3e39; 56acf17; 689653c; R-S5-grade-20261118-184018-883400; docs/tv3-evidence/.

### Exit ticket

Đề xuất tự nhận xét: phải so cùng phạm vi và tách phát hiện khỏi ngăn tác hại; 40 test và PASS-VISIBLE chưa chứng minh an toàn khi hai worker ghi đồng thời.

## NguyenHuuDuc-2A202603429

### Phần việc phụ trách

B4/B5/B7.5/B7.6, config operations/legal, runbook, rủi ro và bài nộp.

### Đóng góp cụ thể

Theo nhánh NguyenHuuDuc: hoàn thiện HAZOP/checklist, kế hoạch một người duyệt, trần chờ, điều kiện dừng và PII. Bản tổng hợp cuối cập nhật C10/C11 dựa trên report chung.

### Bằng chứng

a065538 trên nhánh NguyenHuuDuc; config/operating_gates.json; Phiếu B và C10/C11.

### Exit ticket

Đề xuất tự nhận xét: công suất, người có quyền thật và kênh cảnh báo phải khớp config; chưa biết SLA phản ứng thực tế nếu chưa diễn tập.

## LeDoanDuong-2A202603372

### Phần việc phụ trách

Guards vòng 1, kiểm danh tính/approval/parcel/quyền lợi và test cổng; hỗ trợ phân tích nhánh kỹ thuật S5.

### Đóng góp cụ thể

Theo nhánh LeDoanDuong: pin policy, kiểm quyền lợi/phê duyệt, bảo vệ hãng và payload, sửa liên kết kiện và ngày hết hạn. Bản sửa S5 sau tích hợp được Codex thực hiện theo yêu cầu chung, không gán riêng cho Dương.

### Bằng chứng

03983b0; 56a7d55; 58e9fa2 trên nhánh LeDoanDuong; tests/test_guards.py; lab10/guards_round1.py.

### Exit ticket

Đề xuất tự nhận xét: guard phải kiểm trước nơi ghi và dựa nguồn thật; chống trùng theo ticket chưa đủ, cần kiểm ledger theo order và giao dịch khi có concurrency.

## Trước nộp LMS

Mỗi thành viên xác nhận mục cá nhân và tự nộp cùng link repo bằng tài khoản LMS của mình. Trưởng nhóm xác nhận đề xuất quyết định v1/v2 và các mốc hồi cứu; các mục này không được coi là chữ ký của người đó chỉ vì đã có tên trong file.
