import re
import os
import json
import urllib.request

from src.retrieve import retrieve

MIN_HIT_COUNT = 2
MIN_SCORE_GAP = 1

SYSTEM_PROMPT = """你是一个严格基于给定资料回答问题的助手。
你的任务：
1. 只根据下方【参考资料】中的内容回答用户问题。
2. 如果【参考资料】中没有明确提及答案，请直接回复"抱歉，根据现有资料无法回答该问题"，严禁编造或使用外部知识。
3. 回答时请用流畅的中文，保持简洁。"""


def answer(question, chunks):
    """回答用户问题"""
    if not question:
        return {"answer": "请输入您的问题", "sources": []}
    
    # 1. 调用 retrieve 获取 Top3
    top_results = retrieve(question, chunks)
    
    # 2. 拒答判断
    if not top_results:
        return {"answer": "抱歉，知识库中没有与您问题匹配的相关信息。", "sources": []}
    
    if top_results[0]["score"] < MIN_HIT_COUNT:
        return {"answer": "抱歉，知识库中没有与您问题匹配的相关信息。", "sources": []}
    
    if len(top_results) > 1 and top_results[0]["score"] - top_results[1]["score"] <= MIN_SCORE_GAP:
        return {"answer": "抱歉，未找到唯一匹配的资料，请确认您的问题是否清晰。", "sources": []}
    
    # 3. 拼接 Prompt
    context_parts = []
    for i, r in enumerate(top_results[:3], 1):
        context_parts.append(f"【参考资料 {i}】\n{r['content']}")
    context = "\n\n".join(context_parts)
    
    user_prompt = f"""{context}

---
请根据以上参考资料回答用户问题：{question}"""
    
    # 4. 调用 LLM Mock
    api_base = os.environ.get("LLM_API_BASE", "http://localhost:9876/v1")
    api_key = os.environ.get("LLM_API_KEY", "mock-key")
    model = os.environ.get("LLM_MODEL", "mock")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        req = urllib.request.Request(
            f"{api_base}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            llm_answer = result["choices"][0]["message"]["content"]
    except Exception as e:
        llm_answer = f"调用 LLM 失败: {e}"
    
    # 5. 提取 sources
    sources = [r["id"] for r in top_results]
    
    return {"answer": llm_answer, "sources": sources}
