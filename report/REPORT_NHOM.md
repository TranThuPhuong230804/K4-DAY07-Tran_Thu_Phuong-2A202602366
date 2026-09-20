# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G16  
**Thành viên:** Đào Đức Anh (Trưởng nhóm - MSSV: 2A202602567), Trần Thu Phương (2A202602366), Nguyễn Quốc Tuấn (2A202602910), Nguyễn Mạnh Hải (2A202602988), Cao Văn Trường (2A202602562)  
**Ngày:** 19/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Thông tin học bổng và chính sách hỗ trợ sinh viên tại Trường Đại học Công nghệ (UET - ĐHQGHN).

**Tại sao nhóm chọn chủ đề này?**
> 1. **Nhu cầu thông tin thiết thực và đa dạng:** Học bổng là mối quan tâm hàng đầu của sinh viên, bao gồm nhiều loại hình phong phú như học bổng khuyến khích học tập (KKHT), học bổng doanh nghiệp (Pegatron, Goertek), học bổng tài trợ cá nhân/tổ chức (Vallet, Đinh Thiện Lý, Data Nest, MB Chasing).
> 2. **Cấu trúc văn bản hành chính giàu dữ liệu định lượng:** Các văn bản chứa các bảng biểu định mức tài chính, tiêu chuẩn học lực (GPA), điểm rèn luyện, chứng chỉ ngoại ngữ và thời hạn nộp hồ sơ cụ thể. Đây là dữ liệu thực tế lý tưởng để thử nghiệm các chiến lược chunking (bảo toàn bảng/điều khoản) và đánh giá độ chính xác của Vector Retrieval.
> 3. **Tính chất phân lớp đối tượng rõ ràng:** Dữ liệu có sự phân tách rành mạch giữa quy định chung toàn trường (`audience: all`) và các thông báo xét cấp cụ thể cho sinh viên (`audience: student`), tạo điều kiện hoàn hảo để chứng minh sức mạnh của Metadata Pre-filtering.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|--------------------|----------------------|----------|-----------------|
| 1 | Cấp học bổng khuyến khích học tập kì cuối cho sinh viên tốt nghiệp đợt xét tháng 06 năm 2026 | `https://uet.edu.vn/cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-cho-sinh-vien-tot-nghiep-dot-xet-thang-06-nam-2026/` | 2026-09-19 / `1545/QĐ-ĐHCN` | 4,273 | `doc_id: cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 2 | Chương trình học bổng Đinh Thiện Lý năm học 2026 - 2027 dành cho sinh viên năm cuối và có hoàn cảnh đặc biệt | `https://uet.edu.vn/chuong-trinh-hoc-bong-dinh-thien-ly-nam-hoc-2026-2027-danh-cho-sinh-vien-nam-cuoi-va-sinh-vien-nam-cuoi-co-hoan-canh-dac-biet/` | 2026-09-19 / `not-stated` | 6,234 | `doc_id: chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 3 | Chương trình học bổng Goertek năm 2027 | `https://uet.edu.vn/chuong-trinh-hoc-bong-goertek-nam-2027/` | 2026-09-19 / `3962/ĐHQGHN-ĐT&CTSV` | 3,145 | `doc_id: chuong-trinh-hoc-bong-goertek-nam-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 4 | Chương trình Học bổng Tài năng Pegatron 2027 | `https://uet.edu.vn/chuong-trinh-hoc-bong-tai-nang-pegatron-2027/` | 2026-09-19 / `PVN-26830` | 4,816 | `doc_id: chuong-trinh-hoc-bong-tai-nang-pegatron-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 5 | Đề nghị danh sách tân sinh viên được nhận HB Đinh Thiện Lý năm học 2026-2027 | `https://uet.edu.vn/de-nghi-danh-sach-tan-sinh-vien-duoc-nhan-hb-dinh-thien-ly-nam-hoc-2026-2027/` | 2026-09-19 / `not-stated` | 2,206 | `doc_id: de-nghi-danh-sach-tan-sinh-vien-hoc-bong-dinh-thien-ly-2026-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 6 | Điều chỉnh đối tượng xét học bổng Data Nest năm học 2026-2027 | `https://uet.edu.vn/dieu-chinh-doi-tuong-xet-hoc-bong-data-nest-nam-hoc-2026-2027/` | 2026-09-19 / `not-stated` | 3,017 | `doc_id: dieu-chinh-doi-tuong-hoc-bong-data-nest-2026-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 7 | Học bổng Data Nest, năm học 2026-2027 | `https://uet.edu.vn/hoc-bong-data-nest-nam-hoc-2026-2027/` | 2026-09-19 / `not-stated` | 4,960 | `doc_id: hoc-bong-data-nest-nam-hoc-2026-2027`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 8 | Học bổng The Best of MB Chasing 2026 | `https://uet.edu.vn/hoc-bong-the-best-of-mb-chasing-2026/` | 2026-09-19 / `not-stated` | 2,310 | `doc_id: hoc-bong-the-best-of-mb-chasing-2026`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 9 | Kết quả xét chọn học bổng Vallet dành cho sinh viên Trường Đại học Công nghệ năm 2026 | `https://uet.edu.vn/ket-qua-xet-chon-hoc-bong-vallet-danh-cho-sinh-vien-truong-dai-hoc-cong-nghe-dai-hoc-quoc-gia-ha-noi-nam-2026/` | 2026-09-19 / `not-stated` | 3,200 | `doc_id: ket-qua-xet-chon-hoc-bong-vallet-2026`<br>`audience: student`, `category: scholarship`, `dept: student-affairs` |
| 10 | Quy định về việc xét, cấp học bổng khuyến khích học tập tại Trường Đại học Công nghệ | `https://uet.edu.vn/quy-dinh-ve-viec-xet-cap-hoc-bong-khuyen-khich-hoc-tap-tai-truong-dai-hoc-cong-nghe/` | 2026-09-19 / `not-stated` | 3,712 | `doc_id: quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap`<br>`audience: all`, `category: regulation`, `dept: student-affairs` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|--------------------------------------------|
| `doc_id` | `string` | `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026` | Định danh duy nhất cho tài liệu gốc, dùng để liên kết các chunk con với văn bản mẹ và phục vụ thao tác xóa/cập nhật tài liệu (`delete_document`). |
| `title` | `string` | `Cấp học bổng khuyến khích học tập...` | Tiêu đề văn bản; dùng để tiêm ngữ cảnh (*context injection*) vào đầu chunk và hiển thị tên nguồn trích dẫn cho người dùng cuối. |
| `source_url` | `string` | `https://uet.edu.vn/cap-hoc-bong...` | URL chính thức từ website trường; cung cấp minh chứng cho Agent trích dẫn nguồn trọn vẹn, chống bịa đặt (*anti-hallucination*). |
| `retrieved_at` | `string (YYYY-MM-DD)` | `2026-09-19` | Thời điểm thu thập dữ liệu; giúp theo dõi tính thời hiệu, phát hiện văn bản lỗi thời hoặc xử lý xung đột phiên bản theo thời gian. |
| `document_version` | `string` | `1545/QĐ-ĐHCN`, `PVN-26830` | Số hiệu quyết định/công văn pháp lý; xác lập tính xác thực cao nhất khi đối chiếu các mức học bổng hoặc tranh chấp thông tin. |
| `audience` | `string` | `student`, `all` | Phân loại đối tượng áp dụng; là trường cốt lõi phục vụ **metadata pre-filtering** (lọc thông báo trực tiếp cho sinh viên hoặc quy chế áp dụng toàn trường). |
| `department` | `string` | `student-affairs` | Phòng ban phụ trách (Công tác Sinh viên); cho phép mở rộng lọc theo đơn vị quản lý khi hệ thống tích hợp thêm tài liệu phòng Đào tạo, Kế hoạch Tài chính. |
| `category` | `string` | `scholarship`, `regulation` | Thể loại văn bản; giúp định tuyến câu hỏi (hỏi về học bổng cụ thể tìm trong `scholarship`, hỏi khung chính sách chung tìm trong `regulation`). |
| `language` | `string` | `vi` | Ngôn ngữ văn bản; giúp pipeline RAG lựa chọn bộ tokenizer hoặc mô hình embedding tương thích cho tiếng Việt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi` | FixedSizeChunker (`fixed_size`) | 29 | 195.6 | Kém (bị cắt ngang bảng định mức tiền và câu) |
| `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi` | SentenceChunker (`by_sentences`) | 3 | 1422.3 | Kém (bảng biểu thiếu dấu chấm câu làm chunk quá dài) |
| `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi` | RecursiveChunker (`recursive`) | 33 | 127.6 | Khá tốt (tách theo `\n\n` giữ trọn từng đoạn văn) |
| `chuong-trinh-hoc-bong-tai-nang-pegatron` | FixedSizeChunker (`fixed_size`) | 32 | 198.9 | Trung bình (cắt máy móc giữa các tiêu chuẩn) |
| `chuong-trinh-hoc-bong-tai-nang-pegatron` | SentenceChunker (`by_sentences`) | 5 | 958.8 | Kém (chunk dài ~960 ký tự do nhiều gạch đầu dòng) |
| `chuong-trinh-hoc-bong-tai-nang-pegatron` | RecursiveChunker (`recursive`) | 35 | 135.8 | Tốt (giữ trọn vẹn từng mục điều kiện và quyền lợi) |

### Chiến lược của từng thành viên

**Thành viên 1 — Đào Đức Anh (Chủ trì R3 / Sentence Chunker)**
- **Loại chiến lược:** `SentenceChunker` (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng biểu thức chính quy với kỹ thuật positive lookbehind `r'(?<=[.!?])\s+'` để nhận diện điểm ngắt câu tự nhiên (`. `, `! `, `? `, `.\n`) mà không làm mất dấu câu. Gom nhóm tối đa 3 câu hoàn chỉnh vào mỗi chunk. Do các văn bản thông báo học bổng có văn phong hành chính chuẩn mực, mỗi câu hoặc cụm 2-3 câu thường bao trọn một điều kiện tiên quyết, một mức kinh phí hoặc một mốc thời hạn. Phương pháp này giữ nguyên cấu trúc câu ngữ pháp, không bao giờ bị ngắt ngang từ ngữ hay xé đôi bảng định mức.
- **Code snippet (nếu custom):** Sử dụng `SentenceChunker(max_sentences_per_chunk=3)` trong `src/chunking.py`.

**Thành viên 2 — Trần Thu Phương, Nguyễn Quốc Tuấn**
- **Loại chiến lược:** `RecursiveChunker` (chunk_size=300)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản theo độ ưu tiên ranh giới tự nhiên: đoạn văn (`\n\n`), dòng (`\n`), câu (`. `) và từ (` `). Phương pháp này giúp giữ nguyên cấu trúc các đoạn văn bản mà không cần viết thêm parser riêng cho từng loại văn bản.
- **Code snippet (nếu custom):** Sử dụng `RecursiveChunker(chunk_size=300)` trong `src/chunking.py`.

**Thành viên 3 — Nguyễn Mạnh Hải, Cao Văn Trường**
- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=300, overlap=50)
- **Mô tả & lý do chọn:** Chia kích thước cố định kèm vùng chồng lấn (overlap 50 ký tự) để đảm bảo không bị đứt gãy thông tin ngay tại điểm chia cắt, kiểm soát dung lượng token ổn định.
- **Code snippet (nếu custom):** Sử dụng `FixedSizeChunker(chunk_size=300, overlap=50)` trong `src/chunking.py`.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đào Đức Anh | `SentenceChunker` (`sentences`) | **10/10 (OpenAI)** / 3/10 (Mock) | Bảo toàn trọn vẹn câu hành chính và liên kết chủ ngữ - thuộc tính; 5/5 câu Top-1; tổng số chunk gọn gàng (40 chunks) giảm nhiễu | Một số bảng biểu không có dấu chấm có thể tạo chunk dài hơn |
| Thành viên 2 | `RecursiveChunker` | 6/10 (OpenAI) / 1/10 (Mock) | Xử lý linh hoạt, các chunk có độ dài vừa phải và ngữ nghĩa tự nhiên | Không có cơ chế gắn lại ngữ cảnh tiêu đề cho các đoạn sau |
| Thành viên 3 | `FixedSizeChunker (overlap)` | 4/10 (OpenAI) / 4/10 (Mock) | Kích thước đồng đều, overlap giúp bù đắp thông tin ranh giới | Cắt ngang từ ngữ và bảng số liệu ngẫu nhiên |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`SentenceChunker (max_sentences_per_chunk=3)`** là chiến lược đem lại hiệu quả truy xuất vượt trội nhất cho bộ dữ liệu học bổng này, đạt điểm số tuyệt đối **10/10 điểm (5/5 câu hỏi đạt Gold Doc ở Top-1)** khi chạy trên `text-embedding-3-small`. Lý do: các quy định học bổng (tiêu chuẩn GPA, rèn luyện, giá trị tài trợ, thời hạn nộp) thường được cấu trúc hoàn chỉnh trong 1-3 câu văn bản. Việc chunk theo câu bảo toàn tính toàn vẹn của mệnh đề thông tin, đồng thời gom gọn toàn bộ 10 tài liệu thành đúng 40 chunk vừa vặn (thay vì >100 chunk vụn), giảm thiểu đáng kể tỷ lệ nhiễu từ các khối footer website.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|---------------------------------|---------------------------|
| 1 | Mức học bổng khuyến khích học tập kì cuối cho sinh viên loại Xuất sắc ngành CLC CNTT khóa QH-2022 là bao nhiêu? *(Yêu cầu filter: audience=student)* | 4.100.000 đồng/sinh viên/tháng (theo Quyết định số 1545/QĐ-ĐHCN) | `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026` (Điều 2: Bảng định mức học bổng) |
| 2 | Mỗi suất học bổng Vallet năm 2026 dành cho sinh viên Trường ĐHCN trị giá bao nhiêu và lễ trao học bổng diễn ra ở đâu? | Trị giá 34.000.000 đồng; tổ chức tại Hội trường Nhà Thái Học, Văn Miếu – Quốc Tử Giám (58 Quốc Tử Giám, Hà Nội) lúc 07h30 ngày 23/08/2026 | `ket-qua-xet-chon-hoc-bong-vallet-2026` (Mục 2: Trị giá & Mục 5: Địa điểm trao học bổng) |
| 3 | Sinh viên cần đáp ứng những tiêu chuẩn gì về GPA, rèn luyện và ngoại ngữ để được xét chọn Học bổng Tài năng Pegatron 2027? | GPA năm học 2025-2026 từ 2.8 trở lên, kết quả rèn luyện từ loại Tốt trở lên, có khả năng dùng tiếng Anh/tiếng Trung và phải hoàn thành chứng chỉ tiếng Trung HSK3 trước khi đến thực tập tại công ty | `chuong-trinh-hoc-bong-tai-nang-pegatron-2027` (Mục 1: Đối tượng và tiêu chuẩn xét chọn) |
| 4 | Hồ sơ đăng ký học bổng Đinh Thiện Lý dành cho sinh viên năm cuối gồm những giấy tờ gì và hạn nộp là khi nào? | Đơn đăng ký online; bảng điểm tích lũy có xác nhận; bài luận tiếng Anh tối đa 500 từ; 1 thư giới thiệu; minh chứng NCKH/ngoại khóa; video giới thiệu <=3 phút; giấy tờ hoàn cảnh khó khăn (nếu có). Hạn trước 16h30 ngày 21/7/2026 | `chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027` (Mục 4: Đăng ký học bổng & Mục 5: Thời gian gửi hồ sơ) |
| 5 | Chương trình học bổng Goertek năm 2027 gồm những mô hình đào tạo nào và quyền lợi của từng mô hình là gì? | Gồm 2 mô hình: 1) Đào tạo tại VN: học bổng 60 triệu đồng, gói 21.000.000đ/SV trả 2 lần, thực tập tại Goertek Vina; 2) Đào tạo tại TQ: học bổng 80 triệu đồng, học tại ĐH Sơn Đông, miễn học phí, KTX, vé máy bay khứ hồi, gói 25.000.000đ/SV trả 2 lần | `chuong-trinh-hoc-bong-goertek-nam-2027` (Đoạn mô tả Mô hình đào tạo tại VN và TQ) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mức học bổng khuyến khích kì cuối... | `SentenceChunker` (kèm filter) | Có (Top-1, Score: 0.6994) | Đạt 2/2 điểm; filter audience='student' loại bỏ quy định chung, chunk chứa trọn vẹn mức 4.100.000đ |
| 2 | Trị giá học bổng Vallet và địa điểm... | `SentenceChunker` | Có (Top-1, Score: 0.6773) | Đạt 2/2 điểm; Top-1 trúng văn bản Vallet chính xác |
| 3 | Tiêu chuẩn GPA, rèn luyện Pegatron... | `SentenceChunker` | Có (Top-1, Score: 0.7233) | Đạt 2/2 điểm; Chunk câu gom được cả tiêu đề lẫn điều kiện GPA 2.8, rèn luyện Tốt, HSK3 |
| 4 | Hồ sơ học bổng Đinh Thiện Lý... | `SentenceChunker` | Có (Top-1, Score: 0.6726) | Đạt 2/2 điểm; Chunk câu giữ trọn vẹn cả hồ sơ 500 từ và hạn nộp 21/7/2026 |
| 5 | Mô hình đào tạo Goertek năm 2027... | `SentenceChunker` | Có (Top-1, Score: 0.7160) | Đạt 2/2 điểm; Top-1 chứa đầy đủ cả 2 mô hình đào tạo VN (60tr) và TQ (80tr) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Rất hữu ích, đặc biệt ở **Câu hỏi 1**. Khi áp dụng bộ lọc `audience="student"`, hệ thống loại bỏ hoàn toàn các văn bản quy chế mang tính định hướng chung toàn trường (`audience="all"` như `quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap.md`), giúp thu hẹp không gian tìm kiếm và đưa quyết định cấp học bổng thực tế của kỳ tốt nghiệp tháng 06/2026 lên thẳng Top-1 với độ tin cậy tuyệt đối.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Sức mạnh của ranh giới câu tự nhiên (Sentence Boundaries):** Việc chia tách theo ranh giới câu kết hợp gom 3 câu (`max_sentences_per_chunk=3`) giải quyết triệt để bài toán phân mảnh thông tin, giúp mối quan hệ giữa chủ thể (tên học bổng) và điều kiện thuộc tính (GPA, số tiền, hạn nộp) luôn được bảo toàn trọn vẹn trong một vector embedding.
> 2. **Kiểm soát mật độ chunk trong Vector Store:** Việc chuyển từ các chunker cắt vụn (>100 chunks) sang Sentence Chunker (đúng 40 chunks) giúp giảm thiểu đáng kể nguy cơ xung đột ngữ nghĩa (*semantic collision*) từ các đoạn boilerplate chân trang website.
> 3. **Tác động của Embedding Model:** `MockEmbedder` (hash ngẫu nhiên) chỉ cho kết quả may rủi (~3/10), trong khi mô hình ngữ nghĩa thực tế `text-embedding-3-small` (OpenAI) kết hợp SentenceChunker đưa điểm retrieval lên mức tuyệt đối **10/10 điểm (100% Top-1)**.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập 10 tài liệu, chiến lược chunking quyết định trực tiếp tới khả năng hiểu của Vector Search:
> - `FixedSizeChunker` dễ làm gãy đôi các bảng số liệu tài chính hoặc điều khoản học bổng, khiến số tiền và đối tượng bị tách rời sang 2 chunk khác nhau (chỉ đạt 4/10 điểm).
> - `RecursiveChunker` bảo toàn được ranh giới đoạn văn tốt hơn nhưng ở kích thước nhỏ vẫn có thể tách rời các câu quan trọng (đạt 6/10 điểm).
> - `SentenceChunker` phát huy tối đa ưu thế với văn phong hành chính tiếng Việt, giữ nguyên vẹn mệnh đề và logic văn bản, mang lại chất lượng truy xuất vượt trội nhất (đạt 10/10 điểm).

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> 1. Xây dựng pipeline tiền xử lý (HTML/Markdown Cleaning) để cắt bỏ toàn bộ breadcrumbs, menu điều hướng và widget "Bài viết liên quan" trước khi đưa vào kho dữ liệu.
> 2. Bổ sung Document Title vào mọi chunk (`f"[{doc_title}] > {content}"`) để tăng cường độ liên kết ngữ cảnh ngay cả khi câu văn không nhắc lại tên văn bản.
> 3. Trích xuất metadata phong phú hơn (như `scholarship_name`, `deadline`, `min_gpa`) để tận dụng sức mạnh của Hybrid Search kết hợp Metadata Pre-filtering.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
