import random
import csv
import os
from datetime import datetime

# ▼追加：グラフ描画に必要なライブラリ
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("\n【注意】グラフ機能には 'pandas' と 'matplotlib' が必要です。")
    print("Pydroidのメニュー > Pip > install からインストールしてください。")

# =========================================================
# The Mycologist – Mycelium Ops Simulation (Android Edition)
# =========================================================

# ▼▼▼ Androidのダウンロードフォルダを保存先に指定 ▼▼▼
# これで「ファイル」アプリの「ダウンロード」の中に保存されます
DOWNLOAD_DIR = "/storage/emulated/0/Download"

if os.path.exists(DOWNLOAD_DIR):
    BASE_DIR = DOWNLOAD_DIR
else:
    # ダウンロードフォルダが見つからない場合は、現在地を使う
    BASE_DIR = os.getcwd()

LOG_PATH = os.path.join(BASE_DIR, "run_log.csv")
IMG_PATH = os.path.join(BASE_DIR, "audit_chart.png")

print(f"📂 保存先フォルダ: {BASE_DIR}")
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

TEXT = {
    "ACT1": "培地設計",
    "P1": "しいたけ（主人公）",
    "P2": "えのき（堅実）",
    "P3": "まいたけ（鈍感力）",
}

def t(k: str) -> str: return TEXT.get(k, k)

POISON_MUSHROOMS = [
    {"jp": "ドクツルタケ", "alias": "死の天使", "danger": 5},
    {"jp": "ベニテングダケ", "alias": "赤い幻惑", "danger": 3},
]

DOSSIER = {
    "DOC001": {"name": "古い培地コスト表", "power": 20, "unlock_day": 2},
    "DOC002": {"name": "巡回記録の欠落", "power": 15, "unlock_day": 4},
}

class GameLogger:
    def __init__(self, filepath=LOG_PATH):
        self.filepath = filepath
        self.fieldnames = [
            "day", "player", "facility", "action", "event",
            "hp", "mp", "money", "spore_level", "pressure", "security", "morale"
        ]
        # 上書きモードで開始
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=self.fieldnames).writeheader()

    def log(self, day, player, facility, action, event=""):
        row = {
            "day": int(day),
            "player": player.name,
            "facility": facility.name,
            "action": action,
            "event": event,
            "hp": int(player.HP), "mp": int(player.MP), "money": int(player.money),
            "spore_level": int(facility.spore_level),
            "pressure": int(facility.pressure),
            "security": int(facility.security),
            "morale": int(facility.morale),
        }
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=self.fieldnames).writerow(row)

# -----------------------------
# グラフ描画（画面表示 ＆ 保存）
# -----------------------------
def visualize_log(log_path=LOG_PATH, output_img=IMG_PATH):
    if not HAS_MATPLOTLIB: return
    print(f"\n📊 グラフ生成中...")
    try:
        df = pd.read_csv(log_path)
        if df.empty:
            print("ログが空です。")
            return
            
        daily_df = df.groupby("day").last().reset_index()

        fig, ax1 = plt.subplots(figsize=(10, 6))
        plt.title("Audit Trail: Risk vs Cash Flow", fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.5)

        # 左軸：収支
        color_money = '#2ca02c'
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Cash Flow', color=color_money, fontweight='bold')
        line1 = ax1.plot(daily_df["day"], daily_df["money"], color=color_money, marker='o', label='Cash Flow')
        ax1.tick_params(axis='y', labelcolor=color_money)

        # 右軸：リスク
        ax2 = ax1.twinx()
        line2 = ax2.plot(daily_df["day"], daily_df["spore_level"], color='#d62728', linestyle='--', label='Risk Level')
        ax2.set_ylabel('Risk (0-100)', color='#d62728')
        ax2.set_ylim(0, 105)

        # 保存
        plt.tight_layout()
        plt.savefig(output_img)
        print(f"✅ 画像を保存しました: {output_img}")
        
        # ★ここで画面に表示★
        print("📱 画面に表示します...")
        plt.show() 

    except Exception as e:
         print(f"❌ Graph Error: {e}")

class Facility:
    def __init__(self, name="菌糸中央"):
        self.name, self.spore_level, self.pressure, self.security, self.morale = name, 25, 20, 75, 55
    def check_for_event(self):
        if self.spore_level >= 80: return "SPORE_CRISIS"
        return None

class Player:
    def __init__(self, name):
        self.name = name
        self.evidence = []
        self.HP, self.MP, self.money, self.focus = 100, 50, -50000, 10

    def auto_action(self, facility, day, logger):
        # ランダム行動
        act = random.randint(1, 3)
        if act == 1: # 収益活動
            gain = random.randint(500, 1500)
            self.money += gain
            facility.spore_level += 2
            logger.log(day, self, facility, "culture", f"+{gain}")
        elif act == 2: # 巡回
            facility.spore_level = max(0, facility.spore_level - 10)
            logger.log(day, self, facility, "patrol", "safe")
        else: # 探索
            logger.log(day, self, facility, "search", "nothing")

def start_simulation():
    print("=== Mycelium Ops: Auto-Run (Download Folder Ver) ===")
    
    logger = GameLogger(LOG_PATH)
    facility = Facility()
    player = Player("Auto-Shiitake")
    
    day = 1
    max_days = 15

    while day <= max_days:
        # 1日3回行動
        for _ in range(3):
            player.auto_action(facility, day, logger)
        
        print(f"Day {day} 終了... (収支: {player.money})")
        day += 1

    print(f"\n✅ シミュレーション完了！")
    visualize_log(LOG_PATH, IMG_PATH)
    print(f"\n【確認方法】")
    print(f"スマホの「ファイル」アプリまたは「アルバム」を開き、")
    print(f"「ダウンロード」フォルダ内の 'audit_chart.png' を探してください。")

if __name__ == "__main__":
    start_simulation()
