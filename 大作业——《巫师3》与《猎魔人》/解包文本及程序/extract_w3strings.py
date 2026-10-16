
"""
Witcher 3 .w3strings Decoder & Story Text Extractor
Supports:
  - Version 162 / 163 (Classic Witcher 3, UTF-16LE)
  - Version 164 (Next-Gen Witcher 3, UTF-8)

Features:
  1. Complete string unpacking to CSV (ID, KeyHash, Text)
  2. Dialogue & subtitle extraction (ordered by string ID for dialogue tree flow)
  3. Quest logs & Dandelion journal entries
  4. In-game books, letters, notes & bestiary entries
  5. Cleaned formatting (converts <br> to paragraphs, strips HTML tags)
"""

import os
import sys
import struct
import re
import argparse

# Official CD Projekt Red language keys and obfuscation magic values
LANGUAGES = {
    0x00000000: ("none/cn", 0x00000000),
    0x24987354: ("cz", 0x21793217),
    0x75886138: ("de", 0x42791159),
    0x43975139: ("en", 0x79321793),
    0x18796651: ("es", 0x42387566),
    0x23863176: ("fr", 0x75921975),
    0x42378932: ("hu", 0x67823218),
    0x45931894: ("it", 0x12375973),
    0x54834893: ("jp", 0x59825646),
    0x83496237: ("pl", 0x73946816),
    0x63481486: ("ru", 0x42386347),
    0x18632176: ("zh", 0x16875467),
}

def read_section_count(f):
    """Reads a bit6-encoded section count from the binary stream."""
    first = f.read(1)
    if not first:
        raise EOFError("Stream ends where a section count is expected")
    b = first[0]
    if (b & 0x40) == 0:
        return b & 0x3F
    val = b & 0x3F
    for length in range(2, 6):
        nxt = f.read(1)
        if not nxt:
            raise EOFError("Stream ends inside section count")
        nb = nxt[0]
        val |= (nb & 0x7F) << (6 + 7 * (length - 2))
        if (nb & 0x80) == 0:
            return val
    raise ValueError("Count exceeds maximum 5-byte bit6 encoding")

def deobfuscate(stored_bytes, length, magic, unit):
    """
    Deobfuscates character bytes stored in w3strings containers.
    unit = 1 for UTF-8 (v164), unit = 2 for UTF-16LE (v162/163).
    """
    if magic == 0:
        if unit == 2:
            return stored_bytes.decode('utf-16le', errors='replace')
        return stored_bytes.decode('utf-8', errors='replace')

    key = (magic >> 8) & 0xFFFF
    res = bytearray(stored_bytes)
    for i in range(length):
        char_key = ((length + 1) * key) & 0xFFFFFFFF
        if unit == 2:
            res[i * 2] ^= (char_key & 0xFF)
            res[i * 2 + 1] ^= ((char_key >> 8) & 0xFF)
        else:
            res[i] ^= (char_key & 0xFF)
        key = ((key << 1) | (key >> 15)) & 0xFFFF

    if unit == 2:
        return res.decode('utf-16le', errors='replace')
    return res.decode('utf-8', errors='replace')

def clean_html_formatting(text):
    """Converts HTML breaks to newlines and cleans tags for comfortable reading."""
    t = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    t = re.sub(r'</?(?:i|b|font|color)[^>]*>', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def classify_text(act_id, khash, text):
    """
    Categorizes strings into:
    - 'dialogue': Spoken NPC lines, subtitles, player choices
    - 'journal': Quest logs, Dandelion summaries, mission objectives
    - 'book_letter': In-game books, letters, notes, bestiary descriptions
    - 'ui_system': System menus, graphics settings, credits, item stats/names
    """
    t = text.strip()
    if not t:
        return 'ui_system', t
    
    # 1. Credits & Staff
    if any(k in t for k in [
        'CD PROJEKT', '工程師', '工程师', '總監', '总监', '程式設計師', '程序员', '經理', '经理',
        '專员', '专员', '助理', '服務臺', '服务台', '品保', '质保', '遙測', '遥测',
        '遊戲分析', '游戏分析', '資深', '资深', '首席', '副總裁', '副总裁'
    ]) and len(t) < 40 and not any(p in t for p in ['。', '！', '？', '…', '!', '?']):
        return 'ui_system', t
        
    # 2. Hardware / Console / Graphics / Settings / System Popups
    if any(k in t for k in [
        'XBOX', 'PlayStation', 'DualShock', 'DirectX', 'NVIDIA', 'AMD',
        '儲存', '存储', '保存', '存檔', '存档', '登入', '登录', '主選單', '主菜单',
        '光碟', '光盘', '硬碟', '硬盘', '伺服器', '服务器', '設定檔', '配置文件',
        '遊戲主機', '游戏主机', '手稿：', '配方：', '反鋸齒', '反锯齿', '垂直同步',
        '解析度', '分辨率', '全螢幕', '全屏', '顯示模式', '显示模式', '按鍵綁定', '按键绑定',
        '數字鍵盤', '数字键盘', '小鍵盤', '小键盘', '滑鼠靈敏度', '鼠标灵敏度', 'Gamma',
        '未安裝模組', '未安装模组', '按 <<', '按下 <<', '<<GUI_', '[BUTTON',
        '載入中', '加载中', '读取中', '受損', '受损', '覆寫', '覆盖', '刪除', '删除',
        '未儲存', '未存储', '未保存', '連結失敗', '连接失败'
    ]):
        return 'ui_system', t

    # 3. Item names & stats with KeyHash
    if khash is not None:
        if not any(p in t for p in ['。', '！', '？', '…', '：', '”', '“', '!', '?']) and len(t) < 25:
            return 'ui_system', t
        if re.match(r'^[+-]?\d+[%点點數秒]?\s*[\u4e00-\u9fa5]+', t) or any(k in t for k in ['傷害削減', '伤害削减', '護甲增加', '护甲增加', '毒性等級', '毒性等级']):
            return 'ui_system', t

    # 4. Books / Letters / Documents / Bestiary
    has_html = '<br>' in t.lower() or '<i>' in t.lower()
    if has_html and len(t) > 60:
        return 'book_letter', t
    if len(t) > 150:
        if any(w in t for w in ['傳說', '传说', '筆記', '笔记', '信', '敬啟', '敬启', '此致', '祝', '告示', '–', '—', '親愛的', '亲爱的', '老巫嫗', '老巫妪', '怪物', '生物']):
            return 'book_letter', t
        return 'journal', t

    # 5. Quest objectives / Journals
    if any(t.startswith(prefix) for prefix in [
        '利用狩魔獵人的感官能力', '利用猎魔人的感官能力', '打敗', '打败', '殺死', '杀死',
        '前往', '尋找', '寻找', '調查', '调查', '解救', '搜刮', '與', '与', '跟', '和',
        '詢問', '询问', '返回', '摧毀', '摧毁', '探索', '跟隨', '跟随', '保護', '保护',
        '點燃', '点燃', '交談', '交谈', '護送', '护送', '逃離', '逃离'
    ]) and len(t) < 80 and not any(p in t for p in ['？', '！', '?', '!']):
        return 'journal', t

    # 6. Dialogue / Spoken lines
    has_sent_punct = any(p in t for p in ['。', '！', '？', '…', '，', '、', '：', '!', '?', ','])
    if has_sent_punct or len(t) >= 4:
        return 'dialogue', t

    return 'ui_system', t

def decode_w3strings(filepath, output_dir=None):
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_dir = os.path.join(os.path.dirname(filepath), f"{base_name}_extracted")

    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Reading file: {filepath}")
    with open(filepath, "rb") as f:
        f.seek(0, 2)
        file_len = f.tell()
        key2_offset = file_len - 2

        f.seek(0)
        magic_bytes = f.read(4)
        if magic_bytes != b"RTSW":
            print(f"Error: Invalid magic bytes: {magic_bytes}. Expected b'RTSW'.")
            return False

        version, key_head = struct.unpack("<IH", f.read(6))
        count1 = read_section_count(f)
        entries = [struct.unpack("<III", f.read(12)) for _ in range(count1)]

        count2 = read_section_count(f)
        keys = [struct.unpack("<II", f.read(8)) for _ in range(count2)]

        units = read_section_count(f)
        buffer_start = f.tell()

        f.seek(key2_offset)
        key_tail = struct.unpack("<H", f.read(2))[0]
        full_key = (key_head << 16) | key_tail

        lang_info = LANGUAGES.get(full_key, ("unknown", 0x00000000))
        lang_code, magic = lang_info

        unit = 1 if version >= 164 else 2

        print(f"    - Version: {version} ({'UTF-8 Next-Gen' if version >= 164 else 'UTF-16LE Classic'})")
        print(f"    - Language: {lang_code} (Key: 0x{full_key:08X}, Magic: 0x{magic:08X})")
        print(f"    - Total Strings: {len(entries)}")
        print(f"    - Total Key Mappings: {len(keys)}")

        id_to_hash = {kid ^ magic: khash for khash, kid in keys}

        # Decode all strings
        all_records = []
        categories = {
            'dialogue': [],
            'journal': [],
            'book_letter': [],
            'ui_system': []
        }

        print("[*] Decoding and classifying strings...")
        for sid, off, length in entries:
            act_id = sid ^ magic
            khash = id_to_hash.get(act_id)
            f.seek(buffer_start + off * unit)
            raw = f.read(length * unit)
            text = deobfuscate(raw, length, magic, unit)
            cat, clean_t = classify_text(act_id, khash, text)

            all_records.append((act_id, khash, text))
            categories[cat].append((act_id, khash, clean_t))

    # Sort each category by ID (preserves scene / dialogue flow)
    all_records.sort(key=lambda r: r[0])
    for cat in categories:
        categories[cat].sort(key=lambda r: r[0])

    print("\nClassification Results:")
    print(f"    - 剧情对话与台词 (Dialogue): {len(categories['dialogue'])} 条")
    print(f"    - 任务日志与纪实 (Journal):  {len(categories['journal'])} 条")
    print(f"    - 书籍书信与图鉴 (Books):    {len(categories['book_letter'])} 条")
    print(f"    - 界面与系统条目 (UI/System):{len(categories['ui_system'])} 条")

    # 1. Full CSV export (All strings)
    csv_path = os.path.join(output_dir, "00_all_strings.csv")
    print(f"\n[*] Writing full CSV: {csv_path}")
    with open(csv_path, "w", encoding="utf-8-sig") as out:
        out.write("ID,KeyHashHex,Text\n")
        for aid, kh, txt in all_records:
            kh_str = f"0x{kh:08X}" if kh is not None else ""
            escaped = txt.replace('"', '""')
            out.write(f'{aid},{kh_str},"{escaped}"\n')

    # 2. Dialogues file
    dlg_path = os.path.join(output_dir, "01_dialogues.txt")
    print(f"[*] Writing dialogues: {dlg_path}")
    with open(dlg_path, "w", encoding="utf-8") as out:
        out.write(f"# 《巫师3：狂猎》 剧情对话与台词总表 (共 {len(categories['dialogue'])} 条)\n")
        out.write("# 格式: [ID] 对白文本\n# (已按ID排序，同场景/对话树自然相连)\n\n")
        for aid, _, txt in categories['dialogue']:
            out.write(f"[{aid}] {txt}\n")

    # 3. Quest Journal & Narration
    jrn_path = os.path.join(output_dir, "02_quest_journal.txt")
    print(f"[*] Writing journal: {jrn_path}")
    with open(jrn_path, "w", encoding="utf-8") as out:
        out.write(f"# 《巫师3：狂猎》 任务日志、丹德里恩记述与目标总表 (共 {len(categories['journal'])} 条)\n\n")
        for aid, _, txt in categories['journal']:
            cleaned = clean_html_formatting(txt)
            out.write(f"【任务记录 ID: {aid}】\n{cleaned}\n\n{'-'*60}\n\n")

    # 4. Books, Letters, Lore
    book_path = os.path.join(output_dir, "03_books_and_letters.txt")
    print(f"[*] Writing books & lore: {book_path}")
    with open(book_path, "w", encoding="utf-8") as out:
        out.write(f"# 《巫师3：狂猎》 书籍文献、书信手稿与怪物图鉴总表 (共 {len(categories['book_letter'])} 条)\n\n")
        for aid, _, txt in categories['book_letter']:
            cleaned = clean_html_formatting(txt)
            out.write(f"【文献/信件 ID: {aid}】\n{cleaned}\n\n{'='*60}\n\n")

    # 5. Combined Pure Story Text (Reader Edition)
    story_all_path = os.path.join(output_dir, "04_story_compilation.txt")
    print(f"[*] Writing combined story compilation: {story_all_path}")
    with open(story_all_path, "w", encoding="utf-8") as out:
        out.write("====================================================================\n")
        out.write("                  《巫师3：狂猎》 剧情文本全集 (阅读版)               \n")
        out.write("====================================================================\n\n")
        
        out.write("--------------------------------------------------------------------\n")
        out.write("第一部分：世界文献、往来书信与图鉴手稿 (Books & Letters)\n")
        out.write("--------------------------------------------------------------------\n\n")
        for aid, _, txt in categories['book_letter']:
            cleaned = clean_html_formatting(txt)
            out.write(f"【ID: {aid}】\n{cleaned}\n\n")

        out.write("\n--------------------------------------------------------------------\n")
        out.write("第二部分：任务日志、剧情纪实与丹德里恩随笔 (Quest Journals)\n")
        out.write("--------------------------------------------------------------------\n\n")
        for aid, _, txt in categories['journal']:
            cleaned = clean_html_formatting(txt)
            out.write(f"【ID: {aid}】\n{cleaned}\n\n")

        out.write("\n--------------------------------------------------------------------\n")
        out.write("第三部分：人物对话、过场台词与剧情选项 (Dialogues & Subtitles)\n")
        out.write("--------------------------------------------------------------------\n\n")
        for aid, _, txt in categories['dialogue']:
            out.write(f"[{aid}] {txt}\n")

    print(f"\n[+] Extraction successfully completed! All files saved in:\n    {output_dir}\n")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Witcher 3 story texts from .w3strings files.")
    parser.add_argument("input_file", nargs="?", default="zh.w3strings", help="Path to .w3strings file (default: zh.w3strings)")
    parser.add_argument("-o", "--output", default="extracted_texts", help="Output directory path (default: extracted_texts)")
    args = parser.parse_args()

    decode_w3strings(args.input_file, args.output)
