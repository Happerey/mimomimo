import re


def load_chunks(filepath):
    """加载并切分 FAQ 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 用正则按 ## [faq-XX] 标题分割
    raw_chunks = re.split(r'\n(?=##\s*\[faq-\d{2}\])', content)
    
    chunks = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        # 提取 id（如 faq-01）
        match = re.search(r'\[faq-(\d{2})\]', chunk)
        if match:
            faq_id = f"faq-{match.group(1)}"
            chunks.append({"id": faq_id, "content": chunk})
    
    return chunks


def retrieve(question, chunks):
    """检索与问题最相关的 Top3 FAQ 条目"""
    return []
