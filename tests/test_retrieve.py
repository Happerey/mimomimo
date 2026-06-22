import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.retrieve import load_chunks, retrieve


@pytest.fixture
def chunks():
    """加载 FAQ chunks"""
    faq_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'course-faq.md')
    return load_chunks(faq_path)


class TestLoadChunks:
    def test_load_chunks_returns_list(self, chunks):
        """验证返回列表"""
        assert isinstance(chunks, list)

    def test_load_chunks_count(self, chunks):
        """验证返回 10 个 chunk"""
        assert len(chunks) == 10

    def test_load_chunks_format(self, chunks):
        """验证每个 chunk 是字典且包含 id 和 content"""
        for chunk in chunks:
            assert isinstance(chunk, dict)
            assert "id" in chunk
            assert "content" in chunk

    def test_load_chunks_id_format(self, chunks):
        """验证每个 chunk 的 id 格式为 faq-XX"""
        import re
        for chunk in chunks:
            assert re.match(r'faq-\d{2}', chunk["id"]), f"Invalid id format: {chunk['id']}"

    def test_load_chunks_content_has_faq_tag(self, chunks):
        """验证每个 chunk 的 content 包含 [faq-XX]"""
        import re
        for chunk in chunks:
            assert re.search(r'\[faq-\d{2}\]', chunk["content"]), f"Missing [faq-XX] tag in chunk {chunk['id']}"


class TestRetrieve:
    def test_retrieve_returns_list(self, chunks):
        """验证返回列表"""
        result = retrieve("可复核交付", chunks)
        assert isinstance(result, list)

    def test_retrieve_exact_match(self, chunks):
        """正确匹配：输入'可复核交付'，Top1 为 faq-01"""
        result = retrieve("可复核交付", chunks)
        assert len(result) > 0
        assert result[0]["id"] == "faq-01"

    def test_retrieve_cross_paragraph(self, chunks):
        """跨段落匹配：返回结果包含 faq-04 和/或 faq-10"""
        result = retrieve("非目标 过度设计", chunks)
        assert len(result) > 0
        ids = [r["id"] for r in result]
        assert "faq-04" in ids or "faq-10" in ids

    def test_retrieve_out_of_domain(self, chunks):
        """资料外问题：返回空列表"""
        result = retrieve("奖学金", chunks)
        assert result == []

    def test_retrieve_empty_input(self, chunks):
        """空输入：返回空列表"""
        result = retrieve("", chunks)
        assert result == []

    def test_retrieve_stopwords_filtered(self, chunks):
        """停用词过滤：'的'、'了'等不影响分数"""
        # "ai-log" 和 "ai-log 的" 应该返回相同结果
        result_with_stopwords = retrieve("ai-log 的", chunks)
        result_without_stopwords = retrieve("ai-log", chunks)
        if result_with_stopwords and result_without_stopwords:
            assert result_with_stopwords[0]["id"] == result_without_stopwords[0]["id"]

    def test_retrieve_score_order(self, chunks):
        """验证结果按 score 降序排列"""
        result = retrieve("ai-log 五字段", chunks)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["score"] >= result[i + 1]["score"]

    def test_retrieve_binary_hit(self, chunks):
        """布尔命中：同一关键词重复出现只计 1 分"""
        # faq-01 包含"可复核"多次，但分数应该只计 1
        result = retrieve("可复核", chunks)
        if result:
            faq01 = [r for r in result if r["id"] == "faq-01"]
            if faq01:
                assert faq01[0]["score"] == 1  # "可复核"只出现一次匹配

    def test_retrieve_result_format(self, chunks):
        """验证返回结果格式：每个元素包含 id, content, score"""
        result = retrieve("Day1 提交", chunks)
        if result:
            for r in result:
                assert isinstance(r, dict)
                assert "id" in r
                assert "content" in r
                assert "score" in r
                assert isinstance(r["score"], int)
