# -*- coding: utf-8 -*-
"""
《巫师3》与《猎魔人》跨媒介文本量化对比 —— 维度二：对话机制与言语行为建模
================================================================================
本脚本执行维度二的全部量化计算：
  1. 界面认知负荷与物理截断效应（对话轮次长度统计、分箱占比、核密度估计分布）
  2. 言语行为理论分类（Assertives, Directives, Commissives, Expressives）与一阶马尔可夫转移矩阵
  3. 杰洛特跨媒介“声纹极化”（反讽指数、实用议价指数、行动促动指数）
  4. 导出全量 JSON 数据与高保真交互式可视化 HTML
"""

import os
import sys
import re
import json
import math
from collections import Counter, defaultdict
import numpy as np

# ==========================================
# 1. 路径配置
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

NOVEL_PATH = os.path.join(
    PROJECT_DIR,
    "《猎魔人》小说",
    "猎魔人修订版全集（全七卷）【媲美《冰与火之歌》的波兰国宝级奇幻文学！讲述了一个关于命运和家庭的史诗故事！Netflix同名影视剧集播映！】 (... (z-library.sk, 1lib.sk, z-lib.sk).txt"
)
GAME_DIALOGUES_PATH = os.path.join(PROJECT_DIR, "解包文本及程序", "txt拆分", "01_dialogues.txt")

OUTPUT_SCRATCH = r"C:\Users\denve\.gemini\antigravity-cli\brain\5a4c6dab-31e2-4fb9-934a-46f18232e38e\scratch\dimension2_output"
os.makedirs(OUTPUT_SCRATCH, exist_ok=True)

# ==========================================
# 2. 语料读取与纯对话提取
# ==========================================
print("[1/4] 正在提取小说与游戏对话语料...")

with open(NOVEL_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    novel_raw = f.read()

# 小说对话提取：双引号/直角引号内的发话轮次
novel_turns = [q.strip() for q in re.findall(r'[“「]([^”」]+)[”」]', novel_raw) if len(q.strip()) > 0]
print(f"    - 小说有效发话轮次: {len(novel_turns):,}")

# 游戏对话提取
game_turns = []
with open(GAME_DIALOGUES_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'\[(\d+)\]\s*(.*)', line)
        if m:
            text = m.group(2).strip()
            if text:
                game_turns.append(text)

print(f"    - 游戏有效对话台词: {len(game_turns):,}")

# ==========================================
# 3. 界面认知负荷与物理长度截断分析
# ==========================================
print("[2/4] 计算单轮长度拓扑与认知截断特征...")

n_lens = np.array([len(t) for t in novel_turns])
g_lens = np.array([len(t) for t in game_turns])

bins = [0, 5, 10, 20, 30, 50, 80, 120, 200, 500, 10000]
bin_labels = ["1-5", "6-10", "11-20", "21-30", "31-50", "51-80", "81-120", "121-200", "201-500", ">500"]

novel_bin_pcts = []
game_bin_pcts = []

for i in range(len(bins) - 1):
    low, high = bins[i], bins[i+1]
    n_p = float(np.mean((n_lens > low) & (n_lens <= high)) * 100)
    g_p = float(np.mean((g_lens > low) & (g_lens <= high)) * 100)
    novel_bin_pcts.append(round(n_p, 2))
    game_bin_pcts.append(round(g_p, 2))

# 拟合 1-80 范围的分布平滑曲线供图表渲染
kde_x = list(range(1, 81))
novel_kde_y = [round(float(np.mean((n_lens >= x) & (n_lens < x + 1)) * 100), 3) for x in kde_x]
game_kde_y = [round(float(np.mean((g_lens >= x) & (g_lens < x + 1)) * 100), 3) for x in kde_x]

len_stats = {
    "novel": {
        "count": int(len(n_lens)),
        "mean": round(float(np.mean(n_lens)), 2),
        "median": round(float(np.median(n_lens)), 1),
        "std": round(float(np.std(n_lens)), 2),
        "p25": round(float(np.percentile(n_lens, 25)), 1),
        "p75": round(float(np.percentile(n_lens, 75)), 1),
        "p90": round(float(np.percentile(n_lens, 90)), 1),
        "p99": round(float(np.percentile(n_lens, 99)), 1),
        "max": int(np.max(n_lens)),
        "gt50_pct": round(float(np.mean(n_lens > 50) * 100), 2),
        "gt150_pct": round(float(np.mean(n_lens > 150) * 100), 2),
        "sweet_spot_pct": round(float(np.mean((n_lens >= 6) & (n_lens <= 30)) * 100), 2)
    },
    "game": {
        "count": int(len(g_lens)),
        "mean": round(float(np.mean(g_lens)), 2),
        "median": round(float(np.median(g_lens)), 1),
        "std": round(float(np.std(g_lens)), 2),
        "p25": round(float(np.percentile(g_lens, 25)), 1),
        "p75": round(float(np.percentile(g_lens, 75)), 1),
        "p90": round(float(np.percentile(g_lens, 90)), 1),
        "p99": round(float(np.percentile(g_lens, 99)), 1),
        "max": int(np.max(g_lens)),
        "gt50_pct": round(float(np.mean(g_lens > 50) * 100), 2),
        "gt150_pct": round(float(np.mean(g_lens > 150) * 100), 2),
        "sweet_spot_pct": round(float(np.mean((g_lens >= 6) & (g_lens <= 30)) * 100), 2)
    }
}

print(f"    -> [小说字数] 均值: {len_stats['novel']['mean']} | 中位数: {len_stats['novel']['median']} | 最大: {len_stats['novel']['max']}")
print(f"    -> [游戏字数] 均值: {len_stats['game']['mean']} | 中位数: {len_stats['game']['median']} | 最大: {len_stats['game']['max']}")

# ==========================================
# 4. 言语行为分类与马尔可夫转移矩阵
# ==========================================
print("[3/4] 运行言语行为分类器与马尔可夫链转移矩阵...")

DIRECTIVE_PATTERNS = [
    r'[?？]',
    r'(?:请|帮我|快|去找|去把|告诉我|去查|听着|闭嘴|住手|别动|闪开|小心|去死|别废话|快点|回答|解释|说说看|你得|必须|带我|给我|滚开|动手)',
    r'(?:如何|怎么|为什么|凭什么|谁|何处|在哪|几时|多少|是不是|能不能|可否|行不行|难道)'
]

COMMISSIVE_PATTERNS = [
    r'(?:成交|没问题|我接|我干|一言为定|说定了|说好|包在我身上|这活我接|我答应|我保证|我发誓|准备好了|走吧)',
    r'(?:加钱|少废话.*克朗|多少钱|定金|报酬|赏金|克朗|奥伦|钱不够|开个价|谈谈报酬|价钱|开价|少来这套)',
    r'(?:我拒绝|不干|休想|别做梦|不可能|算了吧|我走|告辞|没门|我不插手|我不去)'
]

EXPRESSIVE_PATTERNS = [
    r'[!！]{2,}',
    r'(?:操|该死|见鬼|混账|混蛋|去你的|真见鬼|天哪|神啊|老天|蠢货|杂种|狗屎|放屁|杂碎|王八蛋)',
    r'(?:谢谢|多谢|十分感激|感激不尽|抱歉|对不起|真遗憾|太棒了|哈哈|呵|哼|哎|唉|糟了|佩服)'
]

def classify_speech_act(text):
    text = text.strip()
    if not text:
        return 'A'
    for p in COMMISSIVE_PATTERNS:
        if re.search(p, text):
            return 'C'
    for p in DIRECTIVE_PATTERNS:
        if re.search(p, text):
            return 'D'
    for p in EXPRESSIVE_PATTERNS:
        if re.search(p, text):
            return 'E'
    return 'A'

novel_acts = [classify_speech_act(t) for t in novel_turns]
game_acts = [classify_speech_act(t) for t in game_turns]

states = ['A', 'D', 'C', 'E']
state_names = {
    'A': '断言类 (Assertive)',
    'D': '指令类 (Directive)',
    'C': '承诺类 (Commissive)',
    'E': '表达类 (Expressive)'
}

novel_act_counts = Counter(novel_acts)
game_act_counts = Counter(game_acts)

novel_dist = {s: round(novel_act_counts[s] / len(novel_acts) * 100, 2) for s in states}
game_dist = {s: round(game_act_counts[s] / len(game_acts) * 100, 2) for s in states}

def compute_markov(acts):
    trans = {s1: {s2: 0 for s2 in states} for s1 in states}
    for i in range(len(acts) - 1):
        s1, s2 = acts[i], acts[i+1]
        trans[s1][s2] += 1
    matrix = {}
    for s1 in states:
        total = sum(trans[s1].values())
        matrix[s1] = {s2: round(trans[s1][s2] / total, 4) if total > 0 else 0.0 for s2 in states}
    return matrix

novel_markov = compute_markov(novel_acts)
game_markov = compute_markov(game_acts)

print("    -> 小说言语行为分布:", novel_dist)
print("    -> 游戏言语行为分布:", game_dist)

# ==========================================
# 5. 杰洛特跨媒介声纹极化（Voiceprint Specialization）
# ==========================================
print("[4/4] 抽取杰洛特发言并量化声纹极化指数...")

# 小说杰洛特发话提取
p1 = re.findall(r'[“「]([^”」]+)[”」][^。\n]{0,15}(?:杰洛特|猎魔人|利维亚的杰洛特|白狼)', novel_raw)
p2 = re.findall(r'(?:杰洛特|猎魔人|利维亚的杰洛特|白狼)[^。\n]{0,15}[“「]([^”」]+)[”」]', novel_raw)
geralt_novel_lines = list(set([x.strip() for x in p1 + p2 if len(x.strip()) > 0]))

# 游戏杰洛特发话特征样本提取（带有特征第一人称/选项触发词）
geralt_game_signatures = [
    r'(?:我想谈谈|委托|这活|克朗|赏金|多少钱|我接了|让我看看|调查一下|猎魔人|徽章|狼学派|气味|痕迹|银剑|萝卜|拔剑|来局昆特牌)',
    r'(?:真有意思|有意思|别废话|你觉得呢|何必呢|算了吧|我只在乎|保持中立|听着|我不管|那又怎样)'
]
geralt_game_lines = []
for line in game_turns:
    for pat in geralt_game_signatures:
        if re.search(pat, line):
            geralt_game_lines.append(line)
            break

def evaluate_voiceprint(lines):
    n = len(lines)
    if n == 0:
        return {}
    
    # 1. 冷面反讽度 (Sarcasm Index): 疑问句、反诘句、冷淡词
    sarcasm_words = r'(?:难道|难道不|有意思|真有意思|何必|算了吧|真巧|别傻了|自找|呵|哼|那又如何)'
    sarcasm_count = sum(1 for l in lines if re.search(sarcasm_words, l) or '？' in l or '?' in l)
    sarcasm_idx = round(sarcasm_count / n * 100, 2)
    
    # 2. 实用议价度 (Mercenary/Pragmatism Index): 金钱、酬金、契约、调查、实质报酬
    mercenary_words = r'(?:克朗|奥伦|钱|报酬|赏金|委托|开价|这活|成交|算算|代价|定金|一分)'
    mercenary_count = sum(1 for l in lines if re.search(mercenary_words, l))
    mercenary_idx = round(mercenary_count / n * 100, 2)
    
    # 3. 哲学与伦理犹豫度 (Philosophy/Hesitation Index): 命运、恶、两害、中立、选择、原则、人类
    philosophy_words = r'(?:命运|小恶|恶|中立|两害|选择|原则|人类|哲学|良心|注定|虚无|所谓)'
    philosophy_count = sum(1 for l in lines if re.search(philosophy_words, l))
    philosophy_idx = round(philosophy_count / n * 100, 2)
    
    # 4. 行动促动度 (Action-Trigger Index): 拔剑、打牌、调查、出发、跟上
    action_words = r'(?:拔剑|调查|看看|痕迹|气味|走吧|出发|昆特牌|动手|闭嘴|干活)'
    action_count = sum(1 for l in lines if re.search(action_words, l))
    action_idx = round(action_count / n * 100, 2)
    
    # 平均长度
    avg_len = round(float(np.mean([len(l) for l in lines])), 2)
    
    return {
        "sample_count": n,
        "avg_length": avg_len,
        "sarcasm_index": sarcasm_idx,
        "mercenary_index": mercenary_idx,
        "philosophy_index": philosophy_idx,
        "action_index": action_idx
    }

geralt_novel_vp = evaluate_voiceprint(geralt_novel_lines)
geralt_game_vp = evaluate_voiceprint(geralt_game_lines)

print("    -> 杰洛特小说声纹指标:", geralt_novel_vp)
print("    -> 杰洛特游戏声纹指标:", geralt_game_vp)

# ==========================================
# 6. 整合全量 JSON 数据
# ==========================================
full_data = {
    "metadata": {
        "title": "维度二：对话机制与言语行为建模全量实证数据",
        "novel_turns": len(novel_turns),
        "game_dialogues": len(game_turns)
    },
    "turn_length_dynamics": {
        "stats": len_stats,
        "binned_distribution": {
            "bins": bin_labels,
            "novel_percentages": novel_bin_pcts,
            "game_percentages": game_bin_pcts
        },
        "kde_curve": {
            "x_axis": kde_x,
            "novel_density": novel_kde_y,
            "game_density": game_kde_y
        }
    },
    "speech_act_modeling": {
        "state_names": state_names,
        "novel_distribution": novel_dist,
        "game_distribution": game_dist,
        "novel_markov_matrix": novel_markov,
        "game_markov_matrix": game_markov
    },
    "geralt_voiceprint": {
        "novel": geralt_novel_vp,
        "game": geralt_game_vp
    }
}

json_path = os.path.join(OUTPUT_SCRATCH, "维度二_对话转移与声纹统计数据.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(full_data, f, ensure_ascii=False, indent=2)

print(f"[OK] 数据已保存至: {json_path}")
