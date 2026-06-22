# AI 协作日志

## 记录 1：理解项目结构

| 字段 | 内容 |
|------|------|
| **目的** | 阅读 rag-assistant 目录所有文件，理解数据特征和项目要求 |
| **输入** | rag-assistant 目录下的 README.md、course-faq.md、mock_server.py、test_basic.py、questions.json |
| **建议** | AI 总结了项目结构：10条FAQ按[faq-XX]编号切片，需实现 retrieve() 和 answer() 两个接口，提出了三个问题：是否需要先启动Mock Server、是否需要中文分词、资料外拒答阈值如何设定 |
| **人工判断** | 采纳理解，但要求先对齐需求再动手实现 |
| **验证** | - |

## 记录 2：确定检索策略

| 字段 | 内容 |
|------|------|
| **目的** | 明确检索算法的命中分数计算、排序和拒答逻辑 |
| **输入** | 用户提供：1.先计算命中分数 2.取Top3 3.拒答判断（Top1<2或Top1-Top2<1） |
| **建议** | AI 按照用户描述的策略开始实现代码 |
| **人工判断** | 暂停实现，要求先写 spec.md 对齐需求，避免返工 |
| **验证** | - |

## 记录 3：编写 Spec 初稿

| 字段 | 内容 |
|------|------|
| **目的** | 定义项目目标、非目标、验收标准，约束 AI 行为边界 |
| **输入** | course-faq.md 内容、questions.json 测试用例、用户提供的检索策略 |
| **建议** | AI 编写了 spec.md 初稿，包含5个目标、6个非目标、7个验收标准、检索策略说明，并提出3个待确认问题：分词粒度、大小写处理、命中分数计算 |
| **人工判断** | 接受框架，但对检索策略提出重大修改 |
| **验证** | 用户审阅 spec.md 后给出具体修改意见 |

## 记录 4：优化检索算法

| 字段 | 内容 |
|------|------|
| **目的** | 改进检索算法，提高匹配准确性和拒答可靠性 |
| **输入** | 用户提供：1.短语匹配替代分词 2.布尔命中计数 3.重新定义阈值（MIN_HIT_COUNT=2, MIN_SCORE_GAP=1） |
| **建议** | AI 建议：保留原阈值Top1<2，调整Top1-Top2<1为<=1；按标点切分短语，剔除长度<=1字符和停用词 |
| **人工判断** | 全部采纳：1.放弃分词改用短语匹配 2.采用布尔命中 3.阈值设为MIN_HIT_COUNT=2、MIN_SCORE_GAP=1，Top1-Top2<=1时拒答 |
| **验证** | 待通过 tests/questions.json 的10个测试用例验证 |

## 记录 5：项目初始化与 Git 管理

| 字段 | 内容 |
|------|------|
| **目的** | 创建 Git 仓库管理项目代码，建立版本控制 |
| **输入** | rag-assistant 目录下所有文件 |
| **建议** | AI 初始化 Git 仓库，提交所有文件，添加 .gitignore 排除 __pycache__ |
| **人工判断** | 采纳，要求全部提交 |
| **验证** | git log 显示两个提交：初始化项目和添加 .gitignore |

## 记录 6：设计 RAG 六环节数据流

| 字段 | 内容 |
|------|------|
| **目的** | 画出完整的 RAG 数据流图，明确每个环节的输入/输出和处理逻辑 |
| **输入** | course-faq.md 数据特征（10条FAQ、[faq-XX]编号）、spec.md 目标（正确匹配/跨段落/资料外拒答/空输入） |
| **建议** | AI 提出5个待确认问题：1.切片时机 2.System Prompt格式 3.Chunks嵌入格式 4.来源引用方案（A:LLM自带 / B:后处理拼接） 5.拒答判断时机（A:检索环节 / B:LLM判断） 6.跨段落处理方式 |
| **人工判断** | 逐项确认：1.程序启动时预切，懒加载存内存 2.System Prompt"严格基于资料回答，不能编造" 3.用【参考资料1/2/3】格式嵌入 4.选方案B：LLM只输出纯文本，sources从retrieve结果提取 5.选方案A：检索环节判断拒答，不调用LLM 6.Top1+Top2+Top3全部拼入Prompt，LLM自动忽略不相关内容 |
| **验证** | 待实现后通过 tests/questions.json 验证 |

## 记录 7：数据流各环节输入/输出定义

| 字段 | 内容 |
|------|------|
| **目的** | 明确 RAG 六环节每个环节的输入和输出，作为实现依据 |
| **输入** | 记录6的决策结果 |
| **建议** | AI 绘制数据流图，标注6个环节的输入/输出：切片(文件→chunks)、检索(Q+chunks→Top3)、拒答判断(Top3+分数→布尔值)、Prompt拼接(指令+Top3+Q→Prompt)、LLM调用(Prompt→纯文本)、来源引用(LLM答案+sources→最终输出) |
| **人工判断** | 采纳，确认数据流图和输入/输出定义 |
| **验证** | 待实现后验证各环节衔接 |

## 记录 8：推导接口签名

| 字段 | 内容 |
|------|------|
| **目的** | 从数据流推导 retrieve 和 answer 的函数签名，明确输入/输出格式 |
| **输入** | 数据流图、各环节输入/输出定义 |
| **建议** | AI 提出3个待确认问题：1.retrieve 输出格式（A:元组 / B:字典 / C:纯内容） 2.retrieve 是否带分数 3.answer 参数设计（A:接收retrieve结果 / B:自己调用retrieve） |
| **人工判断** | 逐项确认：1.选B：输出字典列表 `[{"id", "content", "score"}, ...]` 2.选A：返回带分数结果，供answer判断拒答 3.选B：answer内部调用retrieve，接收chunks列表 |
| **验证** | 接口签名写入 spec.md |

## 记录 9：编写 design.md

| 字段 | 内容 |
|------|------|
| **目的** | 编写完整设计文档，包含数据流图、模块接口、拒答规则、来源引用、Prompt模板 |
| **输入** | spec.md（接口签名、配置常量）、数据流图、用户确认的5个问题（Mermaid语法、伪代码、调用链、load_chunks独立模块、Prompt完整模板） |
| **建议** | AI 提出5个格式问题：1.数据流图用ASCII还是Mermaid 2.是否需要伪代码 3.是否需要模块依赖关系 4.是否单独说明load_chunks 5.是否写明Prompt模板 |
| **人工判断** | 逐项确认：1.用Mermaid语法+文字说明 2.需要伪代码形式 3.需要说明main→answer→retrieve调用链 4.需要单独说明load_chunks模块 5.必须完整写明System Prompt和User Prompt |
| **验证** | design.md 已创建，包含7个章节：数据流图、模块接口、Prompt模板、拒答规则、来源引用、配置常量、文件结构 |

## 记录 10：编写初版 tasks.md

| 字段 | 内容 |
|------|------|
| **目的** | 拆解开发计划，生成可独立验证的任务清单 |
| **输入** | spec.md、design.md、course-faq.md |
| **建议** | AI 提出7个拆解问题：1.测试驱动模式（TDD/先搭框架） 2.任务粒度（按模块/按场景） 3.单元测试范围 4.任务数量 5.完成标准（自动化命令） 6.Mock Server依赖 7.文档任务 |
| **人工判断** | 逐项确认：1.混合模式（Test-First→Stub→实现） 2.按模块拆分 3.retrieve独立单元测试+answer用mock+questions.json集成测试 4.10个任务 5.每个任务绑定自动化命令 6.单独Task验证Mock Server连通性 7.ai-log.md作为收尾Task |
| **验证** | tasks.md 已创建，包含10个任务和依赖关系图 |

## 记录 11：审查并完善 tasks.md

| 字段 | 内容 |
|------|------|
| **目的** | 审查初版 tasks.md，发现并修复潜在问题 |
| **输入** | 初版 tasks.md、spec.md、test_basic.py、现有代码 |
| **建议** | AI 提出6个完善点：1.test_basic.py需更新（retrieve返回字典列表） 2.现有代码需重写（单字匹配→短语匹配+布尔命中） 3.缺少停用词常量（需补充到spec.md） 4.questions.json可能需微调 5.缺少test-record.md 6.缺少reflection.md |
| **人工判断** | 全部采纳，要求按这6点重新调整 tasks.md |
| **验证** | tasks.md 已更新，包含：Task 1补充停用词常量、Task 2更新test_basic.py、Task 9微调questions.json、Task 10新增test-record.md和reflection.md |

## 记录 12：推送到远程仓库

| 字段 | 内容 |
|------|------|
| **目的** | 将项目代码推送到 GitHub 远程仓库，实现版本备份和协作 |
| **输入** | 本地 Git 仓库（3个commit）、GitHub 仓库地址 |
| **建议** | AI 添加远程仓库 origin，执行 git push -u origin master |
| **人工判断** | 采纳，提供仓库地址 https://github.com/Happerey/mimomimo |
| **验证** | git push 成功，远程仓库显示完整文件结构 |

## 记录 13：执行 Task 1 — 补充停用词常量 + 编写 retrieve 单元测试

| 字段 | 内容 |
|------|------|
| **目的** | Test-First，先写测试再实现；补充 spec.md 配置常量 |
| **输入** | spec.md、course-faq.md、design.md 中的检索算法定义 |
| **建议** | AI 在 spec.md 添加 STOPWORDS 常量，创建 test_retrieve.py 包含 14 个测试用例（TestLoadChunks 5 个 + TestRetrieve 9 个） |
| **人工判断** | 采纳，要求测试覆盖：精确匹配、跨段落、资料外、空输入、停用词过滤、分数排序、布尔命中 |
| **验证** | pytest 运行结果：3 failed（预期，retrieve 未实现）、11 passed |

## 记录 14：执行 Task 2 — 更新 test_basic.py + 搭建框架 Stub

| 字段 | 内容 |
|------|------|
| **目的** | 更新接口契约检查，创建空函数签名让 test_basic.py 通过 |
| **输入** | test_basic.py、spec.md 中的接口签名定义 |
| **建议** | AI 更新 test_basic.py 检查 retrieve 返回字典列表（包含 id/content/score），更新 retrieve.py 和 answer.py 为空签名 |
| **人工判断** | 采纳，要求 retrieve 返回格式为 `[{"id", "content", "score"}, ...]` |
| **验证** | python tests/test_basic.py 结果：9 passed, 0 failed |

## 记录 15：执行 Task 3 — 实现 load_chunks() 模块

| 字段 | 内容 |
|------|------|
| **目的** | 实现 FAQ 文件切片功能，返回 10 个 chunk 字典列表 |
| **输入** | data/course-faq.md、spec.md 中的切片规则（按 `## [faq-XX]` 分割） |
| **建议** | AI 用正则 `\n(?=##\s*\[faq-\d{2}\])` 分割，提取 id 后返回 `[{"id": "faq-01", "content": "..."}, ...]` |
| **人工判断** | 采纳 |
| **验证** | pytest tests/test_retrieve.py::TestLoadChunks 结果：5 passed |
