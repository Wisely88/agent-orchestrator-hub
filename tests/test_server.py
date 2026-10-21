#!/usr/bin/env python3
import unittest
import os
import json
import tempfile
import server

class TestHubServer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        server.DATA_FILE = os.path.join(self.tmp_dir, "tasks.json")

    def test_default_data_and_save(self):
        data = server.load_data()
        self.assertIn("tasks", data)
        self.assertIn("messages", data)
        self.assertTrue(len(data["tasks"]) >= 3)

    def test_dispatch_logic(self):
        tasks = [
            {"id": "T1", "title": "爬虫抓取数据", "desc": "采集外部数据", "assignedAgent": "Unassigned", "status": "待分配"},
            {"id": "T2", "title": "生动视觉UI", "desc": "设计交互动画", "assignedAgent": "Unassigned", "status": "待分配"},
            {"id": "T3", "title": "自动化测试", "desc": "Pytest用例与门禁", "assignedAgent": "Unassigned", "status": "待分配"},
            {"id": "T4", "title": "核心算法引擎", "desc": "配平与计算状态机", "assignedAgent": "Unassigned", "status": "待分配"}
        ]
        dispatched = server.dispatch_tasks(tasks)
        agents = [t["assignedAgent"] for t in dispatched]
        self.assertEqual(agents, ["OpenClaw", "Muse", "Codex", "Claude"])

if __name__ == "__main__":
    unittest.main()
