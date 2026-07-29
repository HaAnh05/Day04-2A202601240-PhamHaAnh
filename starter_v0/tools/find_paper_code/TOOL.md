# find_paper_code

## Target
Tìm kiếm mã nguồn mở (official / community implementation) đính kèm bài báo nghiên cứu từ PapersWithCode và GitHub.

## Parameters
- `query`: Tên bài báo (Paper Title), arXiv ID, hoặc từ khóa tìm kiếm bài báo.
- `max_results`: Số lượng repo tối đa trả về (mặc định: 5).

## Returns
TRẢ VỀ JSON dạng:
```json
{
  "tool": "find_paper_code",
  "query": "Attention Is All You Need",
  "total_found": 3,
  "repositories": [
    {
      "name": "tensorflow/tensor2tensor",
      "url": "https://github.com/tensorflow/tensor2tensor",
      "stars": 12500,
      "is_official": true,
      "framework": "TensorFlow"
    }
  ]
}
```
