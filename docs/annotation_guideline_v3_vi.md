# Hướng dẫn chấm tay, bản 3: câu trả lời về MITRE ATT&CK (thí nghiệm khẳng định)

Dùng với file `cham_tay_khang_dinh_150.csv` (150 dòng). Mỗi người chấm nhận **một bản riêng** của file này.

## Trước khi chấm

- Chấm **độc lập**: không xem nhãn của người khác, không trao đổi với ai cho tới khi chấm xong.
- Chỉ dùng các cột trong file: câu hỏi, câu trả lời của mô hình, đáp án bản hiện hành, đáp án bản cũ.
- **Không dùng AI hay script** để gợi ý nhãn. Nếu có dùng công cụ nào (ví dụ bảng tra tên tactic), ghi tên công cụ vào cuối file.
- Ghi nhãn vào cột `nhan`. Cột `ghi_chu` không bắt buộc; chỉ cần ghi ở những câu khó.
- Thời gian ước tính: khoảng 2–3 giờ.

## Đáp án luôn tính theo bản hiện hành

Mỗi dòng có hai cột phiên bản:

- `ban_hien_hanh`: phiên bản mà câu hỏi gọi là hiện hành (v19.2 hoặc v7.2). Đáp án đúng là cột `dap_an_hien_hanh`.
- `ban_cu`: phiên bản cũ ngay trước đó (v18.1 hoặc v6.3). Cột `dap_an_ban_cu` chỉ dùng để nhận ra câu trả lời lỗi thời.

Với câu hỏi "is the technique ID … still valid?": nếu mã còn hiệu lực, đáp án là chính mã đó; nếu đã bị thay, đáp án là mã thay thế. Trả lời lại mã cũ đã bị thay là **lỗi thời**.

## Ghép mã với tên (câu hỏi về tactic)

Mô hình có thể viết theo mấy dạng:

- `"TA0005 Stealth"`: mã và tên trong cùng một mục;
- `["TA0005", "Stealth"]`: mã và tên tách thành hai mục liền nhau. Ghép chúng lại thành một cặp;
- `"Stealth (TA0005)"`: tên trước, mã trong ngoặc.

Khác biệt nhỏ về chữ không tính là lệch: hoa/thường, "&" thay cho "and", "Defence" thay cho "Defense", hay một chữ thừa như "Tactics Execution". Một mục bị lặp lại (ví dụ "T1020" hai lần) chỉ tính một lần.

## Sáu nhãn

Xét lần lượt từ trên xuống; gặp quy tắc nào khớp thì dừng ở đó.

1. **KHONG_TRA_LOI**: danh sách trả lời rỗng.
2. **KHONG_NHAT_QUAN**: có ít nhất một cặp mã–tên không khớp nhau ở **cả hai** phiên bản, hoặc có mã không tồn tại.
   - Ví dụ lệch (v19.2): "TA0005 Impact", "TA0112 Defense Evasion", "TA0005 Defense Impairment".
   - Ví dụ mã không tồn tại: TA0118.
3. **LOI_THOI**: có ít nhất một mục **chỉ** đúng ở bản cũ. Mục đó có thể là:
   - một **mã**: ví dụ trả TA0005 khi bản hiện hành đã chuyển kỹ thuật sang TA0112; hoặc trả mã kỹ thuật cũ đã bị thay;
   - một **tên** (chỉ có ở v19.2): "Defense Evasion" là tên cũ, vì v19.2 gọi TA0005 là Stealth.

   Gán LOI_THOI cả khi câu trả lời đã có đủ đáp án hiện hành nhưng lẫn thêm mục cũ. Một mục đúng ở **cả hai** phiên bản (ví dụ TA0003 Persistence) không bị coi là lỗi thời.
4. **DUNG**: khớp đúng toàn bộ đáp án hiện hành, không thừa, không thiếu.
5. **MOT_PHAN**: có ít nhất một mục đúng theo bản hiện hành, nhưng thiếu hoặc thừa mục (thừa một mục không thuộc bản nào cũng là MOT_PHAN).
6. **SAI**: các trường hợp còn lại.

## Ví dụ (không có trong 150 dòng)

| Câu trả lời | Đáp án hiện hành | Đáp án bản cũ | Nhãn |
|---|---|---|---|
| `["TA0040 Impact"]` | Impact (TA0040) | Impact (TA0040) | DUNG |
| `["TA0040", "Exfiltration"]` | Impact (TA0040) | Impact (TA0040) | KHONG_NHAT_QUAN |
| `["TA0005 Defense Evasion", "TA0040 Impact"]` (v19.2) | Impact (TA0040), Stealth (TA0005) | Impact (TA0040), Defense Evasion (TA0005) | LOI_THOI |
| `["TA0040 Impact"]` | Impact (TA0040), Stealth (TA0005) | Impact (TA0040), Defense Evasion (TA0005) | MOT_PHAN |
| `["T1002"]` (v7.2) | T1560 | T1002 | LOI_THOI |
| `["T1560", "T1002"]` (v7.2) | T1560 | T1002 | LOI_THOI |
| `["TA0009 Collection"]` | Impact (TA0040) | Impact (TA0040) | SAI |

## Khi xong

Gửi lại file kèm ba thông tin:

- họ tên và vai trò của người chấm (ví dụ: giảng viên an toàn thông tin);
- ngày chấm và khoảng thời gian đã chấm;
- có dùng công cụ nào hỗ trợ không.
