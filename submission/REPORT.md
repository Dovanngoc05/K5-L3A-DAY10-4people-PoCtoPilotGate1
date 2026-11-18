# Hồ sơ nộp Lab 10 — 4people — S5

## Kết quả kiểm tra

- Grade `R-S5-grade-20261118-184018-883400`: **PASS-VISIBLE**, integrity/criteria/visible/regression/monitor đạt; chưa chạy test ẩn.
- Bộ nền trong phạm vi HN/HCM: 65/65 trial đạt, coverage 59,09%, 5.550đ/ticket, ROI 0,80, không ca ùn.
- S5 trong cùng phạm vi: 50/50 trial đạt, coverage 33,33%; 0 hoàn sai, 0 lỗi hãng oan, 0 PII; 6.564đ/ticket, ROI 0,52; LLM cao nhất 764đ dưới trần 1.500đ.
- 40/40 test đạt. Chẩn đoán logic toàn S5 150/150 cũng đạt, nhưng không dùng để tuyên bố mọi kho có lợi nhuận hoặc mở rộng phạm vi pilot.
- Tiêu chí ký `d355eb9`, hash `ce7ab3b6`; snapshot vòng 1 `300f9086` còn nguyên. Thư mục `submission/runs/` chứa report ba mốc và nhật ký thật của máy tích hợp.

## Những gì đã sửa

Vòng 1 kiểm tracking/policy/approval, quyền ghi tiền, đúng kiện/hãng và PII; đặt phạm vi HN/HCM, ngân sách 1.500đ và kế hoạch một người duyệt 6 ca/giờ. Vòng 2 đọc sổ cái theo order để không trả lại quyền lợi đã thanh toán, chỉ trả phần còn lại khi hoàn tay một phần, chặn ghi lỗi hãng lặp; thêm monitor chi phí theo kho và chuyển người do ngân sách. Không đổi tiêu chí hoặc thu phạm vi về 0.

Lỗi integrity thiếu 28 file đã được sửa bằng cách nhận đúng file từ repo thẻ được người dùng chỉ định, chỉ dùng thẻ ngoài S5 để kiểm SHA256. File hiện có được khôi phục LF khớp manifest. Không sửa grader, manifest, nhãn hoặc snapshot để đạt kết quả.

## Quyết định và giới hạn của hồ sơ

`decision_v1` và `decision_v2` được điền **Cải tiến thêm** theo đề xuất hồ sơ: số mock đạt nhưng chưa có kiểm chứng giao dịch đồng thời, độ tươi ledger production, kênh cảnh báo thực và diễn tập dừng <=5 phút. Nhóm cần xác nhận lựa chọn này trước khi nộp; không tạo chữ ký thay trưởng nhóm. PASS-VISIBLE cho phép cân nhắc Tiếp tục, không bắt buộc chọn Tiếp tục khi còn thiếu bằng chứng vận hành thật.

B6 và v1 không có bản hoàn chỉnh lưu trước sự cố, nên được đánh dấu tổng hợp hồi cứu. Checkpoint thực tế tạo sau tải S5 nhưng trước đọc/phân tích. Hồ sơ không sửa timestamp hoặc tự nhận đáp ứng mốc thời gian mà lịch sử không chứng minh được. Team chấm quyết định ảnh hưởng của sai lệch quy trình này; `ĐỦ THÀNH PHẦN` không đồng nghĩa bảo đảm điểm hoặc mọi điều kiện rubric đều đã đạt.

Các mục cá nhân trong TEAM.md tổng hợp theo phân công và nhánh/commit. Exit ticket là gợi ý tự nhận xét, từng thành viên cần đọc/sửa/xác nhận; không phải lời khai cá nhân đã được thu thập. Dữ liệu trong báo cáo là mock, chưa có triển khai hoặc thông báo đối tác thật.

## Nộp

Ba phiếu cuối: `submission/docs/`. Code/config hai vòng, tiêu chí/lock và manifest đã được gom. Sửa phiếu gốc trong `templates/` rồi chạy lại `python -X utf8 -m lab10.check_submission --collect` nếu nhóm chỉnh nội dung; không sửa riêng bản chép trong submission/docs.

Mỗi thành viên tự nộp link repo trên LMS bằng tài khoản của mình. Trưởng nhóm kiểm tra quyền truy cập repo theo hướng dẫn hiện hành của Coach; không coi push GitHub là đã nộp LMS.
