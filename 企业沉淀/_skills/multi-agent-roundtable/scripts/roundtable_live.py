#!/usr/bin/env python3
"""三省六部 · 实时飞书卡片 + Kanban看板（Web可查看辩论内容）"""
import json, os, sys, asyncio, urllib.request, subprocess, shlex, textwrap

PYTHONPATH = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if PYTHONPATH not in sys.path:
    sys.path.insert(0, PYTHONPATH)

env = {}
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

API_KEY = env['DASHSCOPE_API_KEY']
BASE_URL = env.get('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
FEISHU_OPEN_ID = "ou_5ad3af46154379fa6e57d09bd37e7d8e"
HERMES_BIN = "/opt/hermes/bin/hermes"

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="qwen-max", api_key=API_KEY, base_url=BASE_URL, temperature=0.5,
    model_info={"vision": False, "function_calling": True, "json_output": True, "structured_output": False, "family": "unknown"},
)

AGENT_CONFIGS = [
    ("data_minister", "📊 数据大臣", "数据分析/SQL/ROI/AB实验。只信数据。"),
    ("ops_minister", "🎯 运营大臣", "活动策划/积分商城/用户运营。方案可落地。"),
    ("legal_minister", "⚖️ 法务大臣", "合规/备案/个税/隐私/反作弊。方案过合规关。"),
]
agents = {}
name_map = {}
for agent_id, display, expertise in AGENT_CONFIGS:
    name_map[agent_id] = display
    agents[agent_id] = AssistantAgent(
        name=agent_id, model_client=model_client,
        system_message=f"你是瑞幸即享咖啡大臣。专长：{expertise}",
    )

termination = TextMentionTermination("同意") | TextMentionTermination("结论") | MaxMessageTermination(10)
team = SelectorGroupChat(
    participants=list(agents.values()), model_client=model_client,
    termination_condition=termination,
    selector_prompt="主持圆桌。议题：{history}。大臣：{participants}。从{roles}中选下一个。不要连续选同一个人。鼓励质疑。充分后说「结论」。",
)


# ── Kanban 看板操作 ──

def kanban_run(*args):
    """执行 hermes kanban 命令，返回 (ok, output)"""
    cmd = [HERMES_BIN, "kanban"] + list(args)
    env_ = os.environ.copy()
    env_["PATH"] = f"/opt/hermes/bin:{env_.get('PATH', '')}"
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env_)
        out = (r.stdout or "").strip() + (r.stderr or "").strip()
        return r.returncode == 0, out
    except Exception as e:
        return False, str(e)


def kanban_create_task(title, body=""):
    """创建一个 Kanban 任务，返回 task_id 或 None"""
    ok, out = kanban_run("create", "--triage", title)
    if ok:
        # 输出格式：Created t_xxxxx  (triage, assignee=-)
        for part in out.split():
            if part.startswith("t_") and len(part) > 8:
                # 追加 body 作为第一条 comment
                if body:
                    kanban_comment(part, body)
                return part
    return None


def kanban_comment(task_id, text, author=None):
    """给 Kanban 任务追加评论"""
    parts = [task_id]
    if author:
        parts += ["--author", author]
    parts.append(text)
    kanban_run("comment", *parts)


def kanban_complete_task(task_id):
    """标记任务完成"""
    kanban_run("complete", task_id)


# ── 飞书卡片 ──

def get_token():
    data = json.dumps({"app_id": env['FEISHU_APP_ID'], "app_secret": env['FEISHU_APP_SECRET']}).encode()
    req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=data, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())['tenant_access_token']

def send_or_update_card(topic, turns, status, message_id=None):
    token = get_token()
    elements = [{"tag": "div", "text": {"tag": "lark_md", "content": f"**议题：** {topic}\n**状态：** {status}"}}, {"tag": "hr"}]
    for t in turns:
        c = t['content'][:200] + "..." if len(t['content']) > 200 else t['content']
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**{t['speaker']}**\n{c}"}})
    elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": f"三省六部 | {len(turns)}轮发言 | 看板 http://82.156.210.39:9119/kanban"}]})

    card = {"config": {"wide_screen_mode": True}, "header": {"title": {"tag": "plain_text", "content": "🏛️ 三省六部圆桌"}, "template": "indigo"}, "elements": elements}
    body = json.dumps({"receive_id": FEISHU_OPEN_ID, "msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)}).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if message_id:
        req = urllib.request.Request(f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}", data=body, headers=headers)
        req.method = 'PATCH'
    else:
        req = urllib.request.Request("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id", data=body, headers=headers)

    resp = json.loads(urllib.request.urlopen(req).read())
    return resp['data']['message_id'] if resp.get('code') == 0 and not message_id else message_id


def update_dashboard(topic, turns, status):
    os.makedirs("/opt/data/dashboard", exist_ok=True)
    with open("/opt/data/dashboard/dashboard_status.json", "w") as f:
        json.dump({"topic": topic, "turns": turns, "status": status}, f, ensure_ascii=False)


async def run():
    topic = sys.argv[1] if len(sys.argv) > 1 else "分析问题"
    ts = topic[:60]

    # 1. 创建 Kanban 任务
    print(f"📋 创建看板任务...")
    task_id = kanban_create_task(f"🏛️ 圆桌：{ts}", f"议题：{topic}\n三省六部大臣正在讨论中，前往 http://82.156.210.39:9119/kanban 查看实时辩论内容")

    # 2. 发飞书卡片
    update_dashboard(topic, [], "讨论进行中...")
    msg_id = send_or_update_card(topic, [], "⏳ 讨论中...")
    print(f"📬 议题：{topic}")
    if task_id:
        print(f"📋 Kanban 任务：{task_id}")

    all_turns = []
    async for msg in team.run_stream(task=topic):
        if hasattr(msg, 'source') and hasattr(msg, 'content') and msg.content:
            agent_id = msg.source
            display = name_map.get(agent_id, agent_id)
            content = msg.content.strip()

            turn = {"speaker": display, "content": content}
            all_turns.append(turn)

            # 飞书卡片更新
            send_or_update_card(topic, all_turns, "⏳ 讨论中...", msg_id)
            update_dashboard(topic, all_turns, "讨论中...")

            # Kanban 评论（大臣发言）
            if task_id:
                # 截断超长内容（Kanban comment 有行数限制）
                comment = f"{display}：{content[:500]}"
                if len(content) > 500:
                    comment += "...（余下内容见飞书卡片）"
                kanban_comment(task_id, comment, author=display)

            print(f"  {display}：{content[:60]}...")

    # 完成
    update_dashboard(topic, all_turns, "讨论完成")
    send_or_update_card(topic, all_turns, "✅ 讨论完成", msg_id)
    if task_id:
        kanban_complete_task(task_id)
        kanban_comment(task_id, "✅ 三省六部圆桌讨论完成，共{}轮发言".format(len(all_turns)))

    with open("/opt/data/roundtable_result.json", "w") as f:
        json.dump({"topic": topic, "turns": all_turns}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成！共{len(all_turns)}轮发言")
    if task_id:
        print(f"📋 看板查看：http://82.156.210.39:9119/kanban")
        print(f"   → 查找任务「🏛️ 圆桌：{ts}」点开看评论")


if __name__ == "__main__":
    asyncio.run(run())
