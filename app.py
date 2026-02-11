from flask import Flask, render_template, request, jsonify
from dataclasses import dataclass, asdict
import os
import time

# Optional OpenAI usage
USE_OPENAI = False
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        USE_OPENAI = True
    except Exception:
        USE_OPENAI = False

app = Flask(__name__)

@dataclass
class Item:
    name: str
    official_rank: int
    description: str

OFFICIAL_ITEMS = [
    Item("氧氣瓶", 1, "呼吸"),
    Item("水", 2, "補充液體"),
    Item("星圖", 3, "導航"),
    Item("食物濃縮物", 4, "營養"),
    Item("太陽能電池板", 5, "電力"),
    Item("衣服補丁", 6, "防止失壓"),
    Item("醫療箱", 7, "急救"),
    Item("繩索", 8, "安全/移動"),
    Item("降落傘", 9, "防止隕石碰撞"),
    Item("救生筏", 10, "隱蔽所"),
    Item("信號鏡", 11, "通信"),
    Item("手電筒", 12, "照明"),
    Item("火柴", 13, "點火"),
    Item("月球地圖", 14, "導航輔助"),
    Item("磁羅盤", 15, "導航（不太有效）"),
]

def calculate_score(submitted_names):
    off_map = {item.name: item.official_rank - 1 for item in OFFICIAL_ITEMS}
    score = 0
    for i, name in enumerate(submitted_names):
        if name in off_map:
            score += abs(off_map[name] - i)
        else:
            score += len(OFFICIAL_ITEMS)
    return score

@app.route("/")
def index():
    items = [asdict(it) for it in OFFICIAL_ITEMS]
    return render_template("index.html", items=items, openai_enabled=USE_OPENAI)

@app.route("/evaluate", methods=["POST"]) 
def evaluate():
    data = request.get_json()
    order = data.get("order", [])
    if not isinstance(order, list) or len(order) != len(OFFICIAL_ITEMS):
        return jsonify({"error": "invalid order"}), 400

    score = calculate_score(order)

    official_list = [asdict(it) for it in OFFICIAL_ITEMS]
    submitted_list = [{"name": name, "pos": i + 1} for i, name in enumerate(order)]

    per_item = []
    off_pos_map = {it.name: it.official_rank for it in OFFICIAL_ITEMS}
    for i, name in enumerate(order):
        per_item.append({
            "name": name,
            "submitted_rank": i + 1,
            "official_rank": off_pos_map.get(name, None),
            "diff": None if name not in off_pos_map else abs(off_pos_map[name] - (i + 1))
        })

    return jsonify({
        "score": score,
        "submitted": submitted_list,
        "official": official_list,
        "per_item": per_item
    })

def local_chat_response(message: str):
    """簡易本地回應（fallback）：提供有用提示與回覆"""
    message_lower = message.lower()
    # Simple rule-based hints
    if "oxygen" in message_lower or "氧氣" in message_lower:
        return "氧氣是最關鍵的資源；確保氧氣瓶放在前三名。"
    if "water" in message_lower or "水" in message_lower:
        return "水對倖存很重要，通常排在前二至前三名。"
    if "rank" in message_lower or "排名" in message_lower:
        return "你可以把物品拖放後按「評分」，系統會顯示與 NASA 官方排名的差距與分數。"
    # Generic helpful reply
    tips = [
        "試著把維持生命的物品（氧氣、水、食物）放在最前面。",
        "導航工具對長距離返回基地有幫助，但在短期生存時可能不如氧氣或水重要。",
        "如果你想要更詳細的解釋，輸入像「為什麼氧氣重要？」之類的問題。"
    ]
    # Rotate by time to add a bit variety
    return tips[int(time.time()) % len(tips)]

@app.route("/chat", methods=["POST"]) 
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400

    # If OpenAI available, use it
    if USE_OPENAI:
        try:
            # Build a short conversation: system + user
            system = "你是友善的助理，專門提供關於月球倖存任務的實用建議。"
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=400,
            )
            text = resp["choices"][0]["message"]["content"].strip()
            return jsonify({"reply": text, "source": "openai"})
        except Exception as e:
            # Fallback to local response if OpenAI fails
            fallback = f"（OpenAI 呼叫失敗：{str(e)[:120]}）\n" + local_chat_response(message)
            return jsonify({"reply": fallback, "source": "fallback"})
    else:
        # Local rule-based reply
        reply = local_chat_response(message)
        return jsonify({"reply": reply, "source": "local"})

if __name__ == "__main__":
    # 0.0.0.0 so Codespaces can forward port
    app.run(host="0.0.0.0", port=5000, debug=True)
