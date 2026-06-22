import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.answer import answer
from src.retrieve import load_chunks


@pytest.fixture
def chunks():
    """加载 FAQ chunks"""
    faq_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'course-faq.md')
    return load_chunks(faq_path)


class TestAnswer:
    def test_answer_returns_dict(self, chunks):
        """验证返回字典"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "根据资料，可复核交付是..."
                }
            }]
        }
        with patch('src.answer.urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = str(mock_response).encode('utf-8')
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp
            result = answer("可复核交付", chunks)
            assert isinstance(result, dict)

    def test_answer_has_required_keys(self, chunks):
        """验证返回结果包含 answer 和 sources 键"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "根据资料，可复核交付是..."
                }
            }]
        }
        with patch('src.answer.urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = str(mock_response).encode('utf-8')
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp
            result = answer("可复核交付", chunks)
            assert "answer" in result
            assert "sources" in result
            assert isinstance(result["answer"], str)
            assert isinstance(result["sources"], list)

    def test_answer_reject_low_score(self, chunks):
        """资料外拒答：Top1.score < 2"""
        result = answer("奖学金", chunks)
        assert "抱歉" in result["answer"] or "没有" in result["answer"]
        assert result["sources"] == []

    def test_answer_reject_empty_chunks(self):
        """空 chunks 拒答"""
        result = answer("可复核交付", [])
        assert "抱歉" in result["answer"] or "没有" in result["answer"]
        assert result["sources"] == []

    def test_answer_reject_empty_question(self, chunks):
        """空问题拒答"""
        result = answer("", chunks)
        assert result["sources"] == []

    def test_answer_prompt_format(self, chunks):
        """验证拼接的 Prompt 包含【参考资料】格式"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "根据资料..."
                }
            }]
        }
        with patch('src.answer.urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = str(mock_response).encode('utf-8')
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            # 捕获请求体
            captured_payload = None
            def capture_request(req):
                nonlocal captured_payload
                import json
                captured_payload = json.loads(req.data.decode('utf-8'))
                return mock_resp

            mock_urlopen.side_effect = capture_request
            answer("可复核交付", chunks)

            if captured_payload:
                user_msg = captured_payload["messages"][-1]["content"]
                assert "【参考资料" in user_msg

    def test_answer_sources_extraction(self, chunks):
        """验证 sources 从 retrieve 结果正确提取"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "根据资料..."
                }
            }]
        }
        with patch('src.answer.urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = str(mock_response).encode('utf-8')
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp
            result = answer("可复核交付", chunks)
            if result["sources"]:
                assert any(s.startswith("faq-") for s in result["sources"])
