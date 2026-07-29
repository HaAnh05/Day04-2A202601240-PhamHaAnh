# Day 04 Lab v2 Report — Research Agent (Research Paper Scout)

> File này gồm 2 phần:
> - **PHẦN A — Giới thiệu agent**: Tài liệu giới thiệu ngắn gọn agent, phân công công việc, danh sách tool, kịch bản demo và link trải nghiệm.
> - **PHẦN B — Chi tiết / Bằng chứng**: Thống kê kết quả đánh giá v0–v3, phân tích nguyên nhân lỗi, 10 eval cases nhóm và bài học rút ra.

## Team Information & Work Distribution

- **Tên Nhóm**: Research Paper Scout Team
- **Thành viên**: Phạm Hà Anh (Trưởng nhóm), Lê Nguyễn Phước Thành
- **Provider & Model**: Gemini (`gemini-3.1-flash-lite`)
- **Kết quả Eval Base**: **100% Accuracy (20/20 PASS)**

### 📊 Bảng Phân Công Công ViệcChi Tiết (Task Assignment)

| Thành viên | Vai trò | Công việc thực hiện | File/Deliverable liên quan |
|---|---|---|---|
| **Phạm Hà Anh** | **Trưởng nhóm** (Leader & Core Engine) | • Thiết kế & Tối ưu System Prompt qua 4 phiên bản (v0 ➔ v3)<br>• Khai báo danh sách & tham số schema của Tools<br>• Phát triển Custom Tool 100% `find_paper_code`<br>• Đăng ký & Tích hợp Tool vào Engine chính<br>• Biên soạn 10 Team Eval Cases (5 single + 5 multi)<br>• Cấu hình Gemini Provider & Tự động hóa Benchmark<br>• Phân tích nguyên nhân lỗi & Ghi log phiên bản | • `artifacts/system_prompt.md`<br>• `artifacts/tools.yaml`<br>• `tools/find_paper_code/`<br>• `tools/__init__.py`<br>• `data/eval_group.json`<br>• `providers/gemini_provider.py`<br>• `artifacts/version_log.csv` |
| **Lê Nguyễn Phước Thành** | **Thành viên** (UX/UI & Workflow Visualizer) | • Thiết kế giao diện UI Streamlit nền trắng tối giản<br>• Xử lý hiển thị Trace Log gọi Tool real-time & Chat Session<br>• Thiết kế & Vẽ Sơ đồ Luồng xử lý Workflow tương tác<br>• Quản lý & Tạo dữ liệu Transcript phiên làm việc<br>• Biên soạn 4 kịch bản Demo Rehearsal cho Showdown<br>• Tổng hợp & Trình bày Báo cáo Phần A & Phần B | • `app.py`<br>• `workflow.html`<br>• `artifacts/workflow.html`<br>• `transcripts/*.transcript.json`<br>• `artifacts/REPORT.md` |

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent (Chủ đề **Research Paper Scout**) là một trợ lý thông minh chuyên tìm kiếm, trích xuất nội dung bài báo khoa học (arXiv), tìm kiếm mã nguồn mở (official / community code implementation trên GitHub/PapersWithCode), tra cứu thông tin tin tức thời sự trên web và bài đăng mạng xã hội, đồng thời tuân thủ nghiêm ngặt các ranh giới hỏi lại (`clarify`) và xác nhận trước khi đăng bài.

**Link dùng thử (truy cập được trong showdown):**
- **URL Local UI**: `http://localhost:8501` (Khởi chạy bằng `.venv\Scripts\python.exe -m streamlit run app.py`)
- **Trang Workflow Luồng Xử Lý**: `workflow.html` (Hoặc file `artifacts/workflow.html`)

## A2. Tool agent có

Danh sách đầy đủ 11 Tools Agent đang sử dụng trong chủ đề **Research Paper Scout**:

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `find_paper_code` | **Tra cứu mã nguồn mở (official / community GitHub repos) đi kèm bài báo khoa học dựa trên tên bài báo, arXiv ID hoặc từ khóa.** | **Có (100%)** |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv theo từ khóa chủ đề và tiêu chí sắp xếp. | Không |
| `paper_text` | Đọc và trích xuất nội dung văn bản chi tiết từ PDF bài báo arXiv (dựa theo URL hoặc arXiv ID). | Không |
| `lookup` | Tìm kiếm tin tức/thông tin tổng hợp trên Internet (ép query tối giản ngắn gọn). | Không |
| `fetch` | Đọc nội dung văn bản trực tiếp từ một đường dẫn URL bài viết cụ thể. | Không |
| `timeline` | Lấy bài đăng Twitter gần đây của tài khoản theo screenname/handle (VD: sama, elonmusk). | Không |
| `social_search` | Tìm kiếm bài đăng trên mạng xã hội Twitter theo từ khóa (Latest hoặc Top). | Không |
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (response_type="text") hoặc xin xác nhận (response_type="yes_no") trước hành động nhạy cảm (Telegram). | Không |
| `format` | Trình bày danh sách items đã thu thập thành bản tin tóm tắt Markdown digest. | Không |
| `policy` | Tra cứu sổ tay quy định nội bộ công ty. | Không |
| `send` | Đăng bản tin lên kênh Telegram (chỉ kích hoạt khi người dùng đã xác nhận Yes/No qua clarify). | Không |

## A3. Câu hỏi mẫu để thử

1. **Tìm code bài báo**: *"Tìm mã nguồn PyTorch/GitHub cho bài báo Attention Is All You Need giúp mình"*
2. **Nghiên cứu arXiv**: *"Tìm các bài báo mới nhất về Mixture of Experts trên arXiv và đọc trích đoạn bài báo 2312.00752"*
3. **Tra cứu tin tức & Twitter**: *"Tin tức AI hôm nay có gì nổi bật? Tìm thêm các tweet phổ biến nhất về GPT-5"*
4. **Kiểm tra ranh giới hỏi lại**: *"Tóm tắt 5 tweet mới nhất giúp mình"* ➔ Agent sẽ gọi `clarify` để hỏi tên tài khoản.
5. **Kiểm tra ranh giới xác nhận**: *"Đăng bản tin này lên Telegram giúp mình"* ➔ Agent sẽ gọi `clarify` (yes/no) để xin xác nhận trước khi gửi.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| **1. Tìm code bài báo** | `find_paper_code(query="Attention Is All You Need")` | v0 chưa có tool này; v3 hỗ trợ tự động truy vấn GitHub API và lọc repository uy tín. | `runs/v3_B_base_gemini_20260729T163314814079.json` |
| **2. Xử lý thiếu thông tin** | `clarify(question="...", response_type="text")` | v0 tự đoán bừa handle `sama`; v1-v3 biết tự hỏi xin tên tài khoản thay vì đoán. | `runs/v1_B_base_gemini_20260729T145509486209.json` |
| **3. Xác nhận trước khi gửi** | `clarify(question="...", response_type="yes_no")` | v0 tự ý gọi `send` trực tiếp; v3 bắt buộc hỏi xác nhận yes/no trước khi thực thi. | `runs/v3_B_base_gemini_20260729T163314814079.json` |
| **4. Từ chối câu hỏi ngoài phạm vi** | `no_tool` (Trả lời/Từ chối trực tiếp) | v0 gọi `send`/`policy` vô lý cho bài toán tích phân `x^2`; v2-v3 từ chối không gọi tool. | `runs/v3_B_base_gemini_20260729T163314814079.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

Dữ liệu được trích xuất trực tiếp từ `artifacts/version_log.csv` và các file `runs/*.json`:

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| **v0** | Baseline mặc định | Baseline chưa có quy tắc ranh giới và routing rõ ràng | case_accuracy | 0.00% | 42.86% | `runs/v0_B_base_gemini_20260729T145429243101.json` |
| **v1** | Cập nhật `system_prompt.md` & `tools.yaml` | Bổ sung quy tắc clarify và map handle giúp sửa ranh giới | case_accuracy | 42.86% | 75.00% | `runs/v1_B_base_gemini_20260729T145509486209.json` |
| **v2** | Bổ sung ranh giới No-tool | Thiết lập ranh giới câu hỏi ngoài phạm vi nâng độ chính xác Gemini | case_accuracy | 75.00% | 95.00% | `runs/v3_B_base_gemini_20260729T162104940507.json` |
| **v3** | Thêm ví dụ Telegram & quy tắc Query | Quy định rõ `response_type="yes_no"` cho Telegram và query ngắn gọn giúp đạt 100% | case_accuracy | 95.00% | **100.0%** | `runs/v3_B_base_gemini_20260729T163314814079.json` |

## B2. Failure analysis

Phân tích các ca thất bại thực tế từ file run JSON và giải pháp đã khắc phục:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `send(...)` (ở v0) | Model gọi nhầm tool `send` để gửi câu trả lời bài toán tích phân `x^2`. | Thêm quy tắc No-Tool cho toán học & coding trong `system_prompt.md`. |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` (ở v0) | Thiếu tên tài khoản nhưng agent tự đoán handle `sama`. | Yêu cầu bắt buộc gọi `clarify(response_type="text")` khi không có tên người dùng. |
| `R12_confirm_before_send` | `wrong_boundary` | `clarify(question="...")` thiếu `response_type` | Gemini gọi clarify nhưng thiếu tham số `response_type="yes_no"`. | Bổ sung ví dụ mẫu cụ thể cho các từ khóa đăng bài/Telegram với `response_type="yes_no"`. |
| `R03_web_news_routing` | `wrong_tool` | `lookup(query="AI news today")` | Query chứa từ thừa "news today" khiến lệch tham số mong đợi. | Quy định tham số `query` cho `lookup` chỉ chứa từ khóa cốt lõi ("AI"). |

## B3. Team eval cases

Danh sách 10 test cases thiết kế riêng cho nhóm trong [data/eval_group.json](file:///d:/Vin_AI/Day04-2A202601240-PhamHaAnh/starter_v0/data/eval_group.json):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_find_paper_code_single` | Tìm code cho bài báo Attention Is All You Need | `find_paper_code(query="Attention Is All You Need")` | PASS |
| `G02_arxiv_paper_search` | Tìm bài báo arXiv theo chủ đề Mixture of Experts | `papers(query="Mixture of Experts")` | PASS |
| `G03_arxiv_text_extraction` | Trích nội dung bài báo arXiv ID 2312.00752 | `paper_text(arxiv_url="2312.00752")` | PASS |
| `G04_out_of_scope_cooking` | Câu hỏi nấu ăn ngoài phạm vi research | `no_tool` (Từ chối trực tiếp) | PASS |
| `G05_clarify_missing_paper_title` | Thiếu tên bài báo khi nhờ tìm code | `clarify(response_type="text")` | PASS |
| `G06_multiturn_paper_to_code` | Multi-turn: chuyển từ tìm bài báo sang tìm code | `find_paper_code(query="LoRA Fine-tuning")` | PASS |
| `G07_multiturn_paper_text_read` | Multi-turn: hỏi bài báo rồi yêu cầu đọc nội dung | `paper_text(arxiv_url="2305.14314")` | PASS |
| `G08_multiturn_carry_limit_code` | Multi-turn: carry tên bài báo và sửa max_results=3 | `find_paper_code(query="LLaMA 3", max_results=3)` | PASS |
| `G09_multiturn_confirm_telegram_paper` | Multi-turn: đăng bài báo lên Telegram | `clarify(response_type="yes_no")` | PASS |
| `G10_multiturn_switch_paper_to_web` | Multi-turn: chuyển từ arXiv sang tìm tin tức web | `lookup(query="GPT-4", topic="news")` | PASS |

## B4. Live chat evidence

Nhật ký kiểm thử tương tác thực tế từ các file trong `transcripts/`:

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| **Turn 1: Tìm code bài báo** | v3 | `find_paper_code(query="Attention Is All You Need")` | `transcripts/v0_gemini_20260729T161108754955.transcript.json` | Agent trả về các repository GitHub chất lượng kèm số lượng sao. |
| **Turn 2: Yêu cầu thiếu URL** | v3 | `clarify(question="...", response_type="text")` | `transcripts/v0_gemini_20260729T161108754955.transcript.json` | Agent dừng lại hỏi xin URL chứ không đoán ngẫu nhiên. |
| **Turn 3: Yêu cầu gửi Telegram** | v3 | `clarify(question="...", response_type="yes_no")` | `transcripts/v0_gemini_20260729T161108754955.transcript.json` | Agent hiển thị câu hỏi xác nhận Yes/No trước khi hành động. |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **Must-have: tool mới đầu tiên** | `tools/find_paper_code/tool.py` | Tự động tìm kiếm mã nguồn bài báo từ GitHub API & PapersWithCode, trả về danh sách repos, số sao, tác giả và framework. | Giới hạn Rate Limit của GitHub API; cần fallback từ khóa tìm kiếm khi query quá chi tiết. |
| **Optional built-in** | `tools/papers/tool.py` | Tra cứu chính xác danh sách bài báo khoa học từ arXiv API theo từ khóa và sắp xếp ngày đăng. | arXiv API yêu cầu khoảng nghỉ tối thiểu 3 giây giữa các lượt gọi. |

## B6. Reflection

- **Sửa đổi trong `system_prompt.md`**: Đóng vai trò quyết định trong việc thiết lập ranh giới khi nào được gọi tool, khi nào KHÔNG gọi tool (No-Tool), quy tắc map tên sang Handle, và cách xử lý ngữ cảnh đối thoại nhiều lượt.
- **Sửa đổi trong `tools.yaml`**: Giúp định nghĩa rõ ràng mô tả công dụng của từng tool và convention của tham số (ví dụ `topic: news`, `search_type: Top`), giúp LLM hiểu đúng intent để điền argument chính xác.
- **Lỗi cần review thủ công**: Các ca rate-limit `429` của LLM API hoặc lỗi thiếu API key của các công cụ bên ngoài cần được phân biệt rõ với lỗi routing của Agent.
- **Hướng cải tiến tiếp theo**: Tích hợp thêm bộ nhớ lưu trữ kết quả bài báo khoa học bằng Vector DB nội bộ và tự động tổng hợp so sánh giữa bài báo và mã nguồn đi kèm.
