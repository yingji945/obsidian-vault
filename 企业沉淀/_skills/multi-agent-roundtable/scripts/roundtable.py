#!/usr/bin/env python3
"""三省六部圆桌脚本 - 运营/数据/法务三方讨论"""
import json, os, sys, asyncio

# Ensure autogen packages are importable
pypath = os.path.expanduser("~/.local/lib/python3.13/site-packages")
if pypath not in sys.path:
    sys.path.insert(0, pypath)

# Read credentials
env = {}
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v
API_KEY = env['DASHSCOPE_API_KEY']
BASE_URL = env.get('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="qwen-max", api_key=API_KEY, base_url=BASE_URL, temperature=0.5,
    model_info={"vision": False, "function_calling": True, "json_output": True, "structured_output": False, "family": "unknown"},
)

# Create ministers (names: ASCII only!)
data_agent = AssistantAgent(
    name="data_minister", model_client=model_client,
    system_message="你是瑞幸即享咖啡的「户部尚书·数据大臣」。专长：数据分析、SQL取数、漏斗分析、AB实验、ROI计算。数据说话，不讲虚的。如果别人缺数据支撑，要质疑。",
)
ops_agent = AssistantAgent(
    name="ops_minister", model_client=model_client,
    system_message="你是瑞幸即享咖啡的「礼部尚书·运营大臣」。专长：活动策划、积分商城、用户触达、扫码活动。站在用户角度，给出可落地方案。如果别人只谈成本不谈体验，要提醒。",
)
legal_agent = AssistantAgent(
    name="legal_minister", model_client=model_client,
    system_message="你是瑞幸即享咖啡的「刑部尚书·法务大臣」。专长：合规审查、备案、个税、隐私保护、反作弊。严谨但务实，风险必须提前说清。如果别人有法律漏洞，要指出。",
)

termination = TextMentionTermination("同意") | TextMentionTermination("结论") | MaxMessageTermination(10)

team = SelectorGroupChat(
    participants=[data_agent, ops_agent, legal_agent],
    model_client=model_client, termination_condition=termination,
    selector_prompt="你主持圆桌。话题：{history}。大臣：{participants}。从{roles}选下一个发言。不要连续选同一个人。讨论充分时说「结论」总结。",
)

async def run(topic: str) -> str:
    parts = []
    async for msg in team.run_stream(task=topic):
        if hasattr(msg, 'source') and hasattr(msg, 'content') and msg.content:
            parts.append(f"**{msg.source}**：{msg.content}")
    return "\n\n".join(parts)

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "积分商城改版方向"
    result = asyncio.run(run(topic))
    with open("/opt/data/roundtable_result.json", "w") as f:
        json.dump({"topic": topic, "result": result}, f, ensure_ascii=False, indent=2)
    print(result)
