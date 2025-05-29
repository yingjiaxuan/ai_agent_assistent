from agents.memory_agent import MemoryAgent
from dotenv import load_dotenv
import re  # For regex validation

def main():
    load_dotenv()
    print("Welcome to the Command Line AI Q&A Assistant!")
    while True:
        user_id = input("Please enter your User ID (default 999): ").strip()
        if user_id == "":
            user_id = 999
            break
        if re.fullmatch(r"\d+", user_id):
            user_id = int(user_id)
            break
        else:
            print("User ID must be a number. Please try again.")
    agent = MemoryAgent(user_id)
    print(f"User {user_id} loaded. Current conversation group ID: {agent.group_id}")
    groups = agent.list_conversations()
    if not groups:
        print("[Info] No conversation history found for this user. Use /new to start a new conversation group.")
    print("Type your question to start chatting. Commands: /new (new conversation), /switch (switch group), /history [page] (view history), /exit (exit), /summarize (summarize memory), /profile (manage user profile).\n")
    allowed_cmds = ["/new", "/switch", "/history", "/exit", "/summarize", "/profile"]
    while True:
        user_input = input("You: ")
        if user_input.strip() == "":
            continue
        if user_input.startswith("/"):
            cmd = user_input.strip().split()[0]
            if cmd not in allowed_cmds:
                print(f"Invalid command: {cmd}. Please try again. Available commands: {', '.join(allowed_cmds)}")
                continue
        if user_input.startswith("/exit"):
            agent.save()
            print("Progress saved. Exiting safely. Goodbye!")
            break
        elif user_input.startswith("/new"):
            agent.new_conversation()
            print(f"Started a new conversation group. Current group ID: {agent.group_id}")
        elif user_input.startswith("/switch"):
            groups = agent.list_conversations()
            print("Available group IDs:", groups)
            gid = input("Enter the group ID to switch to: ")
            try:
                gid = int(gid)
                if gid in groups:
                    agent.switch_conversation(gid)
                    print(f"Switched to group {gid}")
                else:
                    print("Invalid group ID.")
            except Exception:
                print("Invalid input.")
        elif user_input.startswith("/history"):
            parts = user_input.strip().split()
            page = 1
            if len(parts) > 1 and parts[1].isdigit():
                page = int(parts[1])
            agent.show_history(page)
        elif user_input.startswith("/summarize"):
            agent.summarize_user_memory()
            print("Memory summary generated and saved to database and YAML.")
        elif user_input.startswith("/profile"):
            mode = input("Choose mode: 1-Manual entry 2-Auto generate (default 2): ")
            if mode.strip() == "1":
                agent.manual_profile_entry()
                print("User profile manually entered and saved to database and YAML.")
            else:
                agent.auto_generate_profile()
                print("User profile auto-generated and saved to database and YAML.")
        else:
            answer = agent.ask(user_input)
            print("AI:", answer)

if __name__ == "__main__":
    main() 