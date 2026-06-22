import re


def retrieve(question, chunks):
    if not question or not chunks:
        return []

    question_lower = question.lower()
    question_words = set(re.findall(r'[\w\u4e00-\u9fff]+', question_lower))

    scored = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = 0
        for word in question_words:
            score += chunk_lower.count(word)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored if score > 0][:3]
