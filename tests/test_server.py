#!/usr/bin/env python3
import os
import tempfile
import unittest
from unittest.mock import patch

import server


class TestHubServer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        server.DATA_FILE = os.path.join(self.tmp_dir.name, "data", "tasks.json")
        server.OUTPUTS_DIR = os.path.join(self.tmp_dir.name, "outputs")

    def test_default_data_and_save(self):
        data = server.load_data()
        self.assertEqual(data["tasks"], [])
        self.assertIn("messages", data)
        data["tasks"].append({"id": "T1", "status": "待执行"})
        server.save_data(data)
        self.assertEqual(server.load_data()["tasks"][0]["id"], "T1")

    def test_unconfigured_agent_fails_closed(self):
        with self.assertRaises(server.AgentNotConfiguredError):
            server.execute_real_agent_task({
                "id": "T1", "title": "test", "desc": "test",
                "assignedAgent": "Codex"
            })
        self.assertFalse(os.path.exists(server.OUTPUTS_DIR))

    def test_claude_missing_key_is_not_fake_success(self):
        with patch.object(server, "ANTHROPIC_API_KEY", ""):
            with self.assertRaises(server.AgentNotConfiguredError):
                server.execute_real_agent_task({
                    "id": "T2", "title": "test", "desc": "test",
                    "assignedAgent": "Claude"
                })
        self.assertFalse(os.path.exists(server.OUTPUTS_DIR))

    def test_configured_provider_writes_artifact_without_executing_it(self):
        with patch.object(server, "call_agent_for_code", return_value=("print('hello')", "Mock Provider")):
            result = server.execute_real_agent_task({
                "id": "T3", "title": "safe artifact", "desc": "test",
                "assignedAgent": "Claude"
            })
        self.assertTrue(os.path.isfile(result["file_path"]))
        self.assertEqual(result["provider"], "Mock Provider")
        self.assertIn("未运行测试", result["test_result"])
        self.assertIn("未执行", result["execution_result"])
        with open(result["file_path"], encoding="utf-8") as f:
            self.assertEqual(f.read(), "print('hello')")

    def test_unknown_agent_is_not_routed_to_gemini(self):
        with patch.object(server, "genai_client") as fake_gemini:
            with self.assertRaises(server.AgentNotConfiguredError):
                server.call_agent_for_code("Muse", "test")
            fake_gemini.models.generate_content.assert_not_called()


if __name__ == "__main__":
    unittest.main()
