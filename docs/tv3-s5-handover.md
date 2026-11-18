> Cập nhật cuối hồ sơ: đã bổ sung đủ file thẻ theo yêu cầu người dùng; grade R-S5-grade-20261118-184018-883400 đạt PASS-VISIBLE và integrity. Các trạng thái thiếu file/chưa ký/chưa tích hợp bên dưới là ghi chép lịch sử. Xem submission/REPORT.md và submission/docs/ để đọc hồ sơ cuối.

# TV3 — Bàn giao S5

## Kết quả có thể dùng

Grade đầu `R-S5-grade-20261118-172607-6b6da8` được chạy trước sửa theo S5. Snapshot vòng 1 `300f9086` giữ nguyên. C0 ghi đúng ba mốc; C1 ghi việc B6 còn trống, không nhận rằng nhóm đã dự đoán sự cố khi chưa có văn bản chứng minh.

| S5 | Base trước cổng | Prepared | After thêm monitor |
|---|---:|---:|---:|
| Trial | 150 | 50 | 50 |
| Độ phủ | 100% | 33,33% | 33,33% |
| pass_rate / pass_k | 0,8333 / 0,8333 | 0,70 / 0,70 | 0,70 / 0,70 |
| Hoàn sai tổng qua 5 seed | 890.000đ | 350.000đ | 350.000đ |
| Lỗi hãng oan | 20 | 15 | 15 |
| Chi phí/ticket, chưa gồm tiền mất | 6.083đ | 6.594đ | 6.594đ |
| ROI, đã tính tiền mất | -0,33 | -0,55 | -0,55 |
| LLM ticket đắt nhất | 2.412đ | 768đ | 768đ |

Không so tổng thiệt hại giữa hai phạm vi như cùng mẫu. Chi phí xử lý thấp hơn làm tay vẫn có thể ROI âm khi tính tiền mất. Base regression sau monitor đạt 65/65 trial trong phạm vi HN/HCM; 35 test công khai và test TV2 đạt.

## Bằng chứng cho TV2

- `S5-02@11` (prepared): O-2501 đã được hoàn ở S5-01, nhưng ticket mới vẫn ghi 25.000đ và lỗi GHSH. `S5-03` tiếp tục cùng nhánh này. Guard kiểm trùng cùng ticket không đủ chống nhiều ticket cho cùng order.
- `S5-20@11` (prepared): O-2520 có dòng hoàn tay T-CSKH-2520 trong ledger_seed, nhưng tiếp tục ghi thêm 20.000đ và lỗi VNX. Cờ refund_status không phản ánh nguồn ghi khác và cập nhật theo lô.
- Biện pháp cần kiểm chứng: dựa vào sổ cái theo đơn và quyền lợi đã thanh toán, không dựa riêng ticket_id/refund_status; ca hợp lệ chưa được hoàn vẫn phải được phục vụ. Khi chạy thật cần bảo đảm tính nguyên tử giữa kiểm tra và ghi để chống hai yêu cầu đồng thời. TV3 chưa sửa guards.py, không tuyên bố nhánh này đã khắc phục.

## Bằng chứng cho TV1/TV4

- `S5-51@11` base: đề xuất 230.000đ vượt auto_limit, chuyển người sau khi đã tốn 565đ AI. Toàn HCM-B2B trung bình 11.326đ/ticket; kho đã ngoài phạm vi prepared nên không nói rằng cổng đã khiến kho này có lời.
- `S5-70@11` base: 2.018đ tiền agent. Prepared chặn trước đọc, dự toán spent 200 + next_call 1.518 > ngân sách 1.500đ; chuyển người chỉ tốn 200đ agent nhưng còn công người.
- Đề nghị đối soát ledger với kế toán, xác nhận quy trình phân luồng sớm ca chắc chắn cần người và tính ROI sau tiền mất. Các ngưỡng, nhân sự, phạm vi và quyết định là của nhóm; không tự sửa tiêu chí đã ký.

## Monitor TV3

`max_warehouse_processing_cost_upper_bound_vnd` nhóm theo warehouse, tính tổng cost_vnd cộng chi phí đầy đủ cho các ca có review_kind, chia số trial từng kho rồi lấy lớn nhất. Đơn giá đọc từ ops_facts; không có label/pass/fail. Vì không có review_units trong monitor_view, recheck bị tính cả ca nên là ước lượng trên của phần công duyệt; không gồm phí trực và tiền hoàn sai. Không thay ROI hoặc đối soát tài chính.

`cost_budget_handoff_rate` đếm tỷ lệ trial có business_gate/cost_budget_per_ticket_vnd, mỗi trial tính một lần. Chỉ số vẫn sáng khi cổng đã ngăn vượt tiền: after bộ nền 0, S5 0,30. Grade `R-S5-grade-20261118-172739-a2b82f` xác nhận monitor đạt; phần C8 ghi số và giới hạn.

## Lỗi đóng gói cần Coach xử lý

Grade đầu báo 23 file hiện có sai hash do CRLF. Đã đổi lại LF chỉ khi SHA256 bản LF khớp manifest; các hash hiện có và snapshot/criteria đều kiểm tra đúng. Không sửa code grader, file manifest hoặc dữ liệu để đổi kết quả.

Grade hiện còn lỗi integrity vì thiếu 28 file thuộc 7 thẻ không được giao. Repo thẻ hướng dẫn chỉ nhận thư mục được giao, nhưng grader kiểm tất cả mục trong MANIFEST. Cần Coach cung cấp bản phát hành/grader tương thích với nhận riêng S5 hoặc hướng dẫn chính thức. Chưa mở/tải các thẻ khác. Vì vậy không báo PASS tổng thể.

## Artifact

- `docs/tv3-evidence/S5-initial/`: grade đầu và report base/prepared/after.
- `docs/tv3-evidence/S5-traces/`: các JSON trace trước sửa để đối chiếu C2.
- `docs/tv3-evidence/S5-latest-grade.json`, `.txt`: grade sau thêm monitor.
- `docs/tv3-evidence/S5-after-monitors-report.json`, `base-after-monitors-report.json`: eval và hồi quy.
- `docs/tv3-evidence/journal.jsonl`: nhật ký thực tế; không xóa các lần lỗi/FAIL.

Phiếu C các mục C3–C7/C9–C12 thuộc phần phối hợp của TV1/TV2/TV4 còn cần hoàn thiện. v1 và v2 vẫn chưa được nhóm chốt. Chưa gom bài nộp hoặc tuyên bố ĐỦ THÀNH PHẦN.
