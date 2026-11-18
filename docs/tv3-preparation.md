# TV3 — Chuẩn bị đánh giá và giám sát

Tài liệu làm việc hỗ trợ, không thay ba phiếu chính. Đã có baseline và trace thật sau khi tiêu chí TV1 ký được merge lên origin/main. Chưa có checkpoint, prepared, kết quả cổng vòng 1 hay thẻ sự cố.

## Đã chuẩn bị

- Phiếu A, A2 câu 1.3: giữ metric ghi lỗi hãng oan do TV1 đã chọn; TV3 xác nhận và sửa đường dẫn/trường dữ liệu theo evaluator. Bản nháp metric chọn chính sách trước đồng bộ chưa được dùng làm metric chính của nhóm.
- Phiếu B, B7.3: một tính chất và hai cách diễn đạt của cùng yêu cầu, lệnh PowerShell, kỳ vọng và ô kết quả chưa chạy.
- B0–B2: bổ sung baseline xác nhận `R-base-before-20261118-160903-aca5cb` và hai tác hại cùng trace `T-002@55`. Bằng chứng ở `docs/tv3-evidence/`; chưa triển khai monitor khi chưa biết thẻ.

## Kết quả và bàn giao hiện tại

- Gốc nhánh: `23b6213` (PR #1 merge nhánh Dovanngoc); commit ký `d355eb9` đã nằm trong lịch sử origin/main. Nhánh remote Dovanngoc không còn được quảng bá khi fetch.
- `criteria verify` đạt, hash `ce7ab3b63b40620ff1556a26080e0d0f24712e4ce6d467cea37e02ec71f44c05`; không sửa file tiêu chí hoặc lock.
- Baseline: 110 trial, pass_rate 0,9909 [0,9727; 1], pass_k 0,9545; hoàn sai 20.000đ, 1 lỗi hãng oan, 0 PII; chi phí 4.203đ/ticket, ROI 1,34, 0 ca ùn. Gate chưa đạt hai ngưỡng an toàn; đây không phải quyết định v1/v2 của cả nhóm.
- TV2 cần xử lý nguyên nhân số ngày khách khai đè tracking và kiểm chứng B7.3; TV4 hoàn thiện operations/legal; chỉ checkpoint khi nhóm chốt cả code lẫn config. Không tự lấy nhánh công việc đang dở của thành viên khác để chốt.
- Test công khai 13/13 đạt. Trên Windows dùng `python -X utf8 -m ...` để in tiếng Việt. Lần eval đã lưu report/journal trước lỗi console cp1252; không cần sửa evaluator hay xóa nhật ký.

## Trước lần đo đầu tiên

TV1 xác nhận đã thống nhất tiêu chí với cả nhóm, ký, commit và push lên origin. Kiểm tra có `config/acceptance_criteria.lock`; sự tồn tại của lock chưa đủ chứng minh đã push. Không sửa tiêu chí sau ký. Nhóm cần chọn PRD v1.1 và eval card Lab 9 làm tài liệu chung.

Sau xác nhận, chạy từng lệnh tại thư mục gốc repo:

```powershell
python -m lab10.eval --suite base --stage base --note "baseline"
python -m lab10.gate --run runs/<ma-lan-chay>/report.json
python -m lab10.trace --suite base --ticket T-002 --seed 55
```

Thay `<ma-lan-chay>` bằng mã thật. Ghi vào B0–B2: mã chạy, suite/stage, phiên bản code/config, chỉ số và dòng trace chứng minh lỗi. Đọc cả phần chi phí/ROI/hàng chờ và theo kho/hãng. Không coi 13 test khởi động đạt là bằng chứng Gate 1 đạt.

## Bàn giao với TV2 và vòng 1

1. Cung cấp trace và nguồn dữ liệu cho lỗi; để TV2 quyết định cổng tổng quát, tránh xử lý riêng ticket.
2. Khi cổng và config sẵn sàng, chạy hai lệnh ở B7.3, dán output thật và kết luận từng ca. Ticket không có nhãn tự động, TV3 phải đối chiếu kỳ vọng bằng dữ liệu.
3. Chạy lại test công khai và eval base ở stage after, kiểm tra không làm hỏng ca vốn đúng.
4. Chỉ checkpoint khi TV1/TV2/TV4 xác nhận cổng và config vòng 1 đã chốt. Checkpoint chỉ thực hiện một lần; không sửa bản chụp và lock.

```powershell
python -m unittest discover -s tests
python -m lab10.eval --suite base --stage after --note "kiem tra cong vong 1"
python -m lab10.checkpoint
python -m lab10.eval --suite base --stage prepared
python -m lab10.gate --run runs/<ma-prepared>/report.json
```

Bàn giao mã prepared, hash checkpoint và số liệu cho TV1 ghi B8; nhóm commit/push mốc vòng 1.

## Sau khi nhận đúng thẻ

Ghi số thẻ ở Phiếu C. Thay Sx bằng số thật. Chạy `python -m lab10.grade --incident Sx` ngay trước khi ai sửa; lưu mã và report đầu tiên vào C0–C1. Dò ít nhất hai lỗi khác nguồn, có ít nhất một lỗi chìm, ghi ticket@seed và dòng trace ở C2. Cả nhóm đối chiếu pre-mortem.

Monitor C8: chọn tín hiệu bám sự cố, dùng các trường trial không có nhãn như `events`, `ledger`, `faults`, `outbound`, `queue_wait_min`, `queue_stuck`, `cost_vnd`. Không đọc label/pass/kết quả chấm và không nhận diện bằng mã ticket. Hàm nhận `trials`, trả về một số; quy định mẫu số và trường hợp rỗng, đăng ký trong `MONITORS`. `escalation_rate` có sẵn không tính. Chỉ kết luận monitor đạt sau khi grade cho thấy chạy được và giá trị khác giữa sự cố với bộ nền; trường hợp cổng đã chặn tác hại có thể cần theo dõi tín hiệu bị chặn trong events.

Sau bản sửa tích hợp:

```powershell
python -m lab10.eval --suite Sx --stage after --note "mo ta thay doi"
python -m lab10.eval --suite base --stage after --note "kiem tra hoi quy"
python -m lab10.grade --incident Sx
```

Bàn giao cho TV1: ba mã base/prepared/after tương ứng report, ngưỡng còn chưa đạt, chi phí/ROI/hàng chờ/độ phủ và kho/hãng có kết quả xấu nhất. Report trên sự cố và trên bộ nền phải ghi rõ suite, không so lẫn hai bộ. Nếu code/config đổi sau đo, chạy lại trước khi gom bài. Mỗi thành viên tự viết đóng góp, exit ticket và việc dùng AI trong TEAM.md.
