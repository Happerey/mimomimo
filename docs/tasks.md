# RAG 课程助手 — 开发任务清单

## 任务依赖图

```
Task 1 (补充停用词 + retrieve单元测试)
    ↓
Task 2 (更新test_basic + 框架Stub) → Task 3 (load_chunks) → Task 4 (retrieve实现)
                                                                    ↓
                                                            Task 5 (answer单元测试) → Task 6 (answer实现)
                                                                                           ↓
Task 7 (Mock Server连通性) ─────────────────────────────────────────────────────────→ Task 8 (main.py)
                                                                                           ↓
                                                                                   Task 9 (集成测试 + 微调questions.json)
                                                                                           ↓
                                                                                   Task 10 (验收收尾)
```

---

## Task 1：补充停用词常量 + 编写 retrieve 单元测试

**目标**：补充 spec.md 配置常量，Test-First 先写测试

**产出文件**：
- `docs/spec.md`（补充停用词常量）
- `tests/test_retrieve.py`

**实现内容**：
1. 在 spec.md 的"配置常量"章节补充停用词列表：
   ```
   | `STOPWORDS` | 的、了、吗、呢、要、么、什、我、你、是、在、有、和、与 | 预处理时剔除的停用词 |
   ```
2. 编写 retrieve 单元测试：
   - test_load_chunks：验证切片函数返回 10 个 chunk，每个 chunk 包含 `[faq-XX]`
   - test_retrieve_exact_match：输入"什么是可复核交付？"，返回 Top1 的 id 为 `faq-01`，且结果为字典列表 `[{"id", "content", "score"}, ...]`
   - test_retrieve_cross_paragraph：输入"Spec中的非目标和AI过度设计有什么关系？"，返回结果的 id 包含 `faq-04` 和/或 `faq-10`
   - test_retrieve_out_of_domain：输入"奖学金政策是什么？"，返回空列表
   - test_retrieve_empty_input：输入空字符串，返回空列表
   - test_retrieve_stopwords：验证停用词（的、了、吗等）被过滤，不影响分数
   - test_retrieve_score_order：验证结果按 score 降序排列
   - test_retrieve_binary_hit：验证同一关键词重复出现只计 1 分

**验证命令**：
```bash
python -m pytest tests/test_retrieve.py -v
```

**完成标准**：
- spec.md 包含 STOPWORDS 常量
- 测试文件可运行（预期全部 FAIL，因为 retrieve 未实现）

---

## Task 2：更新 test_basic.py + 搭建框架 Stub

**目标**：更新接口契约检查，创建空函数签名

**产出文件**：
- `tests/test_basic.py`（更新）
- `src/retrieve.py`（空签名）
- `src/answer.py`（空签名）
- `src/main.py`（空签名）

**实现内容**：
1. 更新 test_basic.py 的接口契约检查：
   - `retrieve()` 返回列表，每个元素是字典且包含 `id`、`content`、`score` 键
   - `answer()` 返回字典，包含 `answer`（str）和 `sources`（list）键
2. 创建空函数签名：
   ```python
   # retrieve.py
   def load_chunks(filepath):
       return []
   
   def retrieve(question, chunks):
       return []
   
   # answer.py
   def answer(question, chunks):
       return {"answer": "", "sources": []}
   
   # main.py
   def main():
       pass
   ```

**验证命令**：
```bash
python tests/test_basic.py
```

**完成标准**：9 个测试全部 PASS

---

## Task 3：实现 load_chunks() 模块

**目标**：实现 FAQ 文件切片功能

**产出文件**：`src/retrieve.py`（load_chunks 函数）

**实现内容**：
- 读取 `data/course-faq.md`
- 用正则 `\n(?=##\s*\[faq-\d{2}\])` 分割
- 提取每个 chunk 的 id（如 `faq-01`）
- 返回 10 个 chunk 列表，每个元素为 `{"id": "faq-01", "content": "完整chunk内容"}`

**验证命令**：
```bash
python -m pytest tests/test_retrieve.py::test_load_chunks -v
```

**完成标准**：test_load_chunks PASS

---

## Task 4：实现 retrieve 核心算法

**目标**：实现短语切分、停用词过滤、布尔命中计分

**产出文件**：`src/retrieve.py`（retrieve 函数）

**实现内容**：
- 按标点（逗号、句号、空格、问号、感叹号）切分问题为短语列表
- 剔除长度 <= 1 的字符
- 剔除停用词（从 spec.md 的 STOPWORDS 常量读取）
- 布尔命中计分：统计有效关键词在 chunk 中出现的去重数量
- 按 score 降序取 Top3（仅返回 score > 0 的结果）
- 返回格式：`[{"id": "faq-01", "content": "...", "score": 3}, ...]`

**验证命令**：
```bash
python -m pytest tests/test_retrieve.py -v
```

**完成标准**：test_retrieve.py 全部 PASS

---

## Task 5：编写 answer 单元测试

**目标**：用 unittest.mock 模拟 HTTP 请求，不依赖真实 Server

**产出文件**：`tests/test_answer.py`

**测试内容**：
- test_answer_normal：mock LLM 返回正常回答，验证输出格式 `{answer, sources}`
- test_answer_reject_low_score：Top1.score < 2 时返回拒答文案
- test_answer_reject_ambiguous：Top1 - Top2 <= 1 时返回模糊拒答文案
- test_answer_empty_chunks：chunks 为空时返回拒答文案
- test_answer_prompt_format：验证拼接的 Prompt 包含 System Prompt 和【参考资料】格式
- test_answer_sources_extraction：验证 sources 从 retrieve 结果正确提取 id 列表

**验证命令**：
```bash
python -m pytest tests/test_answer.py -v
```

**完成标准**：测试文件可运行（预期全部 FAIL，因为 answer 未实现）

---

## Task 6：实现 answer 模块

**目标**：实现拒答判断、Prompt 拼接、LLM 调用

**产出文件**：`src/answer.py`

**实现内容**：
- 调用 `load_chunks()` 和 `retrieve()` 获取 Top3
- 拒答判断：
  - top_results 为空 → 资料外拒答
  - top_results[0]["score"] < 2 → 资料外拒答
  - top_results[0]["score"] - top_results[1]["score"] <= 1 → 模糊拒答
- 拼接 Prompt：
  - System Prompt：严格基于资料回答，不能编造
  - User Prompt：【参考资料1/2/3】格式 + 用户问题
- 调用 LLM Mock（urllib.request POST 请求）
- 提取 sources：`[r["id"] for r in top_results]`
- 返回 `{answer, sources}`

**验证命令**：
```bash
python -m pytest tests/test_answer.py -v
```

**完成标准**：test_answer.py 全部 PASS

---

## Task 7：验证 Mock Server 连通性

**目标**：确保 Mock Server 可启动并响应请求

**产出文件**：无（验证现有 llm-mock/mock_server.py）

**验证步骤**：
1. 后台启动 Mock Server
2. 等待 2 秒确保服务就绪
3. 发送 POST 请求到 `/v1/chat/completions`
4. 验证响应包含 `choices` 字段
5. 关闭 Mock Server

**验证命令**（Windows PowerShell）：
```powershell
# 启动 Server（后台）
Start-Process -FilePath "python" -ArgumentList "llm-mock/mock_server.py" -WindowStyle Hidden
Start-Sleep -Seconds 2

# 发送测试请求
Invoke-RestMethod -Uri "http://localhost:9876/v1/chat/completions" -Method Post -ContentType "application/json" -Body '{"model":"mock","messages":[{"role":"user","content":"什么是RAG？"}]}'

# 关闭 Server
Stop-Process -Name "python" -ErrorAction SilentlyContinue
```

**完成标准**：响应 JSON 包含 `choices` 数组

---

## Task 8：实现 main.py CLI 入口

**目标**：实现命令行入口，支持 `python src/main.py "问题"` 调用

**产出文件**：`src/main.py`

**实现内容**：
- 解析 `sys.argv[1]` 获取问题
- 若问题为空或未提供，打印"请输入您的问题"并退出
- 调用 `load_chunks("data/course-faq.md")` 获取 chunks
- 调用 `answer(question, chunks)` 获取结果
- 打印 `result["answer"]`
- 若 `result["sources"]` 非空，打印"来源: faq-01, faq-02"

**验证命令**（Windows PowerShell）：
```powershell
# 启动 Mock Server（后台）
Start-Process -FilePath "python" -ArgumentList "llm-mock/mock_server.py" -WindowStyle Hidden
Start-Sleep -Seconds 2

# 测试正常问题
python src/main.py "什么是可复核交付？"

# 测试资料外问题
python src/main.py "奖学金政策是什么？"

# 测试空输入
python src/main.py ""

# 关闭 Server
Stop-Process -Name "python" -ErrorAction SilentlyContinue
```

**完成标准**：
- 正常问题输出包含"可复核"和"来源: faq-01"
- 资料外问题输出"知识库中没有"
- 空输入输出"请输入您的问题"

---

## Task 9：集成测试 + 微调 questions.json

**目标**：用 questions.json 的 10 个问题做端到端验收，根据结果微调测试用例

**产出文件**：
- `tests/test_integration.py`（新建）
- `tests/questions.json`（可能微调）

**实现内容**：
1. 编写集成测试脚本：
   - 读取 questions.json
   - 对每个问题调用 `answer()`
   - 验证输出类型（answer_with_source / refuse / prompt_input）
   - 验证 expected_keywords 是否出现在回答中
   - 验证 expected_source 是否在 sources 中
2. 运行测试，若某些用例失败：
   - 分析是检索算法问题还是测试用例问题
   - 若是测试用例的 expected_keywords 不匹配实际输出，微调 questions.json

**验证命令**（Windows PowerShell）：
```powershell
# 启动 Mock Server（后台）
Start-Process -FilePath "python" -ArgumentList "llm-mock/mock_server.py" -WindowStyle Hidden
Start-Sleep -Seconds 2

# 运行集成测试
python -m pytest tests/test_integration.py -v

# 关闭 Server
Stop-Process -Name "python" -ErrorAction SilentlyContinue
```

**完成标准**：10 个测试用例全部 PASS

---

## Task 10：验收收尾（文档 + 最终检查）

**目标**：扩写 ai-log.md，创建 test-record.md 和 reflection.md，最终检查所有产出

**产出文件**：
- `docs/ai-log.md`（扩写，增量记录每个 Task）
- `docs/test-record.md`（新建）
- `docs/reflection.md`（新建）

**实现内容**：
1. 扩写 ai-log.md：
   - 为 Task 1~10 各添加一条记录（目的、输入、建议、人工判断、验证）
   - 确保每条记录的"人工判断"字段非空
2. 创建 test-record.md：
   - 记录每个测试用例的输入、预期输出、实际输出
   - 包含 test_basic.py、test_retrieve.py、test_answer.py、test_integration.py 的测试结果
3. 创建 reflection.md：
   - 复盘：认知变化、遇到的困难、改进方向

**验收清单**：
1. 目录齐全：`src/`、`data/`、`docs/`、`tests/` 存在且非空
2. README 可复现：包含运行命令和测试命令
3. AI log 有判断：每条 ai-log 的"人工判断"字段非空
4. 产物完整：spec.md、design.md、ai-log.md、test-record.md、reflection.md 齐全
5. 所有测试通过

**验证命令**（Windows PowerShell）：
```powershell
# 运行所有测试
python tests/test_basic.py
python -m pytest tests/test_retrieve.py -v
python -m pytest tests/test_answer.py -v
python -m pytest tests/test_integration.py -v

# 检查文件存在
Get-ChildItem -Path src/, docs/, tests/, data/ -Recurse
```

**完成标准**：
- 所有测试 PASS
- ai-log.md 包含 10+ 条记录
- test-record.md 包含测试结果
- reflection.md 包含复盘内容
- 提交前检查清单全部通过
