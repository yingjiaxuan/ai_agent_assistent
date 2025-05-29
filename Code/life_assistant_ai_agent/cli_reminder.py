from agents.reminder_agent import ReminderAgent
from dotenv import load_dotenv
   

if __name__ == "__main__":
    load_dotenv()
    user_id = input("Please enter your User ID: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("User ID must be a number!")
        exit(1)
    agent = ReminderAgent(user_id)
    result = agent.get_smart_reminders()
    print("\n===== AI Smart Reminder Suggestions =====\n")
    print(result) 