from agents.memory_agent import MemoryAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    print("欢迎使用命令行AI问答助手！")
    user_id = input("请输入用户ID（默认999）: ")
    if not user_id.strip():
        user_id = 999
    else:
        user_id = int(user_id)
    agent = MemoryAgent(user_id)
    print(f"已载入用户{user_id}，当前对话组ID: {agent.group_id}")
    print("输入问题开始对话，输入 /new 新对话，/switch 切换对话组，/history [页码] 查看历史，/exit 退出。\n")
    while True:
        user_input = input("你：")
        if user_input.strip() == "":
            continue
        if user_input.startswith("/exit"):
            agent.save()
            print("已保存并安全退出。再见！")
            break
        elif user_input.startswith("/new"):
            agent.new_conversation()
            print(f"已开启新对话组，当前对话组ID: {agent.group_id}")
        elif user_input.startswith("/switch"):
            groups = agent.list_conversations()
            print("可选对话组ID：", groups)
            gid = input("请输入要切换的对话组ID: ")
            try:
                gid = int(gid)
                if gid in groups:
                    agent.switch_conversation(gid)
                    print(f"已切换到对话组{gid}")
                else:
                    print("无效的对话组ID。")
            except Exception:
                print("输入有误。")
        elif user_input.startswith("/history"):
            parts = user_input.strip().split()
            page = 1
            if len(parts) > 1 and parts[1].isdigit():
                page = int(parts[1])
            agent.show_history(page)
        else:
            answer = agent.ask(user_input)
            print("AI：", answer)

if __name__ == "__main__":
    main() 