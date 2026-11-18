> Cập nhật cuối hồ sơ: đã bổ sung đủ file thẻ theo yêu cầu người dùng; grade R-S5-grade-20261118-184018-883400 đạt PASS-VISIBLE và integrity. Các trạng thái thiếu file/chưa ký/chưa tích hợp bên dưới là ghi chép lịch sử. Xem submission/REPORT.md và submission/docs/ để đọc hồ sơ cuối.

# S5 — Sửa hoàn trùng và xác minh tài chính

## Bản sửa

`lab10/guards.py` đối chiếu sổ cái theo order trước khi ghi tiền, bao gồm hoàn tay và hoàn ở ticket khác. Sổ cái có tiền không hợp lệ được chuyển người đối soát. Nếu quyền lợi đã trả đủ, từ chối lệnh ghi; nếu đã trả một phần, chỉ trả phần còn lại bằng Verdict.modify. Kiểm replay cùng ticket và hard cap 2.000.000đ vẫn giữ. Kiểm lỗi hãng dựa trên order/parcel/carrier để không ghi lại lỗi đã có.

Không thay phạm vi HN/HCM, nhân sự, ngân sách hay tiêu chí để làm đẹp số. Snapshot vòng 1 và tiêu chí đã ký còn nguyên. Trần chi phí và monitor vẫn giữ như trước; ROI tăng vì không còn tiền mất do hoàn trùng.

## Kết quả cuối

Grade `R-S5-grade-20261118-173308-883400`; after `R-S5-after-20261118-173309-883400`.

| Chỉ số S5 | Prepared | After sửa |
|---|---:|---:|
| Trial trong phạm vi | 50 | 50 |
| pass_rate / pass_k | 0,70 / 0,70 | 1 / 1 |
| Coverage | 33,33% | 33,33% |
| Hoàn sai | 350.000đ | 0đ |
| Lỗi hãng oan | 15 | 0 |
| PII | 0 | 0 |
| Chi phí/ticket | 6.594đ | 6.564đ |
| ROI | -0,55 | +0,52 |
| LLM cao nhất/ticket | 768đ | 764đ |

40/40 test đạt, gồm 5 test mới dùng order/ticket tự tạo để kiểm hành vi liên request, hoàn tay một phần, thông báo đúng số thực ghi, ghi hãng lặp và ledger không hợp lệ. Test công khai giữ nguyên. Grade xác nhận criteria/visible/regression/monitor đạt, hidden chưa có tại máy.

Chẩn đoán bổ sung toàn S5: 150/150 trial đạt khi dùng bản sao config trong bộ nhớ với phạm vi all, bao gồm hoàn tay một phần 12.000đ còn lại. Đây là kiểm tra logic ngoài phạm vi pilot, không phải report chứng minh toàn bộ kho có lời, không sửa config trên đĩa hoặc thay phạm vi pilot. Xem `docs/tv3-evidence/S5-full-scope-diagnostic.json`.

## Integrity chưa thể sửa bằng code nghiệp vụ

23 file hiện có đã được phục hồi đúng byte LF khớp MANIFEST và được đặt eol=lf để tránh Git Windows chuyển lại. Hash nguồn khóa hiện có, tiêu chí và snapshot được kiểm tra, không sửa manifest/grader.

Còn thiếu đúng 28 file của 7 gói khác S5. Repo thẻ hướng dẫn chỉ lấy gói được giao nhưng grader kiểm tất cả gói trong manifest. Đã fetch upstream chính thức, kiểm `upstream/main` tại `a9d9b1d`: `lab10/grade.py` và `lab10/MANIFEST.json` không khác bản hiện tại, nên không có bản cập nhật chính thức để áp dụng. Không tải thẻ khác, tạo file giả hoặc bỏ mục manifest để đạt integrity. Cần hướng dẫn/bản phát hành phù hợp từ Coach. Vì vậy grade tổng thể vẫn FAIL dù visible/regression/monitor đạt.

## Giới hạn thực tế

Mock xử lý nối tiếp; kiểm tra ledger trước ghi chưa chống được hai worker cùng đọc số dư cũ. Pilot thật phải có giao dịch/khóa hoặc idempotency tại nơi ghi tiền và đối soát hoàn tay. Không kết luận bảo đảm an toàn production từ test mock. Nhóm vẫn cần hoàn thiện các phần Phiếu B/C của mình, chốt quyết định dựa trên bằng chứng và xử lý integrity trước nộp.

Commit merge và push đang chờ vì yêu cầu cấp quyền trước bị từ chối. Không báo thay đổi local là đã lên GitHub.
