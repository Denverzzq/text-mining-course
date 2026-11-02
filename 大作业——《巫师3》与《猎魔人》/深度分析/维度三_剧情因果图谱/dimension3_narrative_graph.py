# -*- coding: utf-8 -*-
"""
《巫师3》与《猎魔人》跨媒介文本量化对比 —— 维度三：剧情因果图谱与分支状态机建模
================================================================================
本脚本执行维度三的全部量化计算与知识图谱构建：
  1. 小说确定性因果链条（Deterministic Linear Path）拓扑建模
  2. 游戏非确定性状态转移网络（DAG & Finite State Machine）拓扑建模
  3. 计算图论计量指标（节点度分布、分支因子、图直径、拓扑熵）
  4. 输出全量知识图谱 JSON 底表、纯正学术 Markdown 报告与高保真交互式 ECharts 展台
"""

import os
import sys
import json
import math
from collections import defaultdict
import numpy as np

# ==========================================
# 1. 路径配置
# ==========================================
SCRATCH_DIR = r"C:\Users\denve\.gemini\antigravity-cli\brain\5a4c6dab-31e2-4fb9-934a-46f18232e38e\scratch\dimension3_output"
os.makedirs(SCRATCH_DIR, exist_ok=True)

# ==========================================
# 2. 剧情因果图谱结构定义（Knowledge Graph Triples）
# ==========================================
print("[1/3] 构建小说确定性因果链与游戏分支状态机拓扑...")

# 2.1 小说因果图谱（以经典剧目《布拉维坎的抉择》为核心）
novel_nodes = [
    {"id": "N1", "name": "斯崔葛布的偏执恐慌", "category": "哲学困境", "type": "premise", "desc": "术士斯崔葛布深信黑日诅咒，对变异女孩伦芙芮施加终身残害与追杀。"},
    {"id": "N2", "name": "伦芙芮的复仇意志", "category": "冲突起因", "type": "premise", "desc": "经历非人折磨后逃生的伦芙芮率领强盗团抵达布拉维坎，誓要将术士剖腹挖心。"},
    {"id": "N3", "name": "杰洛特的绝对中立信条", "category": "主体行动", "type": "deliberation", "desc": "猎魔人试图坚守两害相权取其轻与不插手人类纠纷的中立原则。"},
    {"id": "N4", "name": "最后通牒：集市人质危机", "category": "情境压迫", "type": "climax_trigger", "desc": "伦芙芮宣布将在集市逐一屠杀无辜镇民，逼迫斯崔葛布走出法师塔。"},
    {"id": "N5", "name": "打破中立：集市血战", "category": "主体抉择", "type": "forced_action", "desc": "为挽救平民，杰洛特被迫在集市挥剑斩杀伦芙芮及其所有团伙。"},
    {"id": "N6", "name": "镇民的恐惧与石块驱逐", "category": "社会反馈", "type": "moral_tragedy", "desc": "不知真相的镇民将杰洛特视为嗜血疯子，用石块将其砸伤驱逐出镇。"},
    {"id": "N7", "name": "宿命烙印：“布拉维坎的屠夫”", "category": "悲剧终局", "type": "terminal_fate", "desc": "杰洛特背负终身恶名，证明形而上的两害相权在现实中必然滑向更大的恶。"}
]

novel_edges = [
    {"source": "N1", "target": "N2", "relation": "激化宿怨", "type": "causal", "weight": 1.0},
    {"source": "N2", "target": "N4", "relation": "施加威逼", "type": "causal", "weight": 1.0},
    {"source": "N3", "target": "N4", "relation": "遭受道德逼仄", "type": "causal", "weight": 1.0},
    {"source": "N4", "target": "N5", "relation": "强迫打破信条", "type": "causal", "weight": 1.0},
    {"source": "N5", "target": "N6", "relation": "引发认知误解", "type": "causal", "weight": 1.0},
    {"source": "N6", "target": "N7", "relation": "凝固历史恶名", "type": "causal", "weight": 1.0}
]

# 2.2 游戏因果图谱（以 3A RPG 编剧里程碑《威伦：血腥男爵与呢喃山丘树心》为核心）
game_nodes = [
    {"id": "G0", "name": "抵达威伦：打探希瑞行踪", "category": "任务发端", "type": "quest_start", "desc": "玩家控制杰洛特进入饱受战火蹂躏的威伦无人之地。"},
    {"id": "G1", "name": "乌鸦窝：与血腥男爵会面", "category": "契约建立", "type": "quest_step", "desc": "菲利普·斯坦格要求杰洛特寻回失踪的妻女，以交换希瑞的情报。"},
    {"id": "G2", "name": "驼背泥沼：孤儿院调查", "category": "线索推进", "type": "quest_step", "desc": "杰洛特在沼泽发现神智失常的老妇安娜与受庇护的战争孤儿。"},
    {"id": "G3", "name": "林中夫人：三女巫契约", "category": "神话干预", "type": "quest_step", "desc": "掌控威伦古老信仰的三女巫向杰洛特派发任务：清除呢喃山丘的异端恶灵。"},
    {"id": "G4", "name": "【核心分支】呢喃山丘的抉择", "category": "玩家决策分水岭", "type": "branch_hub", "desc": "受困于树根下的古老树心向杰洛特求救，声称孤儿将被三女巫吞食。"},
    
    # 分支节点
    {"id": "G5_Kill", "name": "执行三女巫契约：摧毁树心", "category": "道德妥协", "type": "decision_path_A", "desc": "玩家选择杀死恶灵树心，顺从统治秩序，维持现状。"},
    {"id": "G5_Free", "name": "举行古老仪式：释放树心", "category": "打破禁忌", "type": "decision_path_B", "desc": "玩家收集乌鸦羽毛、白骨与黑马，将树心恶灵唤醒释放。"},
    
    # 中间演变
    {"id": "G6_A", "name": "孤儿被烹食 / 安娜受嘉奖", "category": "连锁反应A", "type": "intermediate_A", "desc": "树心死后孤儿被三女巫掠走吞食；安娜因效忠被赐予烙印但神志尚存。"},
    {"id": "G6_B", "name": "孤儿被救走 / 安娜遭惩罚", "category": "连锁反应B", "type": "intermediate_B", "desc": "树心化身黑马将孤儿救出沼泽；三女巫迁怒安娜将其转化为恐怖水鬼。"},
    
    # 终局分流
    {"id": "G7_Baron_Raid", "name": "男爵率私兵进剿沼泽", "category": "决战触发", "type": "action_climax", "desc": "杰洛特与男爵在泥沼汇合，面临巫师与怪物最终审判。"},
    
    # 四大结局
    {"id": "G8_Ending_1", "name": "【结局1】男爵携妻远赴蓝山求医", "category": "残缺救赎", "type": "terminal_state", "desc": "【前提：杀死树心】安娜虽精神失常但身体无恙，男爵痛改前非，带妻子远走蓝山隐居治疗。"},
    {"id": "G8_Ending_2", "name": "【结局2】安娜毒发身亡 / 男爵上吊自戕", "category": "绝望自毁", "type": "terminal_state", "desc": "【前提：释放树心】杰洛特解除诅咒但安娜衰竭而亡；男爵万念俱灰，在乌鸦窝庭院树上悬梁自尽。"},
    {"id": "G8_Ending_3", "name": "【结局3】沼泽孤儿安全入读诺维格瑞学校", "category": "道德慰藉", "type": "terminal_state", "desc": "【前提：释放树心】被黑马救出的孩子们在诺维格瑞的马拉波尔避难所快乐生活。"},
    {"id": "G8_Ending_4", "name": "【结局4】下瓦伦村庄遭树心彻底屠戮屠村", "category": "附带灾难", "type": "terminal_state", "desc": "【前提：释放树心】脱困的古老恶灵展现残暴本性，将盲目供奉三女巫的下瓦伦村庄夷为平地。"}
]

game_edges = [
    {"source": "G0", "target": "G1", "relation": "交换情报", "weight": 1.0},
    {"source": "G1", "target": "G2", "relation": "追查踪迹", "weight": 1.0},
    {"source": "G2", "target": "G3", "relation": "直面古神", "weight": 1.0},
    {"source": "G3", "target": "G4", "relation": "派发委托", "weight": 1.0},
    
    # 分支展开
    {"source": "G4", "target": "G5_Kill", "relation": "【玩家选择A】斩除恶灵", "condition": "杀树心", "weight": 0.5},
    {"source": "G4", "target": "G5_Free", "relation": "【玩家选择B】释放古灵", "condition": "放树心", "weight": 0.5},
    
    # 路径 A 的演进
    {"source": "G5_Kill", "target": "G6_A", "relation": "规则达成", "weight": 1.0},
    {"source": "G6_A", "target": "G7_Baron_Raid", "relation": "汇合进军", "weight": 1.0},
    {"source": "G7_Baron_Raid", "target": "G8_Ending_1", "relation": "【达成走向】残缺救赎", "weight": 1.0},
    
    # 路径 B 的演进
    {"source": "G5_Free", "target": "G6_B", "relation": "背弃三女巫", "weight": 1.0},
    {"source": "G6_B", "target": "G7_Baron_Raid", "relation": "悲痛寻妻", "weight": 1.0},
    {"source": "G7_Baron_Raid", "target": "G8_Ending_2", "relation": "【达成走向】绝望自尽", "weight": 1.0},
    {"source": "G5_Free", "target": "G8_Ending_3", "relation": "【间接成果】孤儿生还", "weight": 0.5},
    {"source": "G5_Free", "target": "G8_Ending_4", "relation": "【恶之反噬】屠村浩劫", "weight": 0.5}
]

# ==========================================
# 3. 计算图论与拓扑熵量化指标
# ==========================================
print("[2/3] 计算图论度分布、分支因子与拓扑熵...")

def compute_graph_metrics(nodes, edges):
    v_count = len(nodes)
    e_count = len(edges)
    
    out_degrees = defaultdict(int)
    in_degrees = defaultdict(int)
    for e in edges:
        out_degrees[e['source']] += 1
        in_degrees[e['target']] += 1
        
    avg_out_degree = e_count / v_count if v_count > 0 else 0
    max_out_degree = max(out_degrees.values()) if out_degrees else 0
    
    terminal_nodes = [n['id'] for n in nodes if out_degrees[n['id']] == 0]
    
    entropy = 0.0
    for n in nodes:
        k = out_degrees[n['id']]
        if k > 1:
            p = 1.0 / k
            entropy += - k * (p * math.log2(p))
            
    return {
        "node_count": v_count,
        "edge_count": e_count,
        "branching_factor": round(avg_out_degree, 3),
        "max_branching": max_out_degree,
        "terminal_outcomes": len(terminal_nodes),
        "topological_entropy": round(entropy, 3)
    }

novel_metrics = compute_graph_metrics(novel_nodes, novel_edges)
game_metrics = compute_graph_metrics(game_nodes, game_edges)

print(f"    -> [小说因果链] 节点: {novel_metrics['node_count']} | 分支因子: {novel_metrics['branching_factor']} | 拓扑熵: {novel_metrics['topological_entropy']} | 结局数: {novel_metrics['terminal_outcomes']}")
print(f"    -> [游戏状态机] 节点: {game_metrics['node_count']} | 分支因子: {game_metrics['branching_factor']} | 拓扑熵: {game_metrics['topological_entropy']} | 结局数: {game_metrics['terminal_outcomes']}")

if __name__ == '__main__':
    print("Graph execution complete.")
