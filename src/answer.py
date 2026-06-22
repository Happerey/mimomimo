import re
import os
import json
import urllib.request


def answer(question, chunks):
    if not question:
        return {"answer": "请输入您的问题", "sources": []}

    api_base = os.environ.get("LLM_API_BASE", "http://localhost:9876/v1")
    api_key = os.environ.get("LLM_API_KEY", "mock-key")
    model = os.environ.get("LLM_MODEL", "mock")

    context = "\n\n".join(chunks) if chunks else ""

    prompt = f"""你是一个课程助手，只基于以下资料回答问题。
如果资料中没有相关信息，请回复"资料中没有找到依据"。
回答必须注明来源编号如 [faq-XX]。

资料：
{context}

用户问题：{question}"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
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
            content = result["choices"][0]["message"]["content"]

            sources = re.findall(r'\[faq-\d{2}\]', content)
            return {"answer": content, "sources": list(set(sources))}
    except Exception as e:
        return {"answer": f"调用 LLM 失败: {e}", "sources": []}
