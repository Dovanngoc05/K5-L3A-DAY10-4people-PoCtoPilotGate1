# TV3 — Chuẩn bị đánh giá và giám sát

Tài liệu làm việc hỗ trợ, không thay ba phiếu chính. Đã có baseline và trace thật sau khi tiêu chí TV1 ký được merge lên origin/main. Chưa có checkpoint, prepared, kết quả cổng vòng 1 hay thẻ sự cố.

## Đã chuẩn bị

- Phiếu A, A2 câu 1.3: giữ metric ghi lỗi hãng oan do TV1 đã chọn; TV3 xác nhận và sửa đường dẫn/trường dữ liệu theo evaluator. Bản nháp metric chọn chính sách trước đồng bộ chưa được dùng làm metric chính của nhóm.
- Phiếu B, B7.3: đã chạy hai cách diễn đạt cùng yêu cầu sau khi tích hợp cổng TV2; cả hai denied, không ghi sổ/lỗi hãng/thông báo hãng. Có output thật trong `docs/tv3-evidence/`.
- B0–B2: bổ sung baseline xác nhận `R-base-before-20261118-160903-aca5cb` và hai tác hại cùng trace `T-002@55`. Bằng chứng ở `docs/tv3-evidence/`; chưa triển khai monitor khi chưa biết thẻ.

## Kết quả và bàn giao hiện tại

### Bản sửa nghiệp vụ theo yêu cầu tiếp theo

User đã yêu cầu sửa cả lỗi nghiệp vụ. `_refund_gate` hiện kiểm ledger theo order và hoàn số dư, `_fault_gate` chặn lỗi hãng lặp; không đổi config hoặc snapshot vòng 1. 40 test đạt. Grade cuối `R-S5-grade-20261118-173308-883400`: visible/criteria/regression/monitor đều đạt, after S5 50/50, 0 hoàn sai/0 lỗi hãng oan, ROI +0,52, chi phí 6.564đ/ticket. Phạm vi S5 vẫn 33,33%. Chẩn đoán trong bộ nhớ đủ 150 trial cũng không có ca hỏng; không thay phạm vi trên đĩa. Integrity vẫn thiếu gói thẻ khác; upstream chính thức chưa có bản sửa grader. Xem `docs/s5-fix-report.md` để dùng trạng thái mới nhất; các mục bàn giao bên dưới là lịch sử trước sửa.

### S5 — phần TV3 đã thực hiện

- Đã chạy grade đầu tiên trước thay đổi theo thẻ: `R-S5-grade-20261118-172607-6b6da8`; base/prepared/after lưu trong docs/tv3-evidence/S5-initial. Đã phân tích hoàn trùng liên ticket/hoàn tay, chi phí AI cộng công người ở HCM-B2B, và ticket dài.
- Đã điền C0–C2 và C8, bổ sung hai monitor không có nhãn vào monitors.py. Không sửa guards.py hoặc quyết định phạm vi/nhân sự của nhóm. Monitor chỉ phát hiện, không khắc phục hoàn trùng.
- Grade sau thêm monitor `R-S5-grade-20261118-172739-a2b82f`: criteria, regression, monitor đạt; visible chưa đạt: 350.000đ hoàn sai, 15 lỗi hãng oan, ROI -0,55, pass_rate/pass_k 0,70. 35/35 test vẫn đạt. Không có kết quả hidden tests ở máy này.
- TV2 cần sửa kiểm trùng theo order/ledger, bao gồm hoàn tay và nhiều ticket của một đơn. TV1/TV4 cần xác nhận biện pháp chi phí/phạm vi và hoàn thiện phần Phiếu C thuộc vai mình; v1/v2 chưa được TV3 tự chọn. Chỉ số mới không được dùng để kết luận đã sửa sự cố.
- Integrity: đã khôi phục 23 file hiện có về byte LF sau khi xác minh SHA256 của bản LF khớp MANIFEST; thêm quy tắc eol=lf theo từng đường dẫn để tránh Git Windows đổi lại. Không sửa nội dung logic file khóa, manifest, tiêu chí hoặc snapshot. Grade mới chỉ còn thiếu 28 file của S1–S4/S6–S8. README repo thẻ yêu cầu chỉ lấy thẻ được giao, trong khi grader kiểm toàn bộ manifest; cần Coach cung cấp cách xử lý chính thức. Không tải/mở thẻ khác và không làm giả integrity đạt.
- Nội dung xung đột merge đã giải quyết; Git vẫn ghi UU do chưa được phép stage/commit hoàn tất. Chưa push các thay đổi này sau lần từ chối cấp quyền commit merge.

Chi tiết bàn giao và artifact: docs/tv3-s5-handover.md.

### Sau tích hợp NguyenHuuDuc và checkpoint

- Đã kết hợp config operations/legal của `a065538` với cổng TV2; giải quyết xung đột Phiếu B bằng cách giữ nội dung TV3 và bổ sung các dòng thử nghiệm do TV4 ghi. Các report TV4 nêu vẫn ở máy TV4, cần lấy file bằng chứng khi gom bài.
- Eval tích hợp `R-base-after-20261118-172347-6b6da8`: 65/65 đạt, coverage 0,5909; chi phí 5.550đ/ticket, ROI 0,80, 0 ùn, không hoàn sai/lỗi hãng oan/PII; 35/35 test đạt. Review rate 0,3077 bao gồm kiểm mẫu, khác escalation rate 0,2308.
- Checkpoint thực hiện lúc 2026-11-18T17:24:42 theo timestamp công cụ, hash `300f908643d9ccd6f8f24d8028656a6bdcd942742a43ccf1b08de0f671d3c492`. Đây là mốc chốt thực tế sau khi đã tải gói S5, trước khi mở/phân tích nội dung S5; không mô tả thành đã chốt trước khi nhận gói thẻ và không sửa/backdate lock.
- Prepared `R-base-prepared-20261118-172442-6b6da8` giữ cùng kết quả eval tích hợp; criteria verify và checkpoint verify đạt. Bản chụp cổng/config giữ nguyên từ đây.
- Lệnh hoàn tất commit merge bị từ chối cấp quyền. Merge còn đang chờ Git đánh dấu giải quyết xung đột và commit; chưa push bản tích hợp/checkpoint. Không chạy S5 trước khi nhóm xác nhận v1 và lưu mốc vòng 1; chưa tự chọn quyết định thay TV1.

Các mục lịch sử bên dưới phản ánh trạng thái từng thời điểm, không thay trạng thái tích hợp mới nhất ở trên.

### Sau tích hợp LeDoanDuong

- Đã merge origin/LeDoanDuong tại `58e9fa2` vào DoanNhatAnh; không thay code cổng của TV2.
- `python -X utf8 -m unittest discover -s tests`: 35/35 đạt, gồm kiểm tra hồi quy toàn bộ bộ nền bằng config mặc định và các ca cổng do TV2 bổ sung.
- Eval `R-base-after-20261118-172000-182fc8`: 65 trial trong phạm vi HN/HCM, coverage 0,5909; pass_rate 1 [1;1], pass_k 1; hoàn sai/lỗi hãng oan/PII đều 0. Chuyển người 0,2308, chi phí 5.165đ/ticket, ROI 0,94, 0 ca ùn, không vượt trần. Gate các ngưỡng đã ký đạt trên report này.
- Không so trực tiếp 65 trial này với 110 trial baseline như cùng một tập mẫu. Test hồi quy toàn bộ là bằng chứng bổ sung, không thay cho eval toàn phạm vi ở mốc chốt.
- Hai behavioral test B7.3 đạt trong hai ca đã chạy; T-002@55 ở after cũng bị chặn khoản hoàn sai. Report, gate, trace và journal được sao lưu trong docs/tv3-evidence.
- Chưa checkpoint: operations.pic/approver/alert vẫn trống, công suất/SLA chưa đặt, legal còn mặc định; cần tích hợp phần TV4 và nhóm chốt. Chưa mở/phân tích S5 hay chạy grade; chưa có prepared hoặc quyết định v1.

### Baseline trước tích hợp

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

Nhóm xác nhận S5. Đã lấy duy nhất `incidents/S5/` từ `https://github.com/minhhai203/K5_L3_Day10_PoC-to-Pilot_Gate1_cards`, giữ nguyên bốn file nguồn; chưa mở nội dung thẻ/tickets hoặc chạy sự cố. Khi kiểm tra remote, origin/main ở `23b6213`, cổng TV2 ở origin/LeDoanDuong `56a7d55`, vận hành TV4 ở origin/NguyenHuuDuc `a065538`; chưa nhánh nào trong ba nhánh này có `round1.lock` hoặc bản chụp vòng 1. Cần nhóm tích hợp, kiểm thử và chốt vòng 1 trước khi phân tích S5; không tạo lại hay giả lập checkpoint quá khứ. Khi có mốc prepared, lệnh cần chạy là `python -X utf8 -m lab10.grade --incident S5` trước mọi sửa theo thẻ.

Ghi số thẻ ở Phiếu C. Thay Sx bằng số thật. Chạy `python -m lab10.grade --incident Sx` ngay trước khi ai sửa; lưu mã và report đầu tiên vào C0–C1. Dò ít nhất hai lỗi khác nguồn, có ít nhất một lỗi chìm, ghi ticket@seed và dòng trace ở C2. Cả nhóm đối chiếu pre-mortem.

Monitor C8: chọn tín hiệu bám sự cố, dùng các trường trial không có nhãn như `events`, `ledger`, `faults`, `outbound`, `queue_wait_min`, `queue_stuck`, `cost_vnd`. Không đọc label/pass/kết quả chấm và không nhận diện bằng mã ticket. Hàm nhận `trials`, trả về một số; quy định mẫu số và trường hợp rỗng, đăng ký trong `MONITORS`. `escalation_rate` có sẵn không tính. Chỉ kết luận monitor đạt sau khi grade cho thấy chạy được và giá trị khác giữa sự cố với bộ nền; trường hợp cổng đã chặn tác hại có thể cần theo dõi tín hiệu bị chặn trong events.

Sau bản sửa tích hợp:

```powershell
python -m lab10.eval --suite Sx --stage after --note "mo ta thay doi"
python -m lab10.eval --suite base --stage after --note "kiem tra hoi quy"
python -m lab10.grade --incident Sx
```

Bàn giao cho TV1: ba mã base/prepared/after tương ứng report, ngưỡng còn chưa đạt, chi phí/ROI/hàng chờ/độ phủ và kho/hãng có kết quả xấu nhất. Report trên sự cố và trên bộ nền phải ghi rõ suite, không so lẫn hai bộ. Nếu code/config đổi sau đo, chạy lại trước khi gom bài. Mỗi thành viên tự viết đóng góp, exit ticket và việc dùng AI trong TEAM.md.
