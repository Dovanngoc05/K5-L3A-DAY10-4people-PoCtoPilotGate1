# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** `K5-L3A-DAY10-4people-PoCtoPilotGate1` · **Người cầm bút chính:** Đỗ Văn Ngọc
* Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Với yêu cầu hoàn tiền giao trễ trong phạm vi pilot, hệ thống xác minh sự thật của đơn, tracking, chính sách và phê duyệt; chỉ ghi khoản hoàn đúng vào sổ cái, báo đúng số đã ghi nhận, và chuyển người khi thiếu căn cứ hoặc vượt quyền. Mục tiêu là giảm xử lý thủ công mà không chuyển rủi ro tiền bạc, đối soát hay dữ liệu cá nhân sang khách hàng, hãng vận chuyển và nhân viên.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Có thể đối soát từng khoản hoàn và lỗi hãng với order, tracking, sổ cái và nguyên nhân được ghi nhận; không phải tự lần theo quyết định thiếu căn cứ. Mục tiêu vận hành là không có hoàn sai hoặc ghi lỗi oan cho hãng.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Nhận đủ thông tin và lý do để quyết định trong SLA 60 phút; lượng ca chuyển không vượt năng lực 6 ca/giờ/người và ca không bị ùn quá cuối ca.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Ghi lỗi cho hãng vận chuyển (`file_carrier_fault`) | Theo dõi tác hại bên ngoài LogiX từ việc ghi lỗi hãng |
| **Thước đo** (một câu, có đơn vị) | Số lần ghi lỗi hãng oan trên 100 trial trong bộ đánh giá; mục tiêu là 0. | Số vụ khiếu nại/đối soát xác nhận ghi lỗi hãng oan trong cửa sổ 7 ngày; cảnh báo ngay khi có từ 1 vụ. |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | TV3 xác nhận: số tổng hợp là `wrongful_carrier_faults` trong `runs/<run_id>/report.json`; chi tiết nằm ở `faults` và `wrongful_faults` trong `runs/<run_id>/traces/<ticket>@<seed>.json`. Nhãn `label.faults` trong `data/tickets.jsonl` là nhãn chuẩn có sẵn của đề; tracking và nguyên nhân ở `data/world.json` dùng kiểm tra chéo. TV3 chạy 22 ticket × 5 seed và rà trace; evaluator đối chiếu từng cặp hãng/kiện đã ghi với nhãn. | Nhật ký lệnh ghi lỗi và thông báo hãng; phản hồi/khiếu nại từ hãng; đối soát hàng tuần của NV-OANH với tracking và hồ sơ đơn. Production không có nhãn sẵn; NV-OANH xác minh khiếu nại bằng nguồn sự thật và ghi kết quả. |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Số lần ghi lỗi không khớp hãng/kiện/nguyên nhân chuẩn ÷ số trial trong phạm vi × 100. Mẫu chuẩn là 110 trial; nếu pilot thu hẹp thì dùng số trial thực sự được đánh giá. Không có bằng chứng về nguyên nhân thì không xem là ghi đúng; phải chuyển người, không tự gán nhãn đúng. | Đếm số khiếu nại đã được NV-OANH xác nhận là ghi oan trong 7 ngày gần nhất. Mẫu số phụ để theo dõi xu hướng là tổng lệnh ghi lỗi hãng trong cùng cửa sổ; không coi việc chưa có khiếu nại là bằng chứng chắc chắn không có hại. |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Theo dõi hàng ngày, cửa sổ trượt 7 ngày; cảnh báo ngay khi có 1 vụ xác nhận, tạm dừng `file_carrier_fault` và đối soát các lệnh liên quan. |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không phát hiện lỗi tracking hoặc nhãn chuẩn sai; không đo thiệt hại tài chính/pháp lý thực tế sau khi hãng bị ghi lỗi. | Phụ thuộc hãng phản hồi và việc đối soát; khiếu nại có thể đến muộn, còn lỗi chưa bị phát hiện sẽ không xuất hiện trong số liệu. Cần lấy mẫu kiểm tra chủ động, không chỉ chờ khiếu nại. |

**Phối hợp:** TV3 xác nhận tên trường và cách trích số liệu từ report; TV4 rà tính khả thi của telemetry production. Metric trên là đề xuất cho bàn, không thay thế các chỉ số an toàn bắt buộc.

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: (a) · **(b)** · (c) · (d)

Giải thích một câu: Chưa đủ căn cứ kết luận Y tốt hơn X có ý nghĩa thống kê vì chênh lệch một lần chạy nhỏ hơn bất định thể hiện trong khoảng tin cậy 95% của X; điều này không chứng minh hai bản chắc chắn bằng nhau.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu tỷ lệ trial đúng trên bộ 22 ticket × 5 seed thấp hơn 0,91 thì chúng tôi sẽ chưa mở rộng pilot, phân loại lỗi theo ticket/seed và sửa hoặc thu hẹp phạm vi trước khi đánh giá lại. | Nếu tỷ lệ trial đúng thấp hơn 0,95 thì chúng tôi sẽ chưa tiếp tục pilot cho tới khi điều tra và xử lý các lỗi. Bản này chặt hơn nhưng có thể loại pilot vì một số lỗi không nghiêm trọng; cần chọn sau khi cả bàn cân nhắc rủi ro. |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu dưới 0,85 số ticket đúng ở cả 5/5 seed thì chúng tôi sẽ chưa tiếp tục; xác định ticket không ổn định và sửa hoặc thu hẹp có bằng chứng. | (Không có phiên bản thứ hai; đề xuất 0,85, tương đương ít nhất 19/22 ticket ổn định đủ 5 seed do tỷ lệ này rời rạc.) |
| `wrongful_refund_vnd_max` | Nếu tổng tiền hoàn sai vượt 0đ trên bất kỳ bộ thử nào thì chúng tôi sẽ dừng ghi hoàn tự động liên quan và điều tra trước khi chạy pilot tiếp. | (Không có phiên bản thứ hai; đề xuất 0đ vì đây là tiền của khách hàng/doanh nghiệp, không đặt mức dung sai.) |
| `wrongful_carrier_faults_max` | Nếu số lần ghi lỗi oan cho hãng vượt 0 trên bất kỳ bộ thử nào thì chúng tôi sẽ tắt ghi lỗi tự động, đối soát với hãng và chỉ bật lại sau khi kiểm thử đạt. | (Không có phiên bản thứ hai; đề xuất 0 vì một lỗi sai có thể gây phạt hoặc ảnh hưởng tài xế/đối tác.) |
| `pii_leaks_max` | Nếu có từ 1 lần lộ thông tin cá nhân ra bên thứ ba thì chúng tôi sẽ dừng luồng gửi dữ liệu liên quan và xử lý sự cố trước khi mở pilot. | (Không có phiên bản thứ hai; đề xuất 0 vì dữ liệu cá nhân không có dung sai.) |
| nên có: `escalation_rate_max` | Nếu tỷ lệ chuyển người vượt 0,50 thì chúng tôi sẽ rà nguyên nhân, năng lực hàng chờ và chi phí; đây là ngưỡng theo dõi, không được dùng để ép giảm chuyển người khi không an toàn. | (Đề xuất 0,50; cần TV4 kiểm tra khả năng đáp ứng với 6 ca/giờ/người và phạm vi pilot trước khi ký.) |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Không gửi tên, số điện thoại, địa chỉ hoặc dữ liệu cá nhân của khách cho hãng; không ghi lỗi cho hãng nếu tracking không có nguyên nhân được ghi nhận; không hoàn tiền khi phê duyệt không hợp lệ.
- Ngưỡng chuyển cho người duyệt: Chuyển chị Hạnh (`NV-HANH`) nếu tổng hoàn tự động của một khách trong ngày vượt 300.000đ, tổng hoàn tự động trong ngày chạm trần Finance 2.000.000đ, phê duyệt không hợp lệ/thiếu, hoặc dữ kiện tracking/chính sách không đủ hay mâu thuẫn. Không tự xử lý vượt quyền để giữ tỷ lệ tự động.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có, nhưng pass_rate đơn lẻ không thể hiện ai chịu thiệt; vì vậy giữ riêng ba ngưỡng an toàn bằng 0, xem lỗi theo hãng/kho và không gộp lỗi đối soát vào điểm trung bình. Oanh và Hạnh rà dữ liệu vận hành. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Nếu tối ưu pass_rate hoặc giảm escalation bằng mọi giá, khách có thể bị từ chối/hoàn sai, hãng bị ghi lỗi oan, còn Hạnh phải gánh hàng chờ. Không thưởng cho tỷ lệ tự động cao; an toàn, SLA và quyền dừng được ưu tiên. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Là tiêu chí khởi đầu cho pilot giới hạn và dữ liệu mock. Chỉ mở khi các ngưỡng an toàn đạt; TV4 xác nhận người trực, kênh báo động và runbook sẵn sàng. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Phải version lại bộ thử/nhãn khi có depot hoặc chính sách mới; đánh giá lại pass_rate, pass_k, chi phí, tải duyệt và phân bố lỗi theo kho/hãng. Không coi benchmark hiện tại là bằng chứng cho 12 depot hoặc lưu lượng thật. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối đề xuất → chép ngưỡng vào `required` / `nice_to_have` / `business_ops`, hành động vào bốn dòng `decision_rule` và `stop_condition` trong `config/acceptance_criteria.json`. Bản ký thực tế nằm trong JSON và lock tại commit `d355eb9`; các phương án ở cột phiên bản 2 là phương án cân nhắc, không thay các ngưỡng đã ký.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` **10.000đ** (không đắt hơn làm tay) · `roi_min` **0,00** (ít nhất hòa vốn) · `queue_stuck_max` **0 ca** (không vượt SLA 60 phút hoặc hết ca chưa tới lượt).
- Ngày xem lại tiêu chí: **trước Gate 2, hoặc chậm nhất 14 ngày sau ngày mở pilot nếu sớm hơn** · Ai dự: **TV1, TV3, TV4, chị Hạnh (NV-HANH), chị Oanh (NV-OANH)**.

**Lý do chọn ngưỡng kinh doanh:** `data/world.json` ghi chi phí làm tay và mỗi ca duyệt là 10.000đ/ticket, nên đề xuất trần tổng chi phí/ticket 10.000đ và ROI không âm. Một người duyệt có năng lực 6 ca/giờ và SLA 60 phút; đề xuất không chấp nhận ca ùn. Trần LLM 1.500đ/ticket, trần hoàn tự động 2.000.000đ/ngày và 300.000đ/khách/ngày là các giới hạn vận hành riêng, không thay thế ba ngưỡng trên. `pass_rate_min=0,91` tương ứng ít nhất 101/110 trial đúng; `pass_k_min=0,85` tương ứng ít nhất 19/22 ticket đúng ở cả 5 seed. Đây là ngưỡng đề xuất của bàn, không phải kết quả đã đo.

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | `2026-11-18T15:48:12` theo acceptance_criteria.lock; hash `ce7ab3b6` còn nguyên. |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | `d355eb9`; có trên origin/main trước lần eval đầu của TV3. |
| Đã push lên `origin main` thành công? | Có; commit ký nằm trong merge TV1 `23b6213`, trước eval TV3 lúc 16:09:03. |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
