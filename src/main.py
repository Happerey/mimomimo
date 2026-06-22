import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.retrieve import retrieve
from src.answer import answer


def load_chunks(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = re.split(r'\n(?=##\s*\[faq-\d{2}\])', content)
    return [c.strip() for c in chunks if c.strip()]


def main():
    if len(sys.argv) < 2:
        print("请输入您的问题")
        print("用法: python3 src/main.py \"你的问题\"")
        sys.exit(1)

    question = sys.argv[1]
    if not question.strip():
        print("请输入您的问题")
        sys.exit(0)

    faq_path = os.path.join(os.path.dirname(__file__), "..", "data", "course-faq.md")
    chunks = load_chunks(faq_path)

    relevant = retrieve(question, chunks)

    if not relevant:
        print("资料中没有找到依据。本助手仅能回答 Day1 AI Native 训练营相关问题。")
        sys.exit(0)

    result = answer(question, relevant)
    print(result["answer"])
    if result["sources"]:
        print(f"\n来源: {', '.join(result['sources'])}")


if __name__ == "__main__":
    main()
