import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.retrieve import load_chunks
from src.answer import answer


def main():
    if len(sys.argv) < 2:
        print("请输入您的问题")
        print("用法: python src/main.py \"你的问题\"")
        sys.exit(1)

    question = sys.argv[1]
    if not question.strip():
        print("请输入您的问题")
        sys.exit(0)

    faq_path = os.path.join(os.path.dirname(__file__), "..", "data", "course-faq.md")
    chunks = load_chunks(faq_path)

    result = answer(question, chunks)
    print(result["answer"])
    if result["sources"]:
        print(f"\n来源: {', '.join(result['sources'])}")


if __name__ == "__main__":
    main()
