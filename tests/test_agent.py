"""Agent 模块单元测试（PRD 6.1）。

测试范围：动作解析、任务状态管理。
（模型调用涉及网络与计费，单元测试中建议 mock，不真实请求 API。）
运行：pytest tests/test_agent.py
"""

import pytest

from agent.action_parser import parse_action, SUPPORTED_ACTIONS


def test_parse_action_unsupported_returns_none():
    """不支持的动作类型应返回 None。"""
    assert parse_action("Action: unknown_action(x=1)") is None


def test_parse_action_no_match_returns_none():
    """格式不符的输出应返回 None。"""
    assert parse_action("这不是一条合法动作") is None


def test_supported_actions_set():
    """白名单应包含支持的动作类型（含阶段五新增的 double_click）。"""
    assert SUPPORTED_ACTIONS == {
        "click", "double_click", "type", "scroll", "hotkey", "finish"
    }
