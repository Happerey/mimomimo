# RAG 课程助手 — Spec

## 目标（Goals）

1. 用户输入问题后，CLI 输出基于 `course-faq.md` 的回答和来源编号 `[faq-XX]`
2. 正确匹配：问题明确指向某条 FAQ 时，返回该条内容并标注来源
3. 跨段落匹配：问题涉及多条 FAQ 时，返回相关内容并标注多个来源
4. 资料外拒答：问题与课程无关时，输出"资料中没有找到依据"
5. 空输入提示：用户未输入问题时，提示"请输入您的问题"

## 非目标（Non-Goals）

1. 不做 Web UI（CLI 工具）
2. 不做用户登录（单用户本地运行）
3. 不做数据库存储（文件系统就是数据源）
4. 不支持 PDF/Word 上传（只支持 Markdown）
5. 不支持除 `course-faq.md` 之外的资料源
6. 不引入中文分词库（用简单字符串匹配）

## 验收标准（Acceptance Criteria）

| 测试问题 | 类型 | 预期行为 |
|---------|------|---------|
| Day1要交什么？ | 正确匹配 | 输出包含"6类证据文件"，来源 `[faq-02]` |
| 什么是可复核交付？ | 正确匹配 | 输出包含"助教""独立判断"，来源 `[faq-01]` |
| ai-log的五字段是什么？ | 正确匹配 | 输出包含"目的""输入""建议""人工判断""验证"，来源 `[faq-03]` |
| Spec中的非目标和AI过度设计有什么关系？ | 跨段落 | 输出包含"非目标""过度设计"，来源 `[faq-04]` 和/或 `[faq-10]` |
| 奖学金政策是什么？ | 资料外 | 输出"资料中没有找到依据" |
| 今天中午吃什么？ | 资料外 | 输出"资料中没有找到依据" |
| （空输入） | 空输入 | 输出"请输入您的问题" |

## 配置常量

| 常量名 | 建议值 | 说明 |
|-------|-------|------|
| `MIN_HIT_COUNT` | 2 | 必须命中至少 2 个不同有效关键词，否则拒答 |
| `MIN_SCORE_GAP` | 1 | Top1 - Top2 <= 1 时拒答（差值不足，结果不明确） |

## 接口签名

### retrieve 函数

```python
def retrieve(question: str, chunks: list) -> list:
    """
    输入: question - 用户问题字符串
         chunks - 完整的 FAQ chunk 列表（10个字符串）
    输出: Top3 匹配结果列表，每个元素为字典：
         [
             {"id": "faq-01", "content": "chunk内容", "score": 3},
             {"id": "faq-02", "content": "chunk内容", "score": 2},
             {"id": "faq-03", "content": "chunk内容", "score": 1}
         ]
         如果所有命中分数均为0，返回空列表 []
    """
```

### answer 函数

```python
def answer(question: str, chunks: list) -> dict:
    """
    输入: question - 用户问题字符串
         chunks - 完整的 FAQ chunk 列表（10个字符串）
    输出: 字典，格式如下：
         {
             "answer": "LLM生成的回答，或拒答文案",
             "sources": ["faq-01", "faq-02"]
         }
    """
    # 1. 调用 retrieve 拿到带分数的 Top3
    # 2. 拒答判断：top_results 为空 或 score < 2 或 score差值 <= 1
    # 3. 拼接 Prompt 并调用 LLM
    # 4. 返回 LLM 回答 + 从 top_results 提取的 id 列表作为 sources
```

## 检索算法（Retrieve）

1. **输入**：用户问题 Q，FAQ 文本块列表 C
2. **切片**：按 `## [faq-XX]` 标题分割，每条 FAQ 为独立 chunk
3. **预处理**：
   - 将 Q 按标点（逗号、句号、空格、问号、感叹号）切分为短语列表
   - 剔除长度 <= 1 的字符
   - 剔除停用词：的、了、吗、呢、要、么、什、我、你、是、在、有、和、与
   - 得到有效关键词列表 K
4. **布尔命中计分**：对于每个 chunk c，计算 Score(c) = K 中出现在 c 里的不同关键词的去重数量（每个关键词最多计 1 分）
5. **排序**：按 Score 降序取前 3 个 chunk 返回

## 拒答与回答逻辑（Answer）

```
if Top1.Score < MIN_HIT_COUNT:
    拒答（资料外）
elif Top1.Score - Top2.Score <= MIN_SCORE_GAP:
    拒答（结果不明确）
else:
    将 Top1~Top3 内容拼入 Prompt，调用 LLM 生成回答
```
