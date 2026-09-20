# Báo Cáo Cá Nhân - Lab 7: Embedding & Vector Store

**Họ tên:** Trần Thu Phương  
**Nhóm:** G01_T141  
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) - Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần giống nhau trong không gian vector. Với văn bản, điều này thường cho thấy hai câu/đoạn đang nói về nội dung hoặc ý nghĩa gần nhau, dù cách diễn đạt có thể khác.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần nộp hồ sơ học bổng trước hạn.
- Câu B: Người học phải gửi giấy tờ xét học bổng đúng thời gian quy định.
- Tại sao tương đồng: Hai câu đều nói về việc nộp hồ sơ/giấy tờ học bổng và yếu tố thời hạn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên cần nộp hồ sơ học bổng trước hạn.
- Câu B: Hôm nay thời tiết Hà Nội có mưa vào buổi chiều.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau, một câu về quy trình học bổng, một câu về thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector nên phản ánh tốt hơn mức độ giống nhau về ý nghĩa. Euclidean distance dễ bị ảnh hưởng bởi độ lớn vector, trong khi với text embeddings ta thường quan tâm văn bản có cùng ngữ nghĩa hay không hơn là độ dài/độ lớn biểu diễn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((độ_dài_tài_liệu - overlap) / (chunk_size - overlap))`  
> Thay số: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`  
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi `overlap=100`: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`, tức số chunk tăng từ 23 lên **25 chunks**. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, giảm nguy cơ cắt mất câu hoặc tách rời thông tin quan trọng, nhưng đổi lại số chunk và chi phí truy xuất tăng lên.

---

## 2. Hướng tiếp cận của tôi (My Approach) - Cá nhân (10 điểm)

Giải thích cách tiếp cận của tôi khi lập trình các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** - hướng tiếp cận:
> Tôi dùng regex `r"(?<=[.!?])(?:[ \t]+|\r?\n+)"` để tách câu tại khoảng trắng hoặc xuống dòng ngay sau các dấu `.`, `!`, `?`. Sau khi tách, từng câu được `strip()` để bỏ khoảng trắng thừa rồi gom tối đa `max_sentences_per_chunk` câu vào một chunk. Trường hợp văn bản rỗng hoặc chỉ có khoảng trắng trả về `[]`; tham số `max_sentences_per_chunk` cũng được chặn tối thiểu là 1 để tránh bước nhảy không hợp lệ.

**`RecursiveChunker.chunk` / `_split`** - hướng tiếp cận:
> Thuật toán thử tách văn bản theo thứ tự ưu tiên các separator tự nhiên: đoạn văn `\n\n`, dòng `\n`, câu `. `, từ `" "`, rồi cuối cùng là cắt cứng theo ký tự. Base case là khi đoạn hiện tại đã ngắn hơn hoặc bằng `chunk_size` thì trả về luôn đoạn đó. Nếu một phần sau khi tách vẫn quá dài, `_split` gọi đệ quy với separator tiếp theo; sau đó các phần nhỏ được ghép lại miễn là không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** - hướng tiếp cận:
> `EmbeddingStore` lưu trữ trong bộ nhớ bằng danh sách các record gồm `id`, `content`, `metadata`, `embedding` và `index`. Khi thêm tài liệu, hàm tạo embedding cho từng `Document.content`, đồng thời bảo đảm metadata có `doc_id` để phục vụ xóa/cập nhật theo tài liệu gốc. Khi tìm kiếm, query cũng được embed rồi so sánh với từng chunk bằng tích vô hướng (`dot product`); vì các embedding mock đã được chuẩn hóa, dot product tương đương cosine similarity.

**`search_with_filter` + `delete_document`** - hướng tiếp cận:
> `search_with_filter` lọc metadata trước, tức chỉ giữ các record thỏa tất cả cặp key-value trong `metadata_filter`, sau đó mới tính điểm tương tự trên tập ứng viên đã thu hẹp. Cách này giúp các câu hỏi có ràng buộc như `audience="student"` tránh lấy nhầm tài liệu không dành cho sinh viên. `delete_document` xóa bằng cách dựng lại danh sách record và loại bỏ tất cả chunk có `metadata["doc_id"]` trùng `doc_id` cần xóa, rồi trả về `True` nếu kích thước store giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** - hướng tiếp cận:
> `KnowledgeBaseAgent.answer` trước hết truy xuất top-k chunk liên quan từ `EmbeddingStore`, sau đó tạo context có đánh số `[1]`, `[2]`, `[3]` kèm nguồn lấy từ `source_url`, `source` hoặc `doc_id`. Prompt yêu cầu LLM chỉ trả lời dựa trên phần context, nếu không đủ thông tin thì nói không tìm thấy, và trích dẫn bằng số nguồn. Nhờ vậy câu trả lời theo mô hình RAG có grounding rõ hơn và dễ kiểm tra lại chunk đã dùng.

---

## 3. Hoàn thiện code (Core Implementation) - Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
# Kết quả của: pytest tests/ -v
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                       [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                         [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                          [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                               [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                               [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                     [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                      [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                    [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                      [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                      [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                 [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                             [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                       [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                              [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                  [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                            [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                  [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                      [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                        [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                          [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                     [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                       [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                           [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                        [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                 [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                           [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                       [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                  [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                      [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                            [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                      [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                   [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                 [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                    [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                               [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                        [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                              [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                  [100%]
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) - Cá nhân (5 điểm)

Các điểm dưới đây dùng `MockEmbedder` mặc định trong repo và `compute_similarity()`/dot product trên vector đã chuẩn hóa. Với mock embedding, điểm phản ánh tính ổn định của pipeline hơn là ngữ nghĩa thật sự.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học bổng Vallet trị giá 34 triệu đồng. | Học bổng Vallet trị giá 34 triệu đồng. | cao | 1.0000 | Có |
| 2 | Học bổng Vallet trị giá 34 triệu đồng. | Suất học bổng Vallet có giá trị 34.000.000 đồng. | cao | -0.1106 | Không |
| 3 | GPA tối thiểu để xét học bổng Pegatron là 2.8. | Thời tiết Hà Nội hôm nay có mưa vào buổi chiều. | thấp | 0.0897 | Có |
| 4 | Chunking chia tài liệu thành các đoạn nhỏ. | Cơ sở dữ liệu vector lưu trữ embedding để tìm kiếm tương tự. | thấp | 0.0557 | Có |
| 5 | Metadata audience=student giúp lọc tài liệu cho sinh viên. | Bộ lọc metadata thu hẹp kết quả theo đối tượng người học. | cao | -0.1149 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 2 và cặp 5 bất ngờ nhất vì về mặt ngữ nghĩa chúng rất gần nhau, nhưng `MockEmbedder` lại cho điểm âm. Nguyên nhân là mock embedding dùng MD5 để tạo vector quyết định, không học quan hệ ngữ nghĩa giữa các câu. Điều này cho thấy test pipeline có thể dùng mock để kiểm tra luồng xử lý, nhưng đánh giá chất lượng truy xuất thật cần embedding đa ngôn ngữ hoặc embedding API có khả năng biểu diễn ý nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) - Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src`. **5 câu hỏi này trùng với bộ câu hỏi trong `REPORT_NHOM.md`.**

**Embedding backend:** `text-embedding-3-small` cho phần so sánh chiến lược trong nhóm; khi không có API key, mã nguồn tự fallback về `MockEmbedder` để chạy test và demo cơ bản.

**Chiến lược cá nhân:** `RecursiveChunker(chunk_size=300)`. Tôi chọn cách tách theo ranh giới tự nhiên (`\n\n`, `\n`, `. `, khoảng trắng) vì tài liệu học bổng/quy định đại học có nhiều đoạn, gạch đầu dòng và điều kiện nhỏ. Metadata quan trọng gồm `doc_id`, `source_url`, `retrieved_at`, `document_version`, `audience`, `category`, `department`; riêng câu 1 dùng `metadata_filter={"audience": "student"}`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mức học bổng khuyến khích học tập kì cuối cho sinh viên loại Xuất sắc ngành CLC CNTT khóa QH-2022 là bao nhiêu? | Quyết định cấp học bổng KKHT kì cuối, phần bảng định mức cho ngành CLC CNTT QH-2022 | 0.6184 | Có | Trả lời đúng: 4.100.000 đồng/sinh viên/tháng |
| 2 | Mỗi suất học bổng Vallet năm 2026 dành cho sinh viên Trường ĐHCN trị giá bao nhiêu và lễ trao học bổng diễn ra ở đâu? | Tài liệu Vallet, chunk nêu trị giá học bổng 34.000.000 đồng | 0.5742 | Có nhưng thiếu một phần | Trả lời đúng trị giá, nhưng địa điểm lễ trao nằm ở chunk khác trong top-3 nên câu trả lời chưa đủ chi tiết |
| 3 | Sinh viên cần đáp ứng những tiêu chuẩn gì về GPA, rèn luyện và ngoại ngữ để được xét chọn Học bổng Tài năng Pegatron 2027? | Thông báo Pegatron, phần đối tượng và tiêu chuẩn xét chọn | 0.6418 | Có | Trả lời đúng GPA từ 2.8, rèn luyện từ loại Tốt, có tiếng Anh/Trung và hoàn thành HSK3 trước thực tập |
| 4 | Hồ sơ đăng ký học bổng Đinh Thiện Lý dành cho sinh viên năm cuối gồm những giấy tờ gì và hạn nộp là khi nào? | Thông báo Đinh Thiện Lý, chunk liệt kê thành phần hồ sơ | 0.5667 | Có nhưng chưa trọn vẹn | Trả lời được các giấy tờ chính, nhưng hạn 16h30 ngày 21/7/2026 bị tách sang chunk sau nên câu trả lời thiếu mốc thời gian |
| 5 | Chương trình học bổng Goertek năm 2027 gồm những mô hình đào tạo nào và quyền lợi của từng mô hình là gì? | Thông báo Goertek, chunk giới thiệu chương trình và một phần mô hình đào tạo | 0.5529 | Chưa đủ | Chunk top-3 không gom đủ cả hai mô hình Việt Nam/Trung Quốc và quyền lợi tương ứng nên câu trả lời bị thiếu |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5. **Tổng điểm:** 6 / 10.

**Failure case:** Câu 5 về học bổng Goertek là lỗi rõ nhất. `RecursiveChunker(chunk_size=300)` chia văn bản thành các đoạn nhỏ nên thông tin về hai mô hình đào tạo và quyền lợi đi kèm bị tách rời; top-3 có nhắc đúng chương trình nhưng không đủ bằng chứng để trả lời trọn vẹn. Cách cải thiện là tăng `chunk_size` lên khoảng 700-1000, gắn tiêu đề tài liệu/mục vào đầu mỗi chunk, hoặc dùng `SentenceChunker(max_sentences_per_chunk=3)` như chiến lược tốt nhất của nhóm để giữ trọn các mệnh đề điều kiện và quyền lợi.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng đúng `doc_id` chưa chắc đã đủ để trả lời đúng; chunk phải chứa đúng bằng chứng, số liệu và điều kiện cần trích xuất. Chiến lược `SentenceChunker` của thành viên khác hiệu quả hơn với văn bản hành chính vì nó giữ được quan hệ giữa chủ thể, tiêu chuẩn, số tiền và thời hạn trong cùng một đơn vị ngữ nghĩa. Metadata filter cũng rất hữu ích, đặc biệt ở câu 1, vì nó giúp loại bớt tài liệu quy định chung không dành riêng cho sinh viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation - tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |

