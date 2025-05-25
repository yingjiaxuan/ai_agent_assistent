from agents.memory_agent import MemoryAgent
from dotenv import load_dotenv
import re  # 新增：用于正则校验

def main():
    load_dotenv()
    print("欢迎使用命令行AI问答助手！")
    # 注释掉老代码：未校验用户ID是否为数字
    # user_id = input("请输入用户ID（默认999）: ")
    # if not user_id.strip():
    #     user_id = 999
    # else:
    #     user_id = int(user_id)
    # 新实现：正则校验用户ID，只能为数字
    while True:
        user_id = input("请输入用户ID（默认999）: ").strip()
        if user_id == "":
            user_id = 999
            break
        # if re.fullmatch(r"\\d+", user_id):
        if re.fullmatch(r"\d+", user_id):
            user_id = int(user_id)
            break
        else:
            print("用户ID只能为数字，请重新输入。")
    agent = MemoryAgent(user_id)
    print(f"已载入用户{user_id}，当前对话组ID: {agent.group_id}")
    # 检查是否有历史对话组
    groups = agent.list_conversations()
    if not groups:
        print("【提示】当前用户暂无历史对话记录，请使用 /new 命令开启新的对话组。")
    print("输入问题开始对话，输入 /new 新对话，/switch 切换对话组，/history [页码] 查看历史，/exit 退出，/summarize 生成记忆摘要，/profile 管理用户画像。\n")
    allowed_cmds = ["/new", "/switch", "/history", "/exit", "/summarize", "/profile"]
    while True:
        user_input = input("你：")
        if user_input.strip() == "":
            continue
        # 校验命令是否合法（只对以/开头的命令）
        if user_input.startswith("/"):
            cmd = user_input.strip().split()[0]
            if cmd not in allowed_cmds:
                print(f"无效命令：{cmd}，请重新输入。可用命令：{', '.join(allowed_cmds)}")
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
        elif user_input.startswith("/summarize"):
            # 手动生成记忆摘要
            agent.summarize_user_memory()
            print("记忆摘要已生成并写入数据库和YAML。")
        elif user_input.startswith("/profile"):
            # 用户画像管理
            mode = input("选择模式：1-手动录入 2-自动生成（默认2）: ")
            if mode.strip() == "1":
                agent.manual_profile_entry()
                print("用户画像已手动录入并写入数据库和YAML。")
            else:
                agent.auto_generate_profile()
                print("用户画像已自动生成并写入数据库和YAML。")
        else:
            answer = agent.ask(user_input)
            print("AI：", answer)

if __name__ == "__main__":
    main() 