import re

STOPWORDS = {'的', '了', '吗', '呢', '要', '么', '什', '我', '你', '是', '在', '有', '和', '与', '什么', '怎么', '为什么', '哪个', '哪些'}


def load_chunks(filepath):
    """加载并切分 FAQ 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    raw_chunks = re.split(r'\n(?=##\s*\[faq-\d{2}\])', content)
    
    chunks = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        match = re.search(r'\[faq-(\d{2})\]', chunk)
        if match:
            faq_id = f"faq-{match.group(1)}"
            chunks.append({"id": faq_id, "content": chunk})
    
    return chunks


def retrieve(question, chunks):
    """检索与问题最相关的 Top3 FAQ 条目"""
    if not question or not chunks:
        return []
    
    # 1. 预处理：按标点切分短语
    phrases = re.split(r'[，。？！、\s,.?!\-]+', question)
    
    # 2. 剔除长度 <= 1 的字符和停用词
    keywords = []
    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase) > 1 and phrase not in STOPWORDS:
            keywords.append(phrase)
    
    if not keywords:
        return []
    
    # 3. 布尔命中计分
    scored = []
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        score = 0
        matched = set()
        for kw in keywords:
            if kw.lower() in content_lower and kw not in matched:
                score += 1
                matched.add(kw)
        scored.append({"id": chunk["id"], "content": chunk["content"], "score": score})
    
    # 4. 按 score 降序排列，取 Top3（仅返回 score > 0）
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [r for r in scored if r["score"] > 0][:3]
