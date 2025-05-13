from agents.reminder_agent import ReminderAgent

if __name__ == "__main__":
    user_id = input("请输入用户ID: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("用户ID应为数字！")
        exit(1)
    agent = ReminderAgent(user_id)
    result = agent.get_smart_reminders()
    print("\n===== AI 智能提醒建议 =====\n")
    print(result) 