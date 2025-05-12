import unittest
from agents.reminder_agent import ReminderAgent
class TestReminderAgent(unittest.TestCase):
    def test_add_task(self):
        agent = ReminderAgent()
        # 测试添加任务
        self.assertIsNone(agent.add_task("Test Task"))
if __name__ == "__main__":
    unittest.main()